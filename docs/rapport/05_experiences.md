## 5. Expériences et résultats

Chaque chiffre de ce chapitre vient de la sortie du notebook 03 (`notebooks/03_experiences.ipynb`) ou des fichiers de `resultats/`.

### 5.1 Protocole

Pour les stratégies classiques, le tournoi est rejoué sur 30 graines (0 à 29), avec 10 répétitions par paire et 200 manches, pour trois niveaux de bruit : $\varepsilon = 0$, 0,01 et 0,05. Nous gardons pour chaque stratégie le score moyen par manche avec son intervalle de confiance à 95 % entre graines, le rang moyen et la fraction de graines où elle arrive première. Le réplicateur part de parts égales et est rejoué sur les mêmes graines.

Pour les modèles de langage, nous avons quatre configurations : llama3.1 et qwen2.5, avec horizon annoncé ou non. Chacune compte 10 parties de 10 manches contre tit-for-tat, à la température 0,7, avec la graine 1000 + k pour la partie k, les mêmes graines d'une configuration à l'autre. L'unité statistique est la partie : l'intervalle de la coopération moyenne est un bootstrap sur les 10 parties, jamais sur les 100 coups, et les comparaisons entre horizons reposent sur la coopération par partie (test de Mann-Whitney). Les parties ont été jouées sur un GPU T4 gratuit (Google Colab, Ollama 0.40.16), les empreintes des modèles étant consignées avec les résultats. Six parties de llama3.1 avec horizon annoncé ont été rejouées sur CPU en local (Ollama 0.40.11) : leurs trajectoires sont identiques, coup pour coup, à celles du GPU. Enfin, l'agent a reçu cinq questions posées trois fois chacune, dont une hors sujet.

### 5.2 Stratégies classiques

Sans bruit, le rancunier arrive premier dans toutes les graines avec 2,664 points par manche, devant tit-for-tat (2,540) et Pavlov (2,457). Le bruit renverse ce classement. À $\varepsilon = 0{,}05$, toujours trahir (2,369) devance le rancunier (2,359) et arrive premier dans 73 % des graines. À $\varepsilon = 0{,}01$, le rancunier (2,357) et toujours trahir (2,348) se partagent la première place, à 57 % et 43 % des graines : l'écart de score est de l'ordre de l'intervalle de confiance (0,015 pour le rancunier), et nous ne les départageons pas. Tit-for-tat passe du rang 2 sans bruit au rang moyen 4,1 à 5 % de bruit, et sa version généreuse ne fait pas mieux, avec un rang moyen de 5,8 sur sept stratégies. La figure `docs/figures/fig_classement_bruit.png` les résume.

Pour le réplicateur, la population finale est dominée par le rancunier sans bruit (dans 100 % des graines) et par Pavlov à 5 % de bruit (part moyenne 0,999). À 1 % de bruit, le résultat dépend de la graine : le rancunier domine dans 60 % des graines et Pavlov dans 37 %, avec un écart-type d'environ 0,45 sur les parts. Une seule graine aurait donné une réponse nette et trompeuse.

### 5.3 Agents de langage contre tit-for-tat

| Modèle | Horizon annoncé | Coopération (IC95 bootstrap) | Trajectoires distinctes | 1re manche | Dernière manche | Score moyen par manche | Hors format |
|---|---|---|---|---|---|---|---|
| llama3.1 | oui | 63 % (36 à 90 %) | 3 sur 10 | 70 % | 70 % | 2,45 | 0 sur 100 |
| llama3.1 | non | 31 % (16 à 44 %) | 3 sur 10 | 70 % | 60 % | 1,85 | 0 sur 100 |
| qwen2.5 | oui | 68 % (64 à 72 %) | 3 sur 10 | 100 % | 10 % | 2,82 | 0 sur 100 |
| qwen2.5 | non | 83 % (80 à 86 %) | 3 sur 10 | 100 % | 60 % | 2,88 | 0 sur 100 |

Aucune réponse hors format n'est apparue sur les 400 coups : le coup par défaut (coopérer) n'a pas joué. Tous les scores sont inférieurs aux 3 points de tit-for-tat contre lui-même. Le test de Mann-Whitney sur la coopération par partie donne, pour llama3.1, $U = 74{,}5$ et $p = 0{,}057$ (63 % contre 31 %), et pour qwen2.5, $U = 3{,}5$ et $p = 0{,}0003$ (68 % contre 83 %). Il faut lire ce second résultat avec prudence : chaque configuration ne contient que 3 trajectoires distinctes sur 10 parties, parce que les modèles sont presque déterministes à cette température. Les 10 parties ne sont donc pas 10 tirages indépendants, et la valeur $p$ surestime sans doute ce que l'on sait.

Le détail des trajectoires éclaire les moyennes. Avec horizon annoncé, qwen2.5 coopère à la première manche dans 100 % des parties et à la dernière dans 10 % d'entre elles, soit une seule partie. Sans annonce, il coopère pendant neuf manches puis trahit à la dernière dans trois parties sur dix, ce qui lui rapporte 3,2 points par manche. llama3.1 est bimodal : 3 parties sur 10 sont trahies de bout en bout, quel que soit l'horizon, avec un score de 1,4. Avec horizon annoncé, les sept autres sont coopératives avec une seule trahison isolée, à la sixième manche dans six parties (score de 2,9). Sans annonce, six parties basculent dans la trahison à la quatrième manche et n'en sortent qu'à la dernière. La figure `docs/figures/fig_coop_llm.png` trace la coopération par manche, avec la prédiction de l'induction à rebours à zéro.

### 5.4 Écarts à la théorie

L'induction à rebours prédit 0 % de coopération à horizon annoncé. Nous observons 63 % pour llama3.1 et 68 % pour qwen2.5, et le tableau n'autorise aucune lecture qui ramènerait ces valeurs à zéro. La prédiction n'est donc pas vérifiée, ni en moyenne, ni dans la première manche.

Deux nuances limitent la portée de cet écart. D'abord, la prédiction vaut pour deux joueurs qui raisonnent tous deux par induction. Contre tit-for-tat, qui est conditionnel et non rationnel au sens du cours, la meilleure réponse sur dix manches, que nous avons obtenue en parcourant les 1 024 séquences possibles, est de coopérer neuf fois puis de trahir à la dernière, pour 3,2 points par manche. Que qwen2.5 coopère d'abord puis trahisse en fin de partie s'accorde avec cette réponse optimale, mais aussi avec l'idée d'un effondrement partiel de la fin vers le début, conforme en esprit à l'induction, sans trahison dès la première manche. Nos données ne départagent pas ces deux lectures. Ensuite, l'effet de l'annonce de l'horizon n'est pas cohérent d'un modèle à l'autre. qwen2.5 coopère moins quand l'horizon est annoncé (68 % contre 83 %), dans le sens de la théorie, mais cet écart repose sur très peu de trajectoires. llama3.1 coopère davantage avec l'annonce (63 % contre 31 %), dans le sens contraire, et l'écart n'est pas significatif au seuil de 5 %.

Nous ne tirons aucune conclusion d'une partie isolée. En particulier, le fait que llama3.1 trahisse de bout en bout dans 30 % des parties n'établit pas qu'il raisonne par induction : une trahison dès la première manche contre tit-for-tat coûte cher (1,4 point par manche contre 2,9 pour les parties coopératives), et nous n'avons pas de réponses brutes complètes pour savoir comment le modèle justifie ce choix.

### 5.5 L'agent

Sur le GPU, les 30 essais (15 par modèle) sont conformes : les questions 1 à 4 appellent l'outil attendu, avec deux appels de tournoi pour la question 4, et la question 5, hors sujet, n'appelle aucun outil. Les durées moyennes vont de 1 à 15 secondes. Sur CPU, llama3.1 réussit 12 essais exploitables sur 12 et qwen2.5 10 sur 10 (série partielle), en 19 à 196 secondes en moyenne. Les trois essais de la question 4 de llama3.1 sur CPU sont inexploitables à cause d'un bug de notre contrôle, expliqué au chapitre 6, et ont été rejoués sur le GPU. llama3.1 écrit parfois les nombres des arguments sous forme de chaînes ; le schéma de l'outil les convertit et le calcul est juste.

### 5.6 Limites

Nos résultats sur les modèles de langage valent pour un seul adversaire (tit-for-tat), des parties de 10 manches, deux modèles et un seul prompt. Chaque configuration ne compte que 3 trajectoires distinctes, ce qui donne une puissance statistique faible : un écart non significatif ne prouve pas l'absence d'effet, et un écart significatif repose sur peu d'information indépendante. Ni la température ni le prompt n'ont varié. Les réponses brutes complètes des parties jouées sur Colab n'ont pas été rapatriées : seules la première et la dernière réponse de la partie 1 le sont, alors que celles des six parties locales le sont. Pour l'agent, trois essais par question et cinq questions ne permettent que de dire que les appels sont corrects dans ces cas, pas qu'ils le sont en général, et les arguments des essais Colab n'ont pas été conservés. Pour les stratégies classiques, le classement dépend de l'ensemble des sept stratégies que nous avons choisi.
