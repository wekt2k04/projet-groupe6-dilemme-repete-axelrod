# Comprendre le projet 6

Ce document est écrit pour que chaque membre puisse expliquer tout le projet, ligne de code comprise. Il suppose lu `MATIERE.md` pour la théorie générale. Les chiffres ci-dessous viennent de sorties exécutées (graine 0 sauf mention contraire) ; l'étiquette « à confirmer » signale un résultat qui dépend d'un échantillon trop petit pour conclure.

## 1. Ce que le projet démontre

Le dilemme du prisonnier à une manche a un seul équilibre de Nash, (D, D), qui rapporte 1 à chacun alors que (C, C) rapporte 3. Quand on répète le jeu, la menace de représailles peut rendre la coopération stable. Le projet répond à trois questions : quelle stratégie gagne un tournoi, que devient ce classement quand les joueurs se trompent (le bruit ε), et comment se comporte un LLM local qui joue avec mémoire des coups. Le lien avec le cours est un paradoxe : à horizon fini et connu, l'induction à rebours prédit la trahison dès la première manche (paradoxe du mille-pattes), alors que les stratégies conditionnelles coopèrent en pratique.

## 2. Les formules et leurs valeurs

Les gains sont T = 5, R = 3, P = 1, S = 0. Le jeu est un dilemme parce que T > R > P > S et que 2R = 6 > T + S = 5 : l'alternance trahir / coopérer ne bat pas la coopération mutuelle.

Pour un horizon indéterminé, la partie continue après chaque manche avec la probabilité δ. Un rancunier qui coopère obtient R/(1−δ). S'il trahit une fois, il obtient T puis P à chaque manche suivante : T + δP/(1−δ). La coopération tient si δ ≥ (T−R)/(T−P) = 2/4 = 1/2. Contre TFT, la déviation « trahir toujours » donne le même seuil. L'alternance trahir / coopérer rapporte T, S, T, S, ... soit (T + δS)/(1−δ²), et la coopération tient si δ ≥ (T−R)/(R−S) = 2/3. Le seuil de TFT est donc 2/3.

La dynamique du réplicateur met à jour les parts x_i(t+1) = x_i(t) f_i / f̄, avec f = Mx le score moyen de i contre la population et f̄ = xᵀf la moyenne. Les parts restent positives et de somme 1 parce que la somme des x_i f_i est exactement f̄.

## 3. Le code, fonction par fonction

`match_detail(s1, s2, manches, bruit, rng)` joue une rencontre et renvoie les deux scores moyens et les deux historiques ; `match` n'en garde que les scores. À chaque manche, chaque stratégie voit les historiques des coups exécutés, puis le bruit inverse indépendamment le coup de chaque joueur. `tournoi` remplit `M` pour toutes les paires i ≤ j, en tirant les rencontres avec un seul générateur initialisé par `seed`. Pour i = j (auto-jeu), `M[i][i]` est la moyenne des deux côtés. `replicateur(scores, x0, generations)` applique la formule ci-dessus et renvoie la trajectoire. `seuil_rancunier` et `seuil_tft` calculent les deux seuils. `ecart_deviation_rancunier(delta)` estime par Monte-Carlo l'avantage de trahir contre un rancunier avec arrêt aléatoire, et `ecart_theorique_rancunier(delta)` en donne la valeur exacte T − P + (P − R)/(1 − δ).

## 4. Valeurs de référence des tests

Sans bruit, sur 200 manches : TFT contre TFT donne (3 ; 3) ; toujours trahir contre toujours coopérer donne (5 ; 0) ; TFT contre toujours trahir donne (0,995 ; 1,02) car TFT ne perd que la première manche, soit 199 manches à 1 point et une manche à 0 ; Pavlov contre toujours trahir alterne C, D, C, D, d'où (0,5 ; 3,0). Le seuil du rancunier est 0,5 et celui de TFT 2/3. Les parts du réplicateur sont positives et somment à 1 à chaque génération. Pour le seuil par arrêt aléatoire, avec 60 000 parties : δ = 0,4 donne un écart de +0,655 (erreur standard 0,009 ; théorie +0,667) ; δ = 0,5 donne −0,016 (erreur 0,012 ; théorie 0) ; δ = 0,6 donne −0,997 (erreur 0,016 ; théorie −1). Dévier rapporte donc sous 1/2, coopérer rapporte au-delà, et l'indifférence est à 1/2.

## 5. Premiers résultats du tournoi

Classements par score moyen par manche, 20 répétitions par paire, graine 0, 200 manches (premier essai, à confirmer avec plus de graines et des intervalles de confiance en S5).

| ε | 1er | 2e | 3e | 4e | 5e | 6e |
|---|---|---|---|---|---|---|
| 0 | rancunier 2,663 | TFT 2,541 | Pavlov 2,466 | toujours_D 2,340 | toujours_C 2,251 | aleatoire 1,966 |
| 0,01 | toujours_D 2,350 | rancunier 2,303 | Pavlov 2,215 | TFT 2,108 | aleatoire 1,968 | toujours_C 1,785 |
| 0,05 | toujours_D 2,368 | rancunier 2,357 | Pavlov 2,102 | TFT 2,033 | aleatoire 1,983 | toujours_C 1,623 |

Sans bruit, la coopération conditionnelle gagne. Avec du bruit, une erreur déclenche des représailles en chaîne chez TFT et le rancunier, et la domination de TFT ne résiste pas dans ce premier essai. L'écart entre toujours_D et le rancunier à ε = 0,05 (0,011) est probablement dans le bruit d'échantillonnage : il ne permet pas de les départager. Le TFT généreux (pardon 1/3), ajouté comme septième stratégie, termine 4e à ε = 0 (2,524) et 6e à ε = 0,05 (2,099) dans ce premier essai, ce qui ne montre pas d'avantage net ; à confirmer.

Depuis des parts égales, le réplicateur à 200 générations donne, sans bruit, rancunier 0,342, TFT 0,281, Pavlov 0,230, toujours_C 0,146, et 0 pour toujours_D et aleatoire. Avec ε = 0,01, le rancunier atteint 0,929 et Pavlov 0,071. Avec ε = 0,05, Pavlov atteint 1,0 (valeur arrondie). L'ordre dépend de la matrice estimée avec une graine ; il sera recalculé sur plusieurs graines.

## 6. Les agents LLM

Un joueur LLM est une fonction de même signature qu'une stratégie : elle reçoit l'historique, construit un prompt, appelle le modèle et lit la ligne `CHOIX : COOPERER` ou `CHOIX : TRAHIR`. Une réponse sans cette ligne reçoit un coup par défaut et est comptée à part. On fait varier l'horizon annoncé ou non et le modèle (llama3.1 et qwen2.5), avec au moins 10 parties de 10 manches par configuration. On compare à TFT en fréquence de coopération par manche et en score moyen par manche, jamais en total. Un faux modèle scripté sert à tester la mécanique ; ses sorties sont étiquetées « scripté » et ne disent rien sur la qualité d'un LLM.

## 7. Dix questions probables en séance

1. Pourquoi (D, D) est-il l'unique équilibre de Nash du jeu à une manche ? Parce que trahir domine strictement coopérer : 5 > 3 et 1 > 0.
2. Pourquoi 2R > T + S ? Pour que l'alternance (T, S) ne rapporte pas plus que la coopération mutuelle ; ici 6 > 5.
3. Que prédit l'induction à rebours sur 200 manches ? Trahir à chaque manche, car la dernière manche est un dilemme à une manche, puis l'avant-dernière devient sans enjeu, et ainsi de suite.
4. Pourquoi les stratégies conditionnelles coopèrent-elles quand même ? Les joueurs réels ne sont pas parfaitement rationnels ou ne connaissent pas l'horizon ; avec un horizon indéterminé, la menace de représailles soutient la coopération dès δ ≥ 1/2.
5. D'où vient le seuil 1/2 ? De R/(1−δ) ≥ T + δP/(1−δ), soit δ ≥ (T−R)/(T−P).
6. Pourquoi 2/3 pour TFT ? À cause de la déviation alternée T, S, T, S, qui impose δ ≥ (T−R)/(R−S).
7. Que fait le bruit ? Il inverse chaque coup avec la probabilité ε, pour les deux joueurs ; les stratégies voient les coups exécutés.
8. Comment traite-t-on l'auto-jeu ? Chaque stratégie joue contre elle-même, et le score est la moyenne des deux côtés ; c'est une convention écrite.
9. Pourquoi des scores moyens par manche ? Pour comparer des parties de 10 manches (LLM) et de 200 manches (stratégies).
10. Que conclure d'une seule partie LLM ? Rien : il faut au moins 10 parties par configuration, avec le taux de réponses hors format rapporté.
