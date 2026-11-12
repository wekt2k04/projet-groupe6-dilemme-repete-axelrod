## 6. Tests et qualité

### 6.1 Ce que la suite contient

La suite pytest compte 74 tests, tous verts, et s'exécute en quelques secondes avec la commande `python -m pytest` lancée depuis la racine du dépôt. Elle se répartit en cinq fichiers : 25 tests pour les fonctions pures de `jeux.py`, 16 pour les outils et la boucle de l'agent hors ligne, 16 pour le joueur LLM, 6 pour les contrôles automatiques des essais de l'agent et 11 pour le module d'expériences. Les trois premiers fichiers sont décrits aux chapitres 3 et 4 ; nous développons ici les deux derniers.

Les 11 tests du module d'expériences vérifient les briques statistiques sur des valeurs connues : l'intervalle de Wilson, la moyenne et son intervalle, le résumé d'une configuration (coopération, trajectoires distinctes, défauts comptés à part), la comparaison des horizons, la prédiction de l'induction à rebours, le chargement des fichiers de parties, et les protocoles multi-graines du tournoi et du réplicateur. L'un vérifie que le bootstrap porte sur les parties et non sur les coups, un autre que des trajectoires identiques ne sont comptées qu'une fois.

### 6.2 Des tests sans modèle, étiquetés comme tels

Aucun test ne dépend d'un modèle réel. Les tests de l'agent et du joueur utilisent un faux modèle qui rejoue des réponses fixées et dont chaque sortie porte l'étiquette `[scripté]`. Ils prouvent que la mécanique fonctionne (outils acceptés, erreurs lisibles, appels enchaînés, réponse sans ligne `CHOIX` comptée comme défaut, texte ressemblant à du code jamais exécuté) et ne prouvent rien sur la qualité d'un vrai modèle. Cette qualité se mesure autrement, par les essais répétés du chapitre 5, avec un contrôle automatique de l'outil appelé et de ses arguments.

Les tests qui font intervenir le hasard utilisent une graine fixe et une tolérance large, de sorte qu'ils donnent le même verdict à chaque exécution tout en restant robustes à un changement mineur du code. Une recherche dans les fichiers Python du dépôt ne trouve aucun appel à `eval` ni à `exec`, et la règle d'écoute d'Ollama sur `127.0.0.1` est inscrite dans les conventions et dans le README.

### 6.3 Un incident et ce qu'il a changé

Lors des essais de l'agent sur CPU, les trois essais de la question 4 de llama3.1 sont sortis en erreur. La cause n'était pas le modèle mais notre propre contrôle, qui appliquait `round()` à l'argument `bruit` : le modèle avait écrit ce nombre sous forme de chaîne, et l'arrondi d'une chaîne lève une exception. Nous avons failli lire ce résultat comme un échec de l'agent. Nous avons corrigé le contrôle, qui convertit maintenant les valeurs avant de les comparer, puis nous avons ajouté un test de non-régression, où une chaîne `"0.01"` est acceptée pour le bruit, et rejoué les essais sur le GPU, où les 30 essais sont conformes. Les trois essais perdus restent dans le fichier de résultats sous la rubrique « non exploitables », séparés des essais conformes et des essais non conformes. L'enseignement est que le dispositif de mesure doit lui-même être testé, et que les essais perdus par un bug se comptent à part au lieu de s'effacer.

### 6.4 Reproductibilité et traçabilité

Chaque fichier de résultats d'un vrai modèle consigne le modèle et son empreinte, la version du serveur Ollama, la température, la graine de base et le matériel. Les graines des parties sont les mêmes d'une configuration à l'autre. Pour vérifier que le matériel ne change pas les résultats, nous avons rejoué six parties de llama3.1 avec horizon annoncé sur CPU : les six trajectoires sont identiques à celles du GPU, coup pour coup. Cette comparaison ne porte que sur cette configuration.

Les figures et les tableaux du chapitre 5 viennent du notebook 03, exécuté sur ces fichiers ; chaque chiffre du rapport est repris d'une sortie réelle. Ce qui n'a pas été vérifié est dit : les réponses brutes complètes des parties du GPU n'ont pas été conservées, et les tests ne couvrent pas la qualité des prompts ni celle des modèles.
