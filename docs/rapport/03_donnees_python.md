## 3. Conventions, fonctions Python et tests

Le module `src/jeux.py` regroupe des fonctions pures, sans LangChain ni lecture de fichier. Ses conventions sont écrites dans `CONVENTIONS.md` et répondent aux erreurs fréquentes signalées par le guide : auto-jeu oublié, bruit sur un seul joueur, totaux comparés sur des horizons différents, conclusion tirée d'une seule partie.

### 3.1 Conventions de modélisation

Les coups sont `'C'` (coopérer) et `'D'` (trahir), et les gains par manche valent $T=5$, $R=3$, $P=1$, $S=0$. Une stratégie est une fonction `(mon_historique, historique_adverse, rng)` qui renvoie un coup. Un joueur piloté par un modèle de langage a la même signature, ce qui permet de réutiliser `match` sans le modifier. Le dictionnaire `STRATEGIES` contient les six stratégies du guide ; le TFT généreux, qui pardonne une trahison avec la probabilité 1/3, est placé à part dans `STRATEGIES_ETENDUES`.

Le bruit inverse chaque coup avec la probabilité $\varepsilon$, indépendamment pour chacun des deux joueurs et à chaque manche, ce qui représente deux tirages par manche. Les historiques transmis aux stratégies contiennent les coups exécutés, c'est-à-dire après inversion : TFT copie donc ce que l'adversaire a réellement joué, et non ce qu'il voulait jouer.

Le tournoi oppose toutes les paires, y compris une stratégie à elle-même. Pour cette auto-rencontre, le score retenu est la moyenne des deux côtés, qui diffèrent dès que la stratégie contient du hasard. `M[i][j]` est le score moyen par manche de la stratégie $i$ contre la stratégie $j$, et le classement trie les stratégies par la moyenne de leur ligne de `M`, avec un poids égal pour chaque adversaire. Tous les scores sont des gains moyens par manche, jamais des totaux, afin de comparer une partie de 10 manches jouée par un modèle de langage et une partie de 200 manches jouée par une stratégie. Enfin, `tournoi` crée un seul générateur `random.Random(seed)` pour toutes les rencontres, dans un ordre fixe : une graine donnée reproduit exactement la matrice, et `repetitions` moyenne plusieurs rencontres par paire.

### 3.2 Les fonctions et leur contrat

`est_un_dilemme(t, r, p, s)` renvoie un booléen qui vérifie $T>R>P>S$ et $2R>T+S$. `strategie_par_nom(nom)` renvoie la fonction d'une stratégie connue et lève `ValueError` pour tout autre nom. `match_detail(s1, s2, manches, bruit, rng)` joue la rencontre et renvoie les deux scores moyens par manche et les deux historiques de coups exécutés ; `match` n'en garde que les scores. Sans générateur fourni, `match_detail` utilise `random.Random(0)`.

`tournoi(strategies, manches, bruit, seed, repetitions)` renvoie le triplet formé des noms, de la matrice `M` (tableau NumPy $n\times n$) et du classement, liste de couples (nom, score moyen) triée par ordre décroissant. Seules les paires $i\le j$ sont jouées, une rencontre remplissant `M[i][j]` et `M[j][i]`. `replicateur(scores, x0, generations)` renvoie un tableau de `generations + 1` lignes, positives et de somme 1, après normalisation de `x0`. `seuil_rancunier` et `seuil_tft` calculent $(T-R)/(T-P)$ et le plus grand de $(T-R)/(T-P)$ et $(T-R)/(R-S)$. `longueur_arret_aleatoire(delta, rng)` tire la longueur d'une partie qui continue avec la probabilité $\delta$, au moins égale à 1. Enfin `ecart_deviation_rancunier(delta, parties, seed)` renvoie la moyenne et l'erreur standard de l'écart « gain en trahissant moins gain en coopérant » face à un rancunier, que `ecart_theorique_rancunier(delta)` compare à sa valeur exacte.

### 3.3 Validation des entrées

Chaque fonction refuse les entrées absurdes en levant `ValueError`, et la plupart de ces refus sont couverts par un test. `match_detail` exige `manches` au moins égal à 1 et `bruit` dans $[0,1]$. `tournoi` exige `repetitions` au moins égal à 1. `tft_genereux` exige un pardon dans $[0,1]$. `longueur_arret_aleatoire` exige $\delta\in[0,1[$, puisque $\delta=1$ ne s'arrêterait jamais. `replicateur` exige une matrice carrée, un `x0` de la bonne longueur, positif et non nul, des scores positifs ou nuls, et une moyenne de population strictement positive à chaque génération. Les outils de l'agent attrapent ces `ValueError` et les renvoient au modèle sous forme de message, comme le décrit le chapitre suivant.

### 3.4 Valeurs de référence calculées à la main

Plusieurs scores sans bruit sur 200 manches ont été calculés à la main et inscrits dans les tests.

| Rencontre | Scores moyens attendus | Calcul |
|---|---|---|
| TFT contre TFT | (3 ; 3) | $(C,C)$ à chaque manche |
| toujours_D contre toujours_C | (5 ; 0) | $(D,C)$ à chaque manche |
| TFT contre toujours_D | (0,995 ; 1,02) | TFT perd la première manche : $199/200$ pour lui, $(5+199)/200$ pour l'autre |
| rancunier contre toujours_D | (0,995 ; 1,02) | même calcul |
| Pavlov contre toujours_D | (0,5 ; 3,0) | Pavlov joue $C,D,C,D,\dots$ : $0,1,0,1,\dots$ contre $5,1,5,1,\dots$ |

Pavlov alterne parce qu'après $(C,D)$ les deux derniers coups diffèrent, donc il joue $D$ ; après $(D,D)$ ils sont identiques, donc il rejoue $C$, et ainsi de suite. Les tests ajoutent quelques rencontres qui donnent (3 ; 3), comme rancunier contre TFT, et toujours_D contre elle-même, qui donne (1 ; 1). La matrice du notebook 01 retrouve les mêmes valeurs, par exemple 0,995 et 1,020 pour TFT contre toujours_D, et 0,500 et 3,000 pour Pavlov contre toujours_D.

### 3.5 Vérification du seuil 1/2 par arrêt aléatoire

Pour confronter la formule au code, nous simulons des parties dont la longueur $L$ est géométrique. Face à un rancunier, coopérer rapporte $R\,L$ et trahir dès la première manche rapporte $T+P\,(L-1)$, d'où un écart $T-P+(P-R)\,L$ dont l'espérance est $T-P+(P-R)/(1-\delta)=4-2/(1-\delta)$, nulle exactement pour $\delta=1/2$. Le notebook 01 estime cet écart sur 60 000 parties, avec la graine 5.

| $\delta$ | Écart simulé (± erreur standard) | Écart théorique |
|---|---|---|
| 0,4 | +0,655 ± 0,009 | +0,667 |
| 0,5 | -0,016 ± 0,012 | 0 |
| 0,6 | -0,997 ± 0,016 | -1,000 |

L'écart change de signe autour de $1/2$ : sous ce seuil, trahir rapporte en moyenne davantage, au-dessus il rapporte moins, et à $\delta=1/2$ l'écart est indiscernable de zéro (environ 1,3 erreur standard). Les erreurs standard observées coïncident avec la valeur exacte $2\sqrt\delta/\big((1-\delta)\sqrt{60000}\big)$, soit 0,0086, 0,0115 et 0,0158 : l'estimation d'incertitude du code est cohérente avec la loi géométrique.

### 3.6 Logique des tests

La suite compte 74 tests répartis en cinq fichiers (25 pour `test_jeux.py`, 16 pour `test_hors_ligne.py`, 16 pour `test_joueur_llm.py`, 6 pour `test_controles_agent.py`, 11 pour `test_experiences.py`) et ils réussissent tous. Les 25 tests de `test_jeux.py` suivent l'ordre des conventions. Ils vérifient les valeurs du guide et celles calculées à la main, puis le bruit : une fréquence de trahison proche de 0,2 sur 4 000 manches pour chacun des deux joueurs (tolérance 0,03), le cas limite $\varepsilon=1$ qui inverse tous les coups, et la copie du coup exécuté par TFT. Viennent ensuite le tournoi (reproductibilité, auto-jeu égal à la moyenne des deux côtés, scores par manche identiques sur 50 et 200 manches sans bruit), les invariants du réplicateur (parts positives, somme égale à 1, part nulle conservée, stratégie dominante dont la part dépasse 0,99), les refus d'entrées invalides et le seuil par arrêt aléatoire. Les tests aléatoires utilisent une graine fixe et une tolérance large (quatre erreurs standard pour le seuil), de sorte qu'ils sont déterministes et peu fragiles. Ils se lancent avec `python -m pytest` depuis la racine du dépôt. Les trois autres fichiers, consacrés à l'agent et au joueur LLM, sont présentés au chapitre suivant.
