# Conventions du groupe 6

Ces conventions s'appliquent à tout le code, aux tests, aux expériences et au rapport. Elles répondent aux erreurs fréquentes listées dans le guide du projet 6 (auto-jeu oublié, bruit sur un seul joueur, totaux sur des horizons différents, conclusion tirée d'une seule partie).

## Jeu de base

Les coups sont `C` (coopérer) et `D` (trahir). Les gains par manche sont (C, C) = (3, 3), (C, D) = (0, 5), (D, C) = (5, 0) et (D, D) = (1, 1), soit T = 5, R = 3, P = 1, S = 0. La condition du dilemme, T > R > P > S et 2R > T + S, est vérifiée par `est_un_dilemme()` : 6 > 5.

## Stratégies

Une stratégie est une fonction `(mon_historique, historique_adverse, rng) -> 'C' ou 'D'`. Un joueur LLM suit la même signature, ce qui permet de réutiliser `match` sans le modifier. Les six stratégies du guide portent les noms `toujours_C`, `toujours_D`, `TFT`, `rancunier`, `Pavlov` et `aleatoire`. Le TFT généreux (pardon avec une probabilité fixée, 1/3 par défaut) est une stratégie supplémentaire, nommée `TFT_genereux`, hors du dictionnaire `STRATEGIES` du guide. Pavlov coopère au premier coup, puis coopère si les deux joueurs ont joué la même chose au tour précédent.

## Bruit

Le bruit ε inverse chaque coup avec la probabilité ε, indépendamment pour chaque joueur et chaque manche. Les historiques que voient les stratégies contiennent les coups exécutés, c'est-à-dire après bruit. Les valeurs étudiées sont ε ∈ {0 ; 0,01 ; 0,05}.

## Tournoi

Le tournoi oppose toutes les paires, y compris une stratégie contre elle-même (auto-jeu). Pour l'auto-jeu, le score est la moyenne des deux côtés de la rencontre. `M[i][j]` est le score moyen par manche de la stratégie i contre la stratégie j. Le classement trie les stratégies par moyenne de leur ligne de `M`, adversaire identique compris, avec un poids égal pour chaque adversaire. L'horizon est de 200 manches. La graine de référence est 0 ; `repetitions` permet de moyenner plusieurs rencontres par paire.

## Scores

Tous les scores sont des gains moyens par manche, jamais des totaux. C'est la seule façon de comparer un LLM jouant 10 manches à une stratégie jouant 200.

## Horizon indéterminé

Une partie à arrêt aléatoire continue après chaque manche avec la probabilité δ ; sa longueur suit une loi géométrique, d'espérance 1 / (1 − δ). Le rancunier soutient la coopération si δ ≥ (T − R) / (T − P) = 1/2. Pour TFT, deux déviations sont testées : trahir toujours (même seuil, 1/2) et alterner trahir et coopérer, qui exige δ ≥ (T − R) / (R − S) = 2/3. Le seuil de TFT retenu est le plus grand des deux.

## Agents LLM

La chaîne suit le TP6 : `prompt | modèle | parseur`. Le modèle doit répondre par une ligne `CHOIX : COOPERER` ou `CHOIX : TRAHIR`. Toute réponse sans cette ligne reçoit un coup par défaut et est comptée à part, dans un compteur de valeurs par défaut rapporté avec les résultats. L'horizon (annoncé ou non) est une variable d'expérience. Au moins 10 parties de 10 manches par configuration ; aucune conclusion sur une seule partie.

## Honnêteté expérimentale

Une sortie du faux modèle porte l'étiquette `scripté`, dans la sortie elle-même. Elle prouve que la mécanique fonctionne, jamais la qualité d'un LLM. Les résultats d'un vrai modèle indiquent le modèle, sa version, la graine, le nombre de parties et le nombre de réponses hors format.

## Sécurité

Aucun `eval()` ni `exec()` sur un texte produit par un LLM. Les outils de l'agent reçoivent des données (noms de stratégies connus, nombres bornés), jamais du code, et plafonnent les paramètres coûteux. Ollama n'écoute que sur 127.0.0.1.

## Conventions communes avec les autres groupes

Avec le groupe 1 : A est la matrice des gains du joueur 1 (lignes), B celle du joueur 2 (colonnes), indices à partir de 0. Avec le groupe 2 : chaîne `prompt | modèle | parseur` du TP6, format `CHOIX : ...`, comptage des valeurs par défaut. Chaque groupe code sa propre version.

## Git

Un commit au moins par semaine et par membre, au format `[Prénom] verbe + objet (id étape)`, par exemple `[Jihane] Tests du tournoi et du réplicateur (S3-06)`. Un membre ne commite jamais sous le nom d'un autre.
