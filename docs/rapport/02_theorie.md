## 2. Cadre théorique

Ce chapitre fixe le modèle et les résultats du cours que notre code doit retrouver. Les valeurs numériques viennent des notebooks exécutés du dépôt (graine 0) ou de calculs relancés avec les mêmes fonctions.

### 2.1 Le jeu à une manche

Deux joueurs choisissent en même temps de coopérer ($C$) ou de trahir ($D$). Chaque case du tableau donne le gain du joueur 1 puis celui du joueur 2, avec $T=5$, $R=3$, $P=1$ et $S=0$.

| | $C$ | $D$ |
|---|---|---|
| $C$ | $(R,R)=(3,3)$ | $(S,T)=(0,5)$ |
| $D$ | $(T,S)=(5,0)$ | $(P,P)=(1,1)$ |

Ce jeu est un dilemme du prisonnier si
$$T>R>P>S \qquad\text{et}\qquad 2R>T+S ,$$
ce que vérifient $5>3>1>0$ et $6>5$. La première chaîne classe la tentation ($T$), la récompense ($R$), la punition ($P$) et le gain du naïf trompé ($S$). La seconde condition concerne la répétition. Si les deux joueurs alternaient les rôles, l'un trahissant pendant que l'autre coopère, puis l'inverse, chacun recevrait en moyenne $(T+S)/2$ par manche. Il faut que cette moyenne reste inférieure à $R$, faute de quoi l'alternance battrait la coopération mutuelle. Avec $R=2$ au lieu de 3, on aurait $2R=4<5$ et le code déclare que le jeu n'est plus un dilemme.

Pour le joueur 1, $T>R$ et $P>S$ : trahir rapporte strictement plus que coopérer, quel que soit le coup de l'autre, et la situation est la même pour le joueur 2. Trahir domine donc strictement coopérer, et $(D,D)$ est l'unique équilibre de Nash, ce que confirme la recherche exhaustive du notebook 01. Pourtant $(C,C)$ donne 3 à chacun contre 1 : cette issue Pareto-domine l'équilibre, puisque les deux joueurs y gagnent strictement. Le dilemme tient dans cet écart entre rationalité individuelle et intérêt collectif.

### 2.2 Horizon fini connu : l'induction à rebours

Si les deux joueurs savent que la partie compte exactement $n$ manches, la dernière manche est un dilemme à une manche, où l'on trahit. À l'avant-dernière, le gain futur est le même quel que soit le coup joué, puisque la dernière manche donnera $(D,D)$ dans tous les cas. Il s'ajoute à chaque case du tableau sans modifier les équilibres, et l'on trahit encore. Le raisonnement remonte ainsi jusqu'à la première manche. Le seul équilibre parfait en sous-jeux est « trahir à chaque manche », quel que soit $n$.

Le notebook 01 le vérifie par le calcul pour $n=1$, 2, 3, 5 et 200 : le chemin d'équilibre est toujours $(D,D)$ et le gain total de chaque joueur vaut $n\times P$. Sur 200 manches, la théorie prédit donc 200 points par joueur, alors que deux joueurs qui coopéreraient en obtiendraient $200\times R=600$. C'est le paradoxe du mille-pattes : un argument impeccable sur le papier conduit à une issue que personne n'espère atteindre. Il suppose que l'horizon est connu des deux joueurs et que leur rationalité est connue de tous ; si l'un de ces points manque, l'argument perd sa prise. Nos stratégies ne regardent d'ailleurs jamais le nombre de manches restantes.

### 2.3 Horizon indéterminé et seuils d'actualisation

Supposons maintenant que la partie continue après chaque manche avec la probabilité $\delta$. Sa longueur $L$ suit une loi géométrique d'espérance $1/(1-\delta)$, et un gain $g$ obtenu à chaque manche vaut $g/(1-\delta)$ en espérance. Le rancunier coopère tant que l'adversaire n'a jamais trahi, puis trahit pour toujours. Face à lui, coopérer sans cesse rapporte $R/(1-\delta)$, tandis que trahir dès la première manche rapporte $T$ puis $P$ à chaque manche suivante, soit $T+\delta P/(1-\delta)$. La coopération est stable si
$$\frac{R}{1-\delta}\;\ge\;T+\frac{\delta P}{1-\delta}\iff \delta\,(T-P)\ge T-R\iff \delta\ge\frac{T-R}{T-P}=\frac12 .$$
Le notebook 01 donne les valeurs. Pour $\delta=0{,}4$, coopérer vaut 5,000 et trahir 5,667 ; pour $\delta=0{,}5$, les deux valent 6,000 ; pour $\delta=0{,}6$, coopérer vaut 7,500 et trahir 6,500. La menace est crédible, car après une trahison continuer à trahir est la meilleure réponse, et trahir plus tard que la première manche conduit à la même comparaison.

Contre tit-for-tat (TFT), qui coopère au premier coup puis copie le dernier coup adverse, la déviation « trahir toujours » rapporte aussi $T$ puis $P$, donc impose le même seuil $1/2$. Mais une autre déviation existe : alterner trahison et coopération. Le déviant reçoit alors $T,S,T,S,\dots$ et obtient $(T+\delta S)/(1-\delta^2)$, ce qui ne dépasse pas la coopération si
$$\frac{T+\delta S}{1-\delta^{2}}\le\frac{R}{1-\delta}\iff T+\delta S\le R\,(1+\delta)\iff \delta\ge\frac{T-R}{R-S}=\frac23 .$$
À $\delta=0{,}6$, l'alternance rapporte 7,812 contre 7,500 à la coopération ; à $\delta=2/3$, les deux valent 9,000 ; à $\delta=0{,}7$, l'alternance tombe à 9,804 contre 10,000. Le seuil de TFT est le plus grand des deux, soit $2/3$. Nous testons ces deux déviations seulement : nous n'avons pas démontré qu'aucune autre déviation n'est plus exigeante, et le seuil de 2/3 est donc celui des déviations testées, non un seuil d'équilibre parfait démontré.

Une partie de 200 manches en moyenne correspond à $\delta=0{,}995$, bien au-dessus des deux seuils. Lorsque $\delta$ est proche de 1, le théorème de folk (Fudenberg et Maskin, 1986) montre cependant que la coopération n'est qu'un équilibre parmi beaucoup d'autres. La théorie la rend possible sans dire quelles stratégies réussissent face à une population variée, et c'est ce que le tournoi d'Axelrod vient mesurer.

### 2.4 Le bruit

Nous inversons chaque coup avec la probabilité $\varepsilon$, indépendamment pour chacun des deux joueurs et à chaque manche, selon l'idée de la main tremblante de Selten (1975). Les joueurs observent les coups exécutés, après inversion. Une erreur a des effets très différents selon la stratégie. Chez le rancunier, un seul coup inversé en trahison déclenche une trahison définitive des deux côtés. Chez TFT, il lance un écho où les deux joueurs alternent $(C,D)$ et $(D,C)$ jusqu'à une nouvelle erreur. Pavlov se rétablit en deux manches : après $(C,D)$ les deux changent de coup, jouent $(D,D)$, puis reviennent à $(C,C)$. Le tableau suivant, obtenu avec l'appel du notebook 01 (200 manches, 20 répétitions, graine 0), donne le score moyen par manche d'une stratégie qui joue contre elle-même.

| $\varepsilon$ | toujours_C | TFT | rancunier | Pavlov |
|---|---|---|---|---|
| 0 | 3,000 | 3,000 | 3,000 | 3,000 |
| 0,01 | 2,988 | 2,507 | 1,448 | 2,947 |
| 0,05 | 2,944 | 2,345 | 1,250 | 2,766 |

Un rancunier qui rencontre un rancunier passe de 3 à 1,448 dès que le bruit vaut 1 %. Les stratégies qui punissent sans pardonner paient leurs propres erreurs, ce qui explique que les classements changent avec $\varepsilon$.

### 2.5 La dynamique du réplicateur

Soit une population dont les parts $x_i$ sont celles des stratégies, et $M$ la matrice des scores moyens par manche, $M_{ij}$ étant le score de $i$ contre $j$. Le score de la stratégie $i$ est $f_i=(Mx)_i$ et la moyenne de la population est $\bar f=x^\top f$. À chaque génération,
$$x_i(t+1)=x_i(t)\,\frac{f_i}{\bar f}.$$
Une stratégie dont le score dépasse la moyenne gagne des parts, les autres en perdent. Les parts restent positives si les scores sont positifs ou nuls et si $\bar f>0$, et leur somme reste égale à 1 parce que $\sum_i x_i f_i=\bar f$. Une part nulle le reste : le modèle ne contient aucune mutation. Il s'agit d'une version à temps discret de la dynamique de Taylor et Jonker (1978). Comme $M$ vient d'un tournoi simulé, les trajectoires dépendent de la graine qui a servi à l'estimer.

### 2.6 Hypothèses et limites

Le modèle est symétrique, à deux joueurs qui jouent simultanément avec des gains constants et connus. Les six stratégies du guide, plus le TFT généreux en septième, forment un ensemble que nous avons choisi : un classement de tournoi n'a de sens que pour cette population, et une autre composition pourrait le renverser. Le bruit est indépendant d'une manche à l'autre, et personne ne se trompe en observant le coup adverse. Le réplicateur suppose une population infinie qui se mélange parfaitement. Les seuils $1/2$ et $2/3$ valent pour des joueurs qui maximisent un gain actualisé, ce que ne fait pas nécessairement un modèle de langage. Enfin, nos parties de modèles de langage sont courtes, de l'ordre de 10 manches contre 200 pour les stratégies : si l'horizon est annoncé, l'induction à rebours s'applique ; s'il ne l'est pas, le modèle ne peut pas la dérouler. Cette différence est une variable de nos expériences.
