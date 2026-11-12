## 4. L'agent LangChain et les joueurs LLM

### 4.1 Origine du code et construction de l'agent

Le guide décrit un agent du cours, `agent_tj_sma.py`, doté de dix outils. Ce code ne figure pas dans nos supports : nous avons reconstruit l'agent d'après les conventions du guide (types annotés, docstring explicite, sortie JSON, paramètres plafonnés). Nous avons gardé le nom du fichier du cours et l'adapterons si nous recevons l'original. `construire_agent` appelle `create_agent(modele, OUTILS, system_prompt=SYSTEM_PROMPT)` de LangChain (versions installées : langchain 1.5.0, langchain-core 1.8.0, langchain-ollama 1.1.0). Sans modèle fourni, il crée un `ChatOllama` de température 0 qui s'adresse à `http://127.0.0.1:11434`, le nom du modèle venant de la variable `OLLAMA_MODEL` (`llama3.1` par défaut).

Avec la version 1.5, `create_agent` n'a plus de paramètre `verbose`, contrairement à l'ancien exécuteur d'agents. Notre fonction `interroger(agent, question, verbose=True)` reconstitue donc la trace à partir des messages échangés : elle affiche chaque appel d'outil avec ses arguments, le début du résultat (300 caractères) et chaque réponse, puis renvoie tous les messages. Ce paramètre `verbose` est le nôtre.

### 4.2 Les trois outils

| Outil | Arguments (valeur par défaut) | Plafonds |
|---|---|---|
| `tournoi_axelrod` | strategies, manches (200), bruit (0), seed (0), repetitions (1) | 1000 manches, 20 répétitions, 7 stratégies |
| `replicateur` | strategies, generations (200), manches (200), bruit (0), seed (0), repetitions (5) | 2000 générations, 1000 manches, 20 répétitions |
| `seuils_actualisation` | t (5), r (3), p (1), s (0) | aucun |

`tournoi_axelrod` joue toutes les paires comme `jeux.tournoi`, auto-jeu compris, et renvoie une chaîne JSON contenant les paramètres effectifs, les noms, la matrice, le classement et les avertissements ; une liste de stratégies vide désigne les six du guide. `replicateur` estime d'abord la matrice par un tournoi, puis fait évoluer des parts égales ; il renvoie les parts finales, jusqu'à onze points de la trajectoire et la somme des parts. `seuils_actualisation` renvoie le test de dilemme, les gains et les deux seuils (0,5 et 0,6667 par défaut) ; si les gains ne forment pas un dilemme, avec $R=2$ par exemple, il le dit sans calculer de seuil. Le modèle ne lit ni le code ni les tests : il lit le nom de l'outil, sa docstring (de 469 à 863 caractères) et les types des arguments.

### 4.3 Deux niveaux de validation

Le premier niveau est le schéma : les types annotés sont vérifiés avant l'exécution, et une chaîne à la place d'une liste de stratégies, ou `manches="beaucoup"`, lèvent une `ValidationError`. Le schéma convertit en revanche `"200"` en 200, tolérance que reprennent nos contrôles. Le second niveau est dans l'outil : `_preparer` vérifie que les stratégies forment une liste sans doublon de noms connus, et que le bruit est dans $[0,1]$. Toute violation lève `ValueError`, que l'outil attrape et renvoie sous la forme `{"erreur": message}`, si bien que l'agent peut lire l'erreur et l'expliquer.

Les paramètres coûteux sont ramenés dans l'intervalle autorisé, avec un avertissement dans la sortie. Le notebook 02 montre un appel avec $10^9$ manches et $10^6$ répétitions qui devient 1000 manches et 20 répétitions, avec les avertissements « manches ramené de 1000000000 à 1000 (plafond 1000) » et « repetitions ramené de 1000000 à 20 (plafond 20) ». Avec sept stratégies, soit 28 paires, un appel joue au plus 560 000 manches.

### 4.4 Sécurité

Aucun `eval` ni `exec` n'apparaît dans les fichiers Python du dépôt, et aucun texte produit par un modèle n'est exécuté. Les outils reçoivent des données : des nombres bornés et des noms cherchés dans une liste fermée, le dictionnaire `STRATEGIES_ETENDUES`. Le nom `__import__('os').system('echo pirate')`, soumis comme stratégie, est traité comme n'importe quel nom inconnu : il produit une erreur et rien n'est exécuté, ce que montrent un test et le notebook 02. Enfin, Ollama n'écoute que sur `127.0.0.1`, réglage par défaut que nous ne changeons jamais en `0.0.0.0`, car un serveur ouvert au réseau répondrait à toute machine qui l'atteint.

### 4.5 Le prompt système

Le prompt système tient en quatre règles : pour tout résultat chiffré sur un tournoi, une population ou un seuil, appeler l'outil correspondant et ne jamais citer un chiffre de mémoire ; écrire les noms de stratégies exactement comme dans la liste fermée ; donner des gains moyens par manche en indiquant manches, bruit et graine ; signaler toute erreur ou tout avertissement d'un outil. Un test vérifie seulement que les phrases « appelle l'outil » et « jamais un chiffre de mémoire » figurent dans le texte : il protège contre une suppression accidentelle, non contre une désobéissance du modèle. Pour mesurer cette obéissance, `controles_agent.py` fixe pour cinq questions l'outil et les arguments attendus, la dernière question, hors sujet, n'exigeant aucun outil.

### 4.6 Le faux modèle « scripté »

`ModeleScripte` est un faux modèle de chat qui rejoue, dans l'ordre, une liste de réponses fixée dans le test : des demandes d'appel d'outil (`appel_outil`), puis une réponse finale (`reponse_finale`). Sa méthode `bind_tools` renvoie le modèle lui-même, ce qui permet à `create_agent` de lui attacher les outils sans fournisseur réel. Chaque texte qu'il produit commence par l'étiquette `[scripté]`, que les tests vérifient.

Il prouve que la mécanique fonctionne : les outils sont acceptés par `create_agent`, un appel valide exécute l'outil dont le JSON revient dans la conversation, une erreur d'outil revient sous forme lisible, deux outils s'enchaînent, puis la réponse finale termine la boucle. Dans le notebook 02, la boucle échange 6 messages et appelle `seuils_actualisation` puis `tournoi_axelrod`, dont la matrice sur 40 manches, $[[3{,}0 ; 0{,}975] ; [1{,}1 ; 1{,}0]]$, correspond au calcul à la main ($39/40$ et $44/40$). En revanche, puisque le script fixe les choix avant toute question, il ne dit rien sur la capacité d'un vrai modèle à choisir l'outil, écrire les arguments, lire le résultat ou suivre le prompt. Cela se mesure avec Ollama, par plusieurs essais par question.

### 4.7 Le joueur LLM

Un `JoueurLLM` suit la signature d'une stratégie et se branche donc dans `match_detail`. Sa chaîne est celle du TP6, `prompt | modèle | parseur`. Le message système donne les quatre gains, demande de maximiser le total de points et précise si l'horizon est annoncé (« La partie compte exactement 10 manches ») ou non, car l'horizon est une variable de nos expériences. Le message humain donne l'historique des coups exécutés, le numéro de la manche et l'instruction de répondre par une ligne au format exact `CHOIX : COOPERER` ou `CHOIX : TRAHIR`.

La réponse est lue par l'expression régulière `CHOIX\s*:\s*(COOP[ÉE]RER|TRAHIR)`, insensible à la casse. Si plusieurs lignes correspondent, la dernière fait foi, ce qui traite un modèle qui raisonne puis conclut. Une réponse sans ligne valide reçoit le coup par défaut, coopérer, et incrémente le compteur `defauts` ; la liste `reponses` garde pour chaque manche le texte brut, le coup joué et un indicateur de valeur par défaut. Nous avons choisi de coopérer parce que l'issue théorique est la trahison : un défaut « trahir » ferait passer une panne de format pour une conduite rationnelle et pousserait les mesures vers la prédiction à vérifier. Le défaut « coopérer » biaise en sens inverse, ce que nous assumons à condition de le rendre visible, d'où le nombre de réponses hors format rapporté avec chaque résultat. Enfin le joueur n'utilise pas le générateur `rng` : la variabilité vient du modèle et la graine ne la contrôle pas, d'où la répétition des parties (au moins 10 parties de 10 manches par configuration).
