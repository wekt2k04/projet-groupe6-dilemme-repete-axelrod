# MATIERE : Théorie des jeux et systèmes multi-agents, le cours expliqué en entier

Module de Pr A. Jraifi, IDIA3, ENSA Safi. Document d'équipe pour le projet 6 (dilemme du prisonnier répété, tournoi d'Axelrod, agents LLM). But : que chaque membre puisse expliquer à l'oral tout le cours, des définitions de base jusqu'aux agents LangChain, et sache dire ce qui vient du prof et ce qui a été ajouté.

## 0. Mode d'emploi, statuts et sources

### 0.1 Structure de chaque notion

Chaque notion suit le même ordre : **Définition**, **Formule**, **Exemple chiffré**, **Piège**, **Lien projet 6** (quand il existe). Tous les chiffres des exemples ont été calculés en Python pendant la rédaction (anaconda, graines fixées pour les simulations) et recopiés tels quels. Les nombres de la synthèse de Wilfried (notebook) ont été recalculés : ils sont reproduits, avec les mêmes valeurs, sauf mention contraire.

### 0.2 Les deux statuts

- **Vu en cours** : présent dans le cours du prof, c'est-à-dire le chapitre 1 (`ch1-v3.pdf`), le TD1 et son corrigé, plus ce que le notebook déclare venir du cours.
- **Complété (hors cours du prof)** : notions standard ajoutées par le notebook (chapitres 9 à 11, selon le journal) ou reconstruites ici faute de support du prof. Ces sections sont vraies mathématiquement mais ne prouvent pas que le prof les enseigne sous cette forme.

Quand un titre porte les deux statuts, chaque sous-section précise le sien.

### 0.3 État des sources

| Source | Lecture | Remarque |
|---|---|---|
| `ch1-v3.pdf` (9 pages) | lue en entier (pdftotext) | accents détruits par l'encodage, texte exploitable ; contenu : §1.1 à 1.10 |
| `TD1.pdf` et corrigé `.md` | lus en entier | exercices 1.1 à 1.7, six vrai/faux, projet Python |
| `3_Notebook_TJ.ipynb` (248 cellules) | lu en entier | synthèse de Wilfried, chapitres 1 à 13 ; chiffres recalculés |
| `Game Theory.pdf` (20 pages) | lu en texte (pages 1 à 4, projets 1 à 6) | guide des projets ; texte OCR imparfait, formules parfois abîmées |
| Supports du prof au delà du chapitre 1 | **absents** des ressources | impossible de vérifier ce que le prof a enseigné sur Bayes, Shapley, PSO, ACO, boids et l'agent à 10 outils |
| PDF « Google Gemini » | non lu | le notebook le classe comme résumé IA à ne pas croire sans vérifier |

Point important : la règle d'or n°2 du guide dit que le code du cours contient « équilibres de Nash, induction à rebours, Bayes, Shapley, PSO, ACO, boids, agent `agent_tj_sma.py` avec ses 10 outils ». Ces thèmes sont donc bien au programme, mais je n'ai pas les supports : les sections 5 à 8 sont étiquetées « Complété » parce que leur contenu vient du savoir standard et des formules du guide, pas d'un cours que j'ai lu. Quand une formule vient du guide du prof, c'est indiqué.

### 0.4 Écarts constatés entre les sources

1. Le notebook (chapitre 7) cite « ch1-v3 (jeu répété, Tit-for-Tat) ». Or `ch1-v3` ne contient aucun jeu répété : Tit-for-Tat est dans le **TD1, exercice 1.6**, et le grim trigger est un « bonus (hors programme) » du corrigé.
2. L'induction à rebours n'est pas dans `ch1-v3` (seul l'arbre de l'entrant, exemple 1.2, y figure). La méthode est dans le **TD1, exercice 1.5**.
3. Cours et TD notent différemment : route (S,S) vaut $(-1,-1)$ au cours et $(0,0)$ au TD ; bataille des sexes $(5,2),(2,5)$ au cours (Garba / DJ Arafat) contre $(5,3),(3,5)$ au TD (Garba / Concert) ; le TD a deux exercices numérotés 1.5.
4. Le guide cite pour la bataille des sexes « du cours » les probabilités $p=2/3$, $q=1/3$. Cela ne correspond ni à la version du cours ($5/7$ et $2/7$) ni à celle du TD ($5/8$ et $3/8$). Non vérifié : ce sont peut-être d'autres gains, non fournis.
5. Le guide cite Bière ou Quiche avec $P(\text{Fort})=0{,}9$ puis $0{,}3$ et un équilibre poolant Bière « valide pour $0{,}6$, non valide pour $0{,}2$ ». Avec les gains standard de la section 5, je retrouve ce résultat pour $0{,}9$ mais je ne trouve aucun équilibre en stratégies pures pour $0{,}3$. Cas $0{,}3$ non reproduit.
6. Les valeurs par défaut de `tournoi()` dans le guide sont illisibles (OCR) : ignorées.

### 0.5 Gains de référence

- **Dilemme du cours** (années de prison, donc gains négatifs) : $(\text{Nier},\text{Nier})=(-1,-1)$, $(\text{Nier},\text{Avouer})=(-10,0)$, $(\text{Avouer},\text{Nier})=(0,-10)$, $(\text{Avouer},\text{Avouer})=(-5,-5)$.
- **Dilemme du projet 6** : $T=5$ (tentation), $R=3$ (récompense), $P=1$ (punition), $S=0$ (pigeon). Coopérer $=C$, trahir $=D$. Matrice (joueur ligne, joueur colonne) : $(C,C)=(3,3)$, $(C,D)=(0,5)$, $(D,C)=(5,0)$, $(D,D)=(1,1)$.

---

## 1. Jeux en forme normale et extensive, dominance, Pareto

**Statut : Vu en cours** (`ch1-v3` §1.1 à 1.6 et 1.8 ; TD1 exercices 1.1, 1.3, 1.4, vrai/faux 1, 2, 5). Exceptions **Complété** : dominance faible et élimination itérée sur un tableau $3\times3$ (le cours n'illustre l'élimination « successive » que sur le dilemme).

### 1.1 Origines et agent rationnel

**Définition.** La théorie des jeux modélise les situations où mon résultat dépend aussi des décisions des autres (prix d'un concurrent, partage de bande passante, négociation). Fondateurs : Cournot (1838, duopole), von Neumann (1928, théorème du minimax), Nash (1950, thèse de 27 pages, équilibre de Nash, prix Nobel d'économie 1994). Un joueur est **rationnel** s'il connaît ses objectifs et ses alternatives et choisit l'action qui maximise son gain (« payoff »). Trois piliers : **égoïsme** (il maximise son propre gain), **intelligence** (il calcule et anticipe), **connaissance commune** (chacun sait que les autres sont rationnels, sait qu'ils savent qu'il l'est, et ainsi de suite).

**Piège.** La théorie ne dit pas que les humains sont rationnels : elle étudie ce qui arriverait si tous jouaient la logique pure. « Rationnel » ne veut pas dire « moralement égoïste » : le gain peut contenir de l'altruisme. Un agent rationnel maximise le gain **espéré** avec ce qu'il sait ; il n'est pas omniscient.

**Lien projet 6.** Un agent LLM n'est pas garanti rationnel au sens du cours. Le projet mesure justement l'écart entre ce qu'il joue et ce que la théorie prédit (trahison en fin de partie à horizon connu).

### 1.2 Éléments d'un jeu et typologie

**Définition.** Un jeu stratégique est la donnée de trois composantes : les **joueurs** $I=\{1,\dots,N\}$ ; pour chaque joueur $i$, un ensemble de **stratégies** $A_i$ ($a_i\in A_i$) ; des **gains** $\pi_i:A_1\times\cdots\times A_N\to\mathbb{R}$. Un **profil** est une combinaison $a=(a_1,\dots,a_N)$ ; on note $a_{-i}$ les choix de tous sauf $i$. Une stratégie **pure** est une action choisie avec certitude ; une stratégie **mixte** est une loi de probabilité sur les actions pures (section 2).

**Formule.** Nombre de profils $=\prod_{i=1}^N |A_i|$ ; nombre de gains à écrire $=N\prod_i|A_i|$.

**Exemple chiffré.** Joueur 1 avec 3 stratégies, joueur 2 avec 4 : $3\times4=12$ cases, $24$ gains. Trois joueurs à $2,3,4$ stratégies : $24$ profils, $72$ gains. Dix joueurs à deux stratégies : $2^{10}=1\,024$ profils ; vingt joueurs : $2^{20}=1\,048\,576$. Le tableau grandit exponentiellement, d'où les algorithmes des sections 6 et 7.

Typologie du cours :

| Critère | Type A | Type B |
|---|---|---|
| Somme des gains | somme nulle : total constant (poker, échecs, pile ou face) | somme non nulle : total variable (dilemme, négociation) |
| Accords | coopératif : accords contraignants, coalitions | non coopératif : chacun pour soi (type le plus étudié en cours) |
| Temporalité | simultané : forme normale (tableau) | séquentiel : le second observe, forme extensive (arbre) |

**Exemple chiffré (somme nulle).** Les sommes des quatre cases du dilemme du projet valent $\{6,5,5,2\}$, donc l'ensemble $\{2,5,6\}$ : non constant, jeu à somme non nulle. Pour le dilemme du cours les sommes sont $\{-2,-10,-10,-10\}$. Seul Matching Pennies, parmi les jeux du TD, a une somme constante (0).

**Piège.** « Somme nulle » veut dire « somme **constante** » (pas forcément 0). Ne pas dire que le dilemme est à somme nulle « parce que l'un gagne quand l'autre perd » : avec $(R,R)$ les deux gagnent. TD1 vrai/faux 1 : « un jeu se définit uniquement par le nombre de joueurs » est **faux** (il faut joueurs, stratégies, gains).

### 1.3 Forme normale et forme extensive

**Définition.** La **forme normale** (jeux simultanés) est la matrice des gains ; dans chaque case on écrit (gain du joueur Ligne, gain du joueur Colonne). La **forme extensive** (jeux séquentiels) est un arbre : **nœuds** (points de décision), **branches** (actions), **feuilles** (gains finaux). On lit de gauche à droite.

**Exemple chiffré.** Forme normale : le dilemme (sous-section 0.5). Forme extensive : l'entrant potentiel (exemple 1.2 du cours). E choisit *Entrer* ou *Ne pas entrer* $(0,300)$ ; si E entre, I choisit *Coopérer* $(40,50)$ ou *Combattre* $(-10,0)$. Un même jeu peut s'écrire sous les deux formes : la forme normale de l'entrant est $\begin{pmatrix}(40,50)&(-10,0)\\(0,300)&(0,300)\end{pmatrix}$ (lignes : Entrer, Ne pas entrer ; colonnes : Coopérer, Combattre).

**Piège.** La forme normale oublie l'**ordre** des coups : elle laisse I « choisir Combattre » comme s'il s'engageait à l'avance (section 3).

### 1.4 Dominance

**Définition.** $a_i$ est **strictement dominante** si, quels que soient les choix des autres, elle rapporte strictement plus que toute autre stratégie :
$$\pi_i(a_i,a_{-i})>\pi_i(a_i',a_{-i})\quad\forall a_{-i},\ \forall a_i'\neq a_i.$$
Une stratégie est **strictement dominée** s'il en existe une autre qui rapporte toujours strictement plus. **Élimination itérée** : on retire les stratégies dominées, puis on recommence sur le jeu réduit. **Dominance faible** : $\ge$ partout et $>$ pour au moins un $a_{-i}$ (Complété).

**Exemple chiffré (projet 6).** Pour le joueur ligne : si l'autre joue $C$, $D$ donne $5$ et $C$ donne $3$ ($5>3$) ; si l'autre joue $D$, $D$ donne $1$ et $C$ donne $0$ ($1>0$). Donc $D$ est strictement dominante, $C$ strictement dominée, et par symétrie l'issue logique est $(D,D)=(1,1)$.

**Élimination itérée (Complété).** Jeu $3\times3$ : R1 $=(4,3),(5,1),(6,2)$ ; R2 $=(2,1),(8,4),(3,6)$ ; R3 $=(3,0),(9,6),(2,8)$. Tour 1 : la colonne C3 domine C2 pour le joueur 2 ($2>1$, $6>4$, $8>6$), on retire C2. Tour 2 : R1 domine R2 ($4>2$, $6>3$) et R3 ($4>3$, $6>2$). Tour 3 : face à R1, C1 ($3$) bat C3 ($2$). Reste $(R1,C1)=(4,3)$, l'unique équilibre de Nash. Autre jeu $2\times3$ : Haut $=(1,0),(1,2),(0,1)$ ; Bas $=(0,3),(0,1),(2,0)$ : on retire Droite, puis Bas, puis Gauche ; reste (Haut, Milieu) $=(1,2)$.

**Dominance faible : un équilibre perdu (Complété).** Jeu $(T,L)=(1,1)$, les trois autres cases $(0,0)$. Les équilibres purs sont $(T,L)$ et $(B,R)$. Or $B$ est faiblement dominée par $T$ et $R$ par $L$ : éliminer les stratégies faiblement dominées supprime $(B,R)$. D'où la règle : on n'élimine proprement que les stratégies **strictement** dominées (l'ordre n'importe alors pas et aucun équilibre n'est perdu).

**Piège.** Une stratégie dominante n'est pas celle qui contient le plus gros gain de la matrice : elle doit être meilleure **colonne par colonne**. Dans le jeu de la route (TD1, 1.1), A préfère C face à S ($2>0$) mais S face à C ($-1>-10$) : aucune dominante. Dominante $\neq$ meilleure réponse (meilleure face à *un* choix donné). TD1 vrai/faux 5 est **faux** : si un joueur a une dominante $s^*$, l'autre joue sa meilleure réponse $b$ et $(s^*,b)$ est un équilibre pur ; un jeu sans équilibre pur (Matching Pennies) n'a donc aucune dominante.

**Lien projet 6.** C'est la première chose à dire à l'oral : dans le dilemme à une manche, $D$ domine, donc $(D,D)$. Toute la suite du projet répond à : comment sortir de là ?

### 1.5 Optimum de Pareto

**Définition.** Un profil est un **optimum de Pareto** si l'on ne peut pas améliorer le sort d'un joueur sans détériorer celui d'au moins un autre. Un profil $a'$ **domine $a$ au sens de Pareto** si $\pi_i(a')\ge\pi_i(a)$ pour tout $i$, avec $>$ pour au moins un.

**Méthode.** Comparer la case à **toutes** les autres.

**Exemple chiffré (projet 6).** $(C,C)=(3,3)$, $(C,D)=(0,5)$ et $(D,C)=(5,0)$ ne sont dominés par aucune case : ce sont les trois optimums de Pareto. $(D,D)=(1,1)$ est dominé par $(C,C)$ ($3>1$ pour les deux) : l'équilibre n'est **pas** optimal. Dilemme du cours : $(-1,-1)$, $(-10,0)$, $(0,-10)$ sont Pareto-optimaux, $(-5,-5)$ ne l'est pas. TD1 1.4 : dans $\begin{pmatrix}(10,10)&(0,5)\\(5,0)&(5,5)\end{pmatrix}$ les équilibres sont $(A,X)$ et $(B,Y)$ ; $(A,X)$ est Pareto-optimal, $(B,Y)$ est dominé par $(A,X)$ ($10>5$ pour chacun).

**Paradoxe de la rationalité individuelle.** En suivant son intérêt chacun joue la dominante, et le groupe tombe en $(-5,-5)$ au lieu de $(-1,-1)$ (ou en $(1,1)$ au lieu de $(3,3)$).

**Piège.** Nash $\neq$ Pareto, dans les deux sens : $(C,C)$ est Pareto-optimal sans être un équilibre ; $(D,D)$ est un équilibre sans être Pareto-optimal. Autres cas : dans la route (TD), $(S,S)=(0,0)$ est Pareto-optimal sans être un équilibre ; dans la bataille des sexes les deux équilibres sont Pareto-optimaux (le problème est la coordination, pas l'efficacité). Dans un jeu à somme nulle comme Matching Pennies, **les quatre cases** sont Pareto-optimales. Pareto ne dit rien d'équitable : $(0,-10)$ est efficace et très injuste. Ne pas confondre « dominé au sens de Pareto » (comparaison de **profils**) et « stratégie dominée » (comparaison de **stratégies** d'un joueur). TD1 vrai/faux 2 : « un équilibre est toujours un optimum de Pareto » est **faux** (dilemme).

**Lien projet 6.** $(C,C)=(3,3)$ Pareto-domine $(D,D)=(1,1)$ mais n'est pas un équilibre du jeu à une manche : c'est le moteur du projet.

---

## 2. Équilibre de Nash : pur, mixte, indifférence, supports, maximin

**Statut : Vu en cours** pour Nash pur, méthode des cases, théorème de Nash, Matching Pennies et bataille des sexes en mixte, maximin (`ch1-v3` §1.3.1, 1.7, 1.9 ; TD1 exercices 1.1, 1.2, 1.5 bis, 1.7, vrai/faux 3, 6). **Complété** : formule générale $2\times2$, énumération des supports, minimax par programmation linéaire, faucon-colombe, pierre-feuille-ciseaux.

### 2.1 Équilibre de Nash en stratégies pures

**Définition.** Un profil $a^*=(a_1^*,\dots,a_N^*)$ est un **équilibre de Nash** si aucun joueur ne peut augmenter son gain en changeant **seul** de stratégie, les autres gardant la leur :
$$\pi_i(a_i^*,a_{-i}^*)\ \ge\ \pi_i(a_i,a_{-i}^*)\qquad\forall i,\ \forall a_i\in A_i.$$
Chaque stratégie est une **meilleure réponse** aux autres : situation de repos, sans regret.

**Méthode des cases (cours, 2 joueurs).** (1) Pour chaque **colonne**, entourer le meilleur gain du joueur ligne. (2) Pour chaque **ligne**, entourer le meilleur gain du joueur colonne. (3) Une case aux deux gains entourés est un équilibre. On ne compare jamais en diagonale : le joueur ligne compare sa case aux autres cases de la **même colonne**, le joueur colonne aux cases de la **même ligne**.

**Exemple chiffré.** Dilemme du projet : colonne $C$, le ligne préfère $D$ ($5>3$) ; colonne $D$, il préfère $D$ ($1>0$) ; ligne $C$, le colonne préfère $D$ ($5>3$) ; ligne $D$, il préfère $D$. Seule $(D,D)=(1,1)$ est doublement entourée. Autres jeux du cours et du TD :

| Jeu | Équilibres purs | Remarque |
|---|---|---|
| Dilemme | $(D,D)$ | un seul, dominant, non Pareto |
| Route (TD1 1.1) | $(S,C)$ et $(C,S)$ | $(S,S)$ n'est **pas** un équilibre : A gagne $2>0$ en passant à $C$ |
| Bataille des sexes | $(G,G)$ et $(C,C)$ (TD : $(5,3)$ et $(3,5)$) | deux équilibres, problème de coordination |
| Chasse au cerf | $(C,C)=(10,10)$ et $(L,L)=(5,5)$ | le cerf est rationnel si $P(\text{autre cerf})>1/2$ |
| Matching Pennies | aucun | voir 2.3 |

**Combien d'équilibres purs ?** Sur les $256$ jeux $2\times2$ à gains $0/1$, le nombre d'équilibres purs vaut $0$ (2 jeux), $1$ (44), $2$ (114), $3$ (80) ou $4$ (16) ; $3$ et $4$ n'apparaissent qu'avec des égalités de gains. Sur les $576$ jeux $2\times2$ à préférences strictes (aucune égalité), il y en a $0$ (72 jeux), $1$ (432) ou $2$ (72) : jamais plus de deux.

**Théorème de Nash (1950).** Tout jeu statique fini (nombre fini de joueurs et de stratégies) admet au moins un équilibre de Nash, éventuellement en stratégies mixtes.

**Piège.** (1) Tester $(S,S)$ de la route « parce que tout le monde est content » : faux. (2) S'arrêter au premier équilibre trouvé. (3) Croire qu'un jeu fini a toujours un équilibre **pur** : seul l'équilibre éventuellement mixte est garanti. (4) Dominante $\Rightarrow$ équilibre, mais équilibre $\not\Rightarrow$ dominante. (5) Un équilibre peut être injuste (route : $(S,C)=(-1,2)$) mais il est stable. (6) Plusieurs équilibres : la théorie ne dit pas lequel sera joué (coordination, section 7.6).

**Lien projet 6.** Le jeu à une manche a pour unique équilibre pur $(D,D)$. La répétition crée de nouveaux équilibres (section 4).

### 2.2 Stratégies mixtes et principe d'indifférence

**Définition.** Une stratégie mixte est une loi de probabilité sur les stratégies pures (par exemple Pierre $50\,\%$, Feuille $30\,\%$, Ciseaux $20\,\%$). On l'utilise pour être **imprévisible** : celui qui joue toujours Pierre sera battu par Feuille à chaque coup.

**Principe d'indifférence.** À l'équilibre mixte, chaque joueur est indifférent entre les stratégies pures qu'il joue, et c'est la loi de **l'autre** qui l'y rend. Donc, pour trouver la probabilité d'un joueur, on **égalise les espérances de gain de l'autre**.

**Formule $2\times2$ (Complété).** Gains $\begin{pmatrix}(a_1,b_1)&(a_2,b_2)\\(a_3,b_3)&(a_4,b_4)\end{pmatrix}$, $p=P(\text{ligne 1})$, $q=P(\text{colonne 1})$ :
$$p=\frac{b_4-b_3}{(b_1-b_3)-(b_2-b_4)}\ \text{(rend la colonne indifférente)},\qquad q=\frac{a_4-a_2}{(a_1-a_2)-(a_3-a_4)}\ \text{(rend la ligne indifférente)}.$$
Un équilibre entièrement mixte n'existe que si $p,q\in\,]0,1[$.

**Exemple chiffré 1 : Matching Pennies (TD1 1.2).** J1 gagne si les pièces sont égales. Avec $q=P(\text{J2 joue Pile})$ : $E(\text{Pile})=q-(1-q)=2q-1$ et $E(\text{Face})=1-2q$. Égalité : $2q-1=1-2q$, donc $q=1/2$ ; par symétrie $p=1/2$. Gain espéré $0$. Il n'y a aucun équilibre pur : dans chaque case un joueur veut dévier. Bonus du TD : $E_1(p,q)=(2p-1)(2q-1)$, soit $0$ pour $(0{,}5;0{,}5)$, $1$ pour $(1;1)$, $-0{,}24$ pour $(0{,}3;0{,}8)$.

**Exemple chiffré 2 : bataille des sexes du TD (1.5 bis).** $p=P(\text{Yaya joue G})$, $q=P(\text{Fanta joue G})$. Fanta indifférente : $3p=5(1-p)$, donc $p=5/8$. Yaya indifférent : $5q=3(1-q)$, donc $q=3/8$. Gain espéré $5q=3p=15/8=1{,}875$ pour chacun, **moins bon** que chaque équilibre pur (5 ou 3). Raison : on ne se coordonne qu'avec la probabilité $pq+(1-p)(1-q)=15/32\approx47\,\%$, le reste du temps les deux obtiennent $0$. Version du cours $(5,2),(2,5)$ : $p=5/7$, $q=2/7$, gain $10/7\approx1{,}43$.

**Exemple chiffré 3 : route, cours contre TD.** Cours ($(S,S)=(-1,-1)$) : $p=3/4$ de s'arrêter, gain $-1$, collision $(1/4)^2=1/16$. TD ($(S,S)=(0,0)$) : $p=9/11$, gain $-2/11$, collision $(2/11)^2=4/121$. Mêmes équilibres purs, **mixtes différents** : changer un seul gain change le mixte.

**Exemple chiffré 4 (Complété).** Chasse au cerf : $q=1/2$, gain $5$ (égal à $(L,L)$, inférieur à $(C,C)=10$). Faucon-colombe, valeur $V=4$, coût du combat $C=6$ : $(F,F)=(-1,-1)$, $(F,Co)=(4,0)$, $(Co,Co)=(2,2)$ ; équilibres purs $(F,Co)$ et $(Co,F)$ ; mixte $P(F)=V/C=2/3$, gain $2/3$ (très inférieur à $2$, tous colombes).

**Piège.** (1) Calculer $q$ avec **ses propres** gains : faux, $q$ se trouve avec ceux de l'autre. (2) Oublier de vérifier $p,q\in[0,1]$ : pour le dilemme la formule donne $p=q=-1$, hors intervalle, donc pas d'équilibre mixte intérieur (il existe un pur). (3) Réflexe de symétrie : avec $A=\begin{pmatrix}2&-1\\-1&1\end{pmatrix}$ (somme nulle) on trouve $q=2/5$ et valeur $1/5$, pas $1/2$. (4) TD1 vrai/faux 3 « stratégie mixte = hasard sans calcul » est **faux** : les probabilités sont calculées pour rendre l'adversaire indifférent. (5) Le mixte n'est pas forcément meilleur que les purs (bataille : pire).

**Lien projet 6.** Le joueur « aléatoire » du tournoi est une stratégie mixte $1/2$-$1/2$ qui n'est un équilibre de rien ; le bruit $\varepsilon$ se modélise aussi comme un mélange (« la main tremble »).

### 2.3 Énumération des supports et jeux $m\times n$ (Complété)

**Définition.** Pour un jeu $m\times n$ non dégénéré, on essaie chaque couple de supports $(I,J)$ de même taille $k$, on résout l'indifférence $(Ay)_i=v$ pour $i\in I$ et $(x^\top B)_j=w$ pour $j\in J$ avec $\sum x=\sum y=1$, puis on vérifie la non-déviation hors des supports. Cette méthode est celle du projet 1 du guide ; le nombre de supports est exponentiel.

**Exemple chiffré.** Sur la bataille du TD, l'énumération trouve trois équilibres : $((1,0),(1,0))$ gains $(5,3)$, $((0,1),(0,1))$ gains $(3,5)$ et le mixte $((5/8,3/8),(3/8,5/8))$ gains $(1{,}875;1{,}875)$. Sur pierre-feuille-ciseaux ($3\times3$, gains $\pm1$) la résolution du système d'indifférence donne $(1/3,1/3,1/3)$ pour les deux, valeur $0$ ; c'est l'unique équilibre. Sur le dilemme elle ne trouve que $(D,D)$.

**Piège.** Oublier le test de non-déviation hors support ; confondre la matrice $A$ du joueur 1 et $B$ du joueur 2 ; comparer des flottants sans tolérance ; conclure à l'absence d'équilibre sur un jeu dégénéré.

### 2.4 Maximin, minimax et somme nulle

**Définition (Vu en cours).** Nash suppose que l'on est sûr de la rationalité des autres. Von Neumann propose le **maximin** (comportement prudent) : maximiser son gain **minimum**. Pour chaque action on repère le pire gain, puis on choisit l'action dont le pire résultat est le moins mauvais : $\max_i\min_j u_1(i,j)$.

**Exemple chiffré (TD1 1.7, Abel / Lisa).** Lignes A $=(5,2),(3,3)$ ; B $=(0,8),(0,-1)$ ; C $=(-20,4),(5,5)$. Pires gains d'Abel : $3$, $0$, $-20$ ; maximin **A** (au moins $3$ garanti). Équilibre de Nash : **(C,Y) $=(5,5)$** (Abel : face à X meilleur A, face à Y meilleur C ; Lisa : face à A meilleur Y, face à B meilleur X, face à C meilleur Y). Nash donne plus ($5>3$) mais Abel perd $20$ si Lisa joue X : **le maximin est le plus prudent**. Le maximin de Lisa se calcule avec **ses** gains, par colonne : minima $2$ (X) et $-1$ (Y), donc X, alors que son équilibre est Y. Dans le dilemme du cours, maximin $=$ Avouer (pire cas $-5$ contre $-10$) $=$ Nash. Dans le dilemme du projet, pires gains $0$ ($C$) et $1$ ($D$) : maximin $=D$, niveau de sécurité $1$.

**Théorème du minimax (Complété dans sa forme mixte).** En somme nulle avec stratégies mixtes, $\max_x\min_y x^\top Ay=\min_y\max_x x^\top Ay$ : c'est la **valeur du jeu**, atteinte à l'équilibre de Nash. Calcul par programmation linéaire : maximiser $v$ sous $\sum_i x_iA_{ij}\ge v$ pour toute colonne $j$, $\sum_i x_i=1$, $x\ge0$. Matching Pennies : $x=(1/2,1/2)$, $v=0$. Version asymétrique $A=\begin{pmatrix}2&-1\\-1&1\end{pmatrix}$ : $x=(0{,}4;0{,}6)$, $v=0{,}2=1/5$ (les maximin et minimax **purs** valent $-1$ et $1$ : sans mixte ils ne coïncident pas).

**Piège.** TD1 vrai/faux 6 : « le maximin maximise le gain le plus élevé » est **faux** (il maximise le gain **minimum**). Ne pas confondre maximin et maximax. En somme **non** nulle, maximin et Nash divergent (Abel : A contre C).

**Lien projet 6.** Le niveau de sécurité $P=1$ (jouer $D$) est le **gain de punition** du théorème de folklore (section 4.6).

---

## 3. Induction à rebours, équilibre parfait en sous-jeux, menaces non crédibles

**Statut : Vu en cours** pour l'entrant potentiel, l'induction à rebours, l'EPSJ et la menace non crédible (arbre dans `ch1-v3` exemple 1.2 ; méthode dans **TD1 exercice 1.5** et son corrigé ; vrai/faux 4). **Complété** : confiance à trois étapes, mille-pattes, Cournot contre Stackelberg, ultimatum (le guide les cite comme exemples du cours ou formules du projet 2, mais je n'ai pas les supports).

### 3.1 Sous-jeux et induction à rebours

**Définition.** Dans un jeu séquentiel on ne peut pas choisir au début sans savoir ce que feront les joueurs **après**. L'**induction à rebours** part des **derniers nœuds** : à chacun, le joueur qui joue prend ce qui maximise **son** gain ; on remplace le nœud par ce gain et on remonte jusqu'à la racine. Le résultat est l'**équilibre parfait en sous-jeux** (EPSJ) : un équilibre de Nash dans **chaque** sous-jeu, y compris ceux qu'on ne joue pas. Une **stratégie** est un plan complet (une action à chaque nœud où l'on peut avoir à jouer), pas seulement le chemin joué.

**Formule.** $V(\text{nœud})=\max_{a}V(\text{enfant}_a)$ pour la composante du joueur qui joue en ce nœud ; on résout de la fin vers la racine.

**Exemple chiffré : l'entrant potentiel (TD1 1.5).** Gains (E, I) : Ne pas entrer $(0,300)$ ; Entrer puis Coopérer $(40,50)$ ; Entrer puis Combattre $(-10,0)$. Dernier nœud (I) : $50>0$, I **coopère**, gains $(40,50)$. Racine (E) : $40>0$, E **entre**. EPSJ : $(\text{Entrer},\text{Coopérer})=(40,50)$. Stratégies complètes : E : Entrer ; I : Coopérer si E entre.

**Piège.** (1) Induire du début vers la fin : faux. (2) Raisonner avec les gains de E au nœud de I : au nœud de I, c'est le gain de **I** qui compte. (3) Prendre $300$ pour « le meilleur gain de I » : I ne l'obtient que si E n'entre pas. (4) Écrire la stratégie de I comme « Coopérer » seulement : c'est « Coopérer si E entre ». TD1 vrai/faux 4 est **vrai** : l'induction résout les jeux séquentiels **finis à information parfaite**. Avec information imparfaite il faut l'équilibre bayésien parfait (section 5).

**Lien projet 6.** Un dilemme répété un nombre connu de fois est un jeu séquentiel fini : l'induction à rebours s'y applique (section 4.2).

### 3.2 Menace non crédible, engagement

**Définition.** Une **menace** est crédible si l'exécuter est dans l'intérêt du menaçant **au moment où il doit jouer**. Sa « force » n'y change rien.

**Exemple chiffré.** Dans l'entrant, la menace « je combattrai si tu entres » n'est pas crédible : une fois E entrée, combattre rapporte $0$ à I et coopérer $50$. Pourtant la forme normale $\begin{pmatrix}(40,50)&(-10,0)\\(0,300)&(0,300)\end{pmatrix}$ a **deux** équilibres de Nash : $(\text{Entrer},\text{Coopérer})=(40,50)$ et $(\text{Ne pas entrer},\text{Combattre})=(0,300)$. Le second repose sur la menace : I y est indifférent ($300$ dans les deux cas pour lui) et E, croyant la menace, reste dehors. Il n'est **pas** parfait en sous-jeux. Si l'on change le gain de Combattre en $(-10,60)$, alors $60>50$ : I combat vraiment, E reste dehors, issue $(0,300)$ : la menace est devenue crédible (engagement, investissement irréversible, réputation).

**Piège.** Tout EPSJ est un Nash, pas l'inverse : un équilibre de Nash peut reposer sur une menace non crédible (même défaut que la dominance faible, section 1.4). Croire qu'une menace est crédible parce qu'elle est « forte » : faux.

### 3.3 Confiance et paradoxe du mille-pattes (Complété)

**Jeu de la confiance à trois étapes.** A choisit *Quitter* $(1,1)$ ou *Continuer* ; puis B choisit *Quitter* $(0,3)$ ou *Continuer* ; puis A choisit *Partager* $(2,2)$ ou *Prendre* $(3,1)$. Dernier nœud (A) : $3>2$, A prend, donc si B continue l'issue est $(3,1)$. Nœud B : Quitter $=3$ contre $1$, B quitte, $(0,3)$. Premier nœud (A) : Quitter $=1$ contre $0$, A quitte. EPSJ : $(1,1)$, alors que $(2,2)$ était meilleur pour les deux. La coopération est détruite par le manque de crédibilité du dernier coup.

**Mille-pattes à trois étapes (gains illustratifs, de moi).** Étape 1 (A) : *Stop* $(1,0)$ ou continuer. Étape 2 (B) : *Stop* $(0,2)$ ou continuer. Étape 3 (A) : *Stop* $(3,1)$ ou *Continuer* $(2,4)$. Induction : étape 3, $3>2$, A arrête ; étape 2, B compare $2$ (stop) à $1$ (ce qu'il aurait en continuant) et arrête ; étape 1, A compare $1$ à $0$ et arrête. Résultat : **Stop dès la première étape, $(1,0)$**, alors que « tout continuer » donnerait $(2,4)$, meilleur pour les deux. Le guide cite un mille-pattes à trois étapes dont l'EPSJ vaut $(1,0)$ ; j'ignore ses autres gains, donc ceux ci-dessus sont les miens, choisis pour retrouver ce $(1,0)$.

**Paradoxe.** Une induction logiquement correcte contredit l'expérience : les humains (et les LLM) coopèrent au début d'un mille-pattes ou d'un dilemme répété, puis dégradent vers la fin. C'est l'**effet d'horizon**.

**Lien projet 6.** C'est exactement la prédiction à tester : horizon annoncé de 10 manches $\Rightarrow$ la théorie prévoit $D$ à toutes les manches ; un TFT, lui, coopère jusqu'à la fin.

### 3.4 Avantage du premier joueur : Cournot et Stackelberg (Complété)

**Définition.** Demande inverse $P=a-bQ$, coût marginal $c$. **Cournot** : quantités choisies simultanément ; meilleure réponse $q_i=(a-c-bq_j)/(2b)$. **Stackelberg** : la firme 1 choisit $q_1$ d'abord, la firme 2 observe ; on résout par induction à rebours.

**Formules.** Cournot, $n$ firmes : $q^*=\dfrac{a-c}{(n+1)b}$ ; duopole : profit $\dfrac{(a-c)^2}{9b}$. Stackelberg : suiveur $q_2=\dfrac{a-c-bq_1}{2b}$, meneur $q_1=\dfrac{a-c}{2b}$, puis $q_2=\dfrac{a-c}{4b}$ ; profits $\dfrac{(a-c)^2}{8b}$ et $\dfrac{(a-c)^2}{16b}$ (formules du guide, projets 1 et 2).

**Exemple chiffré** ($a=100$, $b=1$, $c=10$). Cournot : $q^*=30$ chacun, prix $40$, profit $30\times30=900$. Stackelberg : $q_1=45$, $q_2=22{,}5$, prix $32{,}5$, profits $1\,012{,}5$ (meneur) et $506{,}25$ (suiveur). Le meneur gagne plus que $900$, le suiveur moins. Monopole : $Q=45$, prix $55$, profit $2\,025$ ; le cartel à $22{,}5$ chacun donne $1\,012{,}5$ à chacun. L'itération des meilleures réponses converge vers $30$ (facteur de contraction $1/2$) : après 12 pas on est à $29{,}9927$.

**Piège.** Le meneur ne joue pas la quantité de Cournot : il anticipe la réaction du suiveur. La valeur de l'engagement vient de l'ordre des coups, pas de la taille.

### 3.5 Ultimatum (Complété)

**Définition.** Le proposant offre $x$ sur un total de $10$ ; si le répondant accepte, gains $(10-x,x)$, sinon $(0,0)$.

**Exemple chiffré.** Si le répondant accepte en cas d'indifférence, l'EPSJ est l'offre $0$ (gain $10$ pour le proposant) ; s'il refuse l'indifférence, l'offre minimale est $1$ (gain $9$). Les humains s'écartent beaucoup de cette prédiction (ils refusent les offres basses). Piège : l'EPSJ est sensible à ce détail de tie-break.

---

## 4. Jeux répétés : horizon, actualisation, folklore, Axelrod, bruit, réplicateur

**Statut : mixte.** **Vu en cours** : 4.1 (TD1 exercice 1.6 : pourquoi $(\text{Nier},\text{Nier})$ n'est pas un équilibre à un coup, définition de Tit-for-Tat, ombre du futur) et 4.2 (conséquence directe de l'induction à rebours ; le guide du projet 6 la cite comme « lien avec le cours »). **Complété (hors cours du prof)** : 4.3 à 4.9. Le corrigé du TD1 dit lui-même que le grim trigger et le seuil $\delta\ge1/5$ sont un « bonus (hors programme) ». Le tournoi, le bruit et le réplicateur viennent du guide du projet 6 et du notebook (chapitre 12), pas d'un cours que j'ai lu.

### 4.1 Pourquoi répéter

**Définition.** Un **jeu répété** rejoue le même jeu (le **jeu de base**) plusieurs manches, les joueurs observant les coups passés. Les gains totaux s'additionnent (ou s'actualisent). Une **stratégie** est une règle qui donne le coup à jouer en fonction de l'historique.

**Idée (TD1 1.6).** À un coup, $(\text{Nier},\text{Nier})$ n'est pas un équilibre : avouer seul rapporte $0>-1$. Si le jeu continue, trahir aujourd'hui rapporte un gain immédiat mais expose à une punition demain : c'est l'**ombre du futur**. Tit-for-Tat (donnant-donnant) : on commence par coopérer, puis on reproduit le dernier coup de l'autre.

**Piège.** La répétition rend la coopération **possible**, pas certaine, et seulement sous conditions (horizon, patience, riposte crédible).

**Lien projet 6.** Tout le projet vit ici : le dilemme $T=5,R=3,P=1,S=0$ rejoué 200 manches.

### 4.2 Horizon fini connu : le paradoxe

**Définition.** Si le nombre de manches $n$ est connu, la dernière manche est un dilemme à un coup : $D$ domine. À l'avant-dernière, la dernière est déjà fixée, donc rien ne peut être puni ni récompensé : $D$ domine aussi. Par récurrence : **$(D,D)$ à toutes les manches**. L'induction à rebours donne le même résultat que le jeu à un coup, quel que soit $n$ (équilibre parfait en sous-jeux unique).

**Exemple chiffré.** Dilemme du TD sur 3 tours : $(\text{Avouer},\text{Avouer})$ à chaque tour, $3\times(-5)=-15$ chacun, contre $3\times(-1)=-3$ en coopérant. Dilemme du projet : sur $n$ manches, tout-$D$ rapporte $n$ et tout-$C$ rapporte $3n$ ; pour $n=200$ : $200$ contre $600$. Exemple de la fin : dix manches connues, le joueur 1 joue TFT, le joueur 2 joue TFT sauf qu'il trahit à la dernière : manches 1 à 9 $(3,3)$, manche 10 $(0,5)$ ; totaux $27$ et $32$. Le joueur 1 peut anticiper et trahir aussi à la manche 10, ce qui entraîne la manche 9, etc.

**Piège.** « TFT contre TFT = 3 par manche » reste vrai en observation mais n'est plus un équilibre à horizon connu : la coopération n'est soutenue par aucun futur. Les humains et les LLM coopèrent pourtant au début puis dégradent vers la fin (effet d'horizon). Ne pas confondre horizon **fini connu** et **indéterminé**.

**Lien projet 6.** C'est l'expérience « horizon annoncé ou non » des agents LLM.

### 4.3 Horizon infini ou indéterminé, facteur d'actualisation

**Définition.** Soit $\delta\in[0,1)$ le **facteur d'actualisation** : le gain de la manche $t$ est pondéré par $\delta^t$. Équivalent : après chaque manche, le jeu continue avec la probabilité $\delta$. Il n'y a plus de « dernier tour » certain. $\delta$ proche de $1$ signifie que l'avenir compte beaucoup (patience).

**Formules.** Flux constant $u$ : $\displaystyle\sum_{t\ge0}\delta^tu=\frac{u}{1-\delta}$. Longueur moyenne d'une partie à arrêt aléatoire : $\dfrac1{1-\delta}$ manches.

**Exemple chiffré.** $\delta=0{,}5$ : en moyenne $2$ manches ; $\delta=2/3$ : $3$ ; $\delta=0{,}9$ : $10$ ; $\delta=0{,}99$ : $100$. Coopérer toujours vaut $\dfrac{R}{1-\delta}$ : $6$ à $\delta=0{,}5$, $30$ à $\delta=0{,}9$.

**Piège.** Inverser le sens de $\delta$ : $\delta$ **grand** $=$ patience $=$ coopération plus facile. Ne pas confondre $\delta$ (jeux répétés), $\gamma$ (actualisation en apprentissage par renforcement) et $\alpha$ (taux d'apprentissage).

**Lien projet 6.** Le guide fixe 200 manches (horizon fixe) mais demande de vérifier le seuil $\delta=1/2$ avec une partie à arrêt aléatoire.

### 4.4 Les stratégies du projet

**Définitions.** Une stratégie est une fonction (mon historique, historique de l'adversaire, hasard) $\to C$ ou $D$.

| Stratégie | Règle | Propriété |
|---|---|---|
| Toujours $C$ | coopère toujours | exploitable |
| Toujours $D$ | trahit toujours | domine à une manche |
| Tit-for-Tat (TFT) | $C$ au 1er coup, puis copie le dernier coup adverse | gentil, réactif, indulgent, lisible |
| Rancunier (grim trigger) | $C$ jusqu'à la première trahison adverse, puis $D$ pour toujours | gentil, jamais indulgent |
| Pavlov (win-stay, lose-shift) | $C$ si les deux ont joué pareil au tour précédent, sinon $D$ | corrige les erreurs |
| Aléatoire | $C$ avec probabilité $1/2$ | mixte pur |
| TFT généreux | comme TFT, mais pardonne une trahison avec une probabilité (ici $1/3$) | brise l'écho |

**Exemple chiffré.** TFT contre toujours $D$ sur 200 manches : manche 1 $(C,D)=(0,5)$, puis $(D,D)=(1,1)$ : TFT fait $\dfrac{0+199}{200}=0{,}995$, toujours $D$ fait $\dfrac{5+199}{200}=1{,}02$. TFT ne gagne **jamais** directement un adversaire (au mieux égalité) ; sa moyenne est haute grâce aux $3$ obtenus contre les gentils.

**Piège.** « Gentil » (ne trahit jamais le premier) n'est pas « indulgent » (pardonne). TFT ne « pardonne » pas : il répond à $D$ par $D$, même si $D$ était une erreur.

### 4.5 Seuils d'actualisation

**Formule (rancunier).** Coopérer toujours vaut $\dfrac{R}{1-\delta}$. Trahir une fois contre un rancunier puis être puni à jamais vaut $T+\dfrac{\delta P}{1-\delta}$. La coopération est stable si
$$\frac{R}{1-\delta}\ge T+\frac{\delta P}{1-\delta}\iff \delta\ge\delta^*=\frac{T-R}{T-P}.$$
**Formule (TFT).** Contre TFT, la déviation « $D$ une fois puis retour à $C$ » vaut $T+\delta S+\dfrac{\delta^2R}{1-\delta}$ ; coopérer est meilleur si $R(1+\delta)\ge T+\delta S$, soit $\delta\ge\dfrac{T-R}{R-S}$. Le seuil de TFT est donc $\max\Big\{\dfrac{T-R}{T-P},\dfrac{T-R}{R-S}\Big\}$.

**Exemple chiffré.** Projet : rancunier $\delta^*=\dfrac{5-3}{5-1}=\dfrac12$ ; TFT : $\max\{1/2,\ 2/3\}=\dfrac23$ (calcul : $3(1+\delta)\ge5$). TD du cours : $T=0,R=-1,P=-5$ donne $\delta^*=\dfrac{0+1}{0+5}=\dfrac15$.

Valeurs contre un rancunier (coopérer toujours / trahir au tour 1) :

| $\delta$ | $R/(1-\delta)$ | $T+\delta P/(1-\delta)$ | Choix |
|---|---|---|---|
| $0{,}3$ | $4{,}29$ | $5{,}43$ | trahir |
| $0{,}4$ | $5$ | $5{,}67$ | trahir |
| $0{,}5$ | $6$ | $6$ | indifférent |
| $0{,}7$ | $10$ | $7{,}33$ | coopérer |
| $0{,}8$ | $15$ | $9$ | coopérer |

Vérification par simulation d'une partie à arrêt aléatoire (40 000 parties) : à $\delta=0{,}3$ les moyennes sont $4{,}29$ et $5{,}43$ ; à $0{,}5$, $6{,}01$ et $6{,}00$ ; à $0{,}7$, $9{,}98$ et $7{,}33$. Contre TFT à $\delta=0{,}9$ : toujours $C$ vaut $30$, toujours $D$ vaut $5+0{,}9/0{,}1=14$, « $D$ puis $C$ » vaut $5+0{,}81\times30=29{,}3$ (toujours $C$ gagne). Un calcul de meilleure réponse à TFT (deux états : prochain coup de TFT) donne « toujours $C$ » pour $\delta=0{,}67$ mais pas pour $\delta=0{,}66$ : le seuil est bien $2/3$.

**Piège.** (1) Utiliser $S$ au lieu de $P$ dans le seuil du rancunier : après la trahison le traître reçoit $P=1$, pas $S=0$. (2) Confondre les deux seuils : $1/2$ protège contre la déviation **définitive**, $2/3$ (TFT) contre « $D$ une fois puis $C$ ». (3) Plus la tentation $T-R$ est grande, plus il faut de patience. (4) Signes mélangés : le résultat doit tomber dans $[0,1]$. (5) Condition du dilemme : $T>R>P>S$ **et** $2R>T+S$ ($6>5$ ici). Avec $T=7$, $(T+S)/2=3{,}5>R=3$ : alterner $(D,C),(C,D)$ rapporterait plus que coopérer toujours.

**Lien projet 6.** Seuil $1/2$ : test unitaire du rapport. Seuil $2/3$ : question d'oral probable (« pourquoi TFT diffère du rancunier ? »).

### 4.6 Théorème de folklore (folk theorem)

**Énoncé.** Dans le jeu répété infiniment (ou à horizon indéterminé) avec $\delta$ assez proche de $1$, **tout** vecteur de gains moyens **réalisable** (dans l'enveloppe convexe des gains du jeu de base) et **individuellement rationnel** (strictement supérieur à ce que chacun peut garantir) est un gain d'équilibre. On l'appelle « de folklore » parce qu'il circulait avant sa publication ; les formes à équilibres parfaits en sous-jeux sont dues à Friedman (1971) puis Fudenberg et Maskin (1986) (de mémoire, non vérifié dans les sources).

**Formule.** Réalisables : $\operatorname{conv}\{(3,3),(0,5),(5,0),(1,1)\}$. Niveau de sécurité de chacun (le minimax) : $\underline v_i=P=1$. Condition : $v_i>1$ pour tout $i$.

**Exemple chiffré.** L'enveloppe est le quadrilatère de sommets $(3,3),(0,5),(1,1),(5,0)$, d'aire $10$. La partie individuellement rationnelle ($x\ge1$ et $y\ge1$) est le quadrilatère $(1,1),(13/3,1),(3,3),(1,13/3)$ d'aire $20/3\approx6{,}67$, soit $66{,}7\,\%$ de l'enveloppe. Vecteur $(2{,}5;2{,}5)$ (alternance $(D,C),(C,D)$) : réalisable et rationnel. Vecteur $(4;1{,}5)$ : réalisable et rationnel. Vecteur $(0{,}5;4{,}5)$ : réalisable mais pas rationnel (le joueur 1 a moins que $1$). Vecteur $(1;1)$ : le minimax, atteint par tout-$D$.

**Piège.** La théorie dit **ce qui est possible**, pas **ce qui sera choisi** : une multitude d'équilibres, dont la coopération mais aussi la trahison perpétuelle. D'où le tournoi et l'évolution (4.7 à 4.9) : « lequel apparaît en pratique ? »

**Lien projet 6.** Le gain de punition est $P=1$ (maximin, section 2.4).

### 4.7 Tournoi d'Axelrod

**Définition.** Axelrod a invité des programmes à s'affronter en round-robin dans un dilemme répété (de mémoire : un premier tournoi en 1980 avec 14 programmes plus un aléatoire, TFT de Rapoport vainqueur ; un second avec 62 participants, TFT vainqueur de nouveau ; non vérifié dans les sources). Ses constats : les bonnes stratégies sont **gentilles**, **réactives**, **indulgentes** et **lisibles**.

**Conventions du groupe (`jeux.py`).** Les historiques contiennent les coups **exécutés** (après bruit), vus par les deux joueurs ; le bruit inverse **chaque** coup de **chaque** joueur indépendamment avec la probabilité $\varepsilon$ ; tournoi sur **toutes** les paires, y compris une stratégie contre **elle-même** (score $=$ moyenne des deux côtés) ; scores $=$ gain **moyen par manche** (jamais de totaux sur des nombres de manches différents) ; score d'une stratégie $=$ moyenne de sa ligne de la matrice $M$, où $M_{ij}$ est le score de $i$ contre $j$.

**Exemple chiffré** (200 manches, 6 stratégies, 20 répétitions par paire, graine 42, $\varepsilon=0$) :

| $i$ \ $j$ | toujours $C$ | toujours $D$ | TFT | rancunier | Pavlov | aléatoire | Moyenne |
|---|---|---|---|---|---|---|---|
| toujours $C$ | 3 | 0 | 3 | 3 | 3 | 1,52 | 2,25 |
| toujours $D$ | 5 | 1 | 1,02 | 1,02 | 3 | 3,02 | 2,34 |
| TFT | 3 | 0,995 | 3 | 3 | 3 | 2,25 | 2,54 |
| rancunier | 3 | 0,995 | 3 | 3 | 3 | 2,98 | **2,66** |
| Pavlov | 3 | 0,5 | 3 | 3 | 3 | 2,19 | 2,45 |
| aléatoire | 3,99 | 0,5 | 2,27 | 0,53 | 2,29 | 2,26 | 1,97 |

Classement : rancunier $2{,}66$, TFT $2{,}54$, Pavlov $2{,}45$, toujours $D$ $2{,}34$, toujours $C$ $2{,}25$, aléatoire $1{,}97$. Les quatre gentils (C, TFT, rancunier, Pavlov) obtiennent $3$ entre eux ; toujours $D$ exploite toujours $C$ ($5$ contre $0$) et Pavlov ($3$ contre $0{,}5$) mais ne fait qu'environ $1$ contre TFT et le rancunier. Le rancunier devance TFT **uniquement** grâce à la colonne « aléatoire » ($2{,}98$ contre $2{,}25$) : sur les cinq autres colonnes leurs scores sont identiques.

**Piège.** (1) « TFT gagne toujours » est faux : le classement dépend du **champ** de stratégies et du **bruit**. Chez Axelrod le champ est plus riche ; ici l'adversaire aléatoire, exploitable sans risque par qui ne pardonne pas, avantage le rancunier. (2) Ne pas confondre « gagner chaque rencontre » (TFT ne le fait jamais) et « avoir la meilleure moyenne ». (3) Oublier la convention d'auto-jeu ; comparer des totaux.

### 4.8 Bruit : l'écho de TFT, l'effondrement du rancunier

**Définition.** Avec le bruit $\varepsilon$ (la « main qui tremble » de Selten), chaque coup voulu est inversé avec la probabilité $\varepsilon$. Une erreur isolée doit être corrigeable, sinon la coopération ne survit pas dans un monde imparfait.

**Exemple chiffré (une erreur).** Deux TFT, erreur du joueur 1 à la manche 3 : coups du joueur 1 `CCDCDCDC...`, du joueur 2 `CCCDCDCD...` : l'**écho** $(D,C),(C,D),(D,C),\dots$ ; chacun reçoit $5,0,5,0,\dots$ soit $2{,}5$ par manche (manches 3 à 20) au lieu de $3$. **Deux erreurs** (manches 3 et 8) : le système tombe en $(D,D)$ définitif, moyenne $28/18\approx1{,}56$ pour le joueur 1 sur les manches 3 à 20. Pavlov après une erreur à la manche 3 : `CCDDCCCC` contre `CCCDCCCC`, retour à $(C,C)$ en 2 manches. Rancunier : une erreur $\Rightarrow$ $(D,D)$ pour toujours.

**Auto-jeu bruité, 200 manches** (valeur exacte par chaîne de Markov ; la simulation de 200 parties redonne à $0{,}01$ près) :

| $\varepsilon$ | TFT | TFT généreux ($1/3$) | Pavlov | rancunier |
|---|---|---|---|---|
| $0$ | 3 | 3 | 3 | 3 |
| $0{,}01$ | $2{,}46$ | $2{,}97$ | $2{,}95$ | $1{,}52$ |
| $0{,}05$ | $2{,}29$ | $2{,}86$ | $2{,}78$ | $1{,}25$ |

À $\varepsilon=0{,}05$, toujours $C$ vaut $2{,}95$ et toujours $D$ $1{,}15$ contre eux-mêmes.

**Classement du tournoi selon $\varepsilon$.** $\varepsilon=0{,}01$ : rancunier $2{,}37$, toujours $D$ $2{,}35$, TFT $2{,}13$, Pavlov $2{,}13$, aléatoire $1{,}97$, toujours $C$ $1{,}79$. $\varepsilon=0{,}05$ : **toujours $D$ $2{,}37$**, rancunier $2{,}36$, Pavlov $2{,}08$, TFT $2{,}01$, aléatoire $2{,}00$, toujours $C$ $1{,}61$. Réponse à la question du guide : la domination de TFT **ne résiste pas** au bruit ; les stratégies tolérantes (TFT généreux, Pavlov) tiennent mieux **en auto-jeu**, et dans le tournoi toujours $D$ gagne dès que le bruit est assez fort (il y est insensible).

**Piège.** Appliquer le bruit à un seul joueur (faux : chaque coup de chaque joueur). Croire que TFT « pardonne » : c'est TFT généreux (pardon avec probabilité) qui casse l'écho.

### 4.9 Dynamique du réplicateur

**Définition.** Part $x_i$ de la stratégie $i$ dans la population ; score moyen de $i$ : $f_i=(Mx)_i$ ; moyenne $\bar f=x^\top Mx$. Les stratégies qui réussissent mieux que la moyenne se multiplient :
$$x_i(t+1)=x_i(t)\,\frac{f_i}{\bar f}\qquad\text{(forme continue : }\dot x_i=x_i(f_i-\bar f)\text{).}$$
Les parts restent $\ge0$ et de somme $1$ si les scores sont positifs. Les points fixes sont les états où toutes les stratégies présentes ont le même score ; les stratégies de score inférieur à la moyenne disparaissent.

**Exemple chiffré (à la main).** Dilemme à une manche, matrice $M=\begin{pmatrix}3&0\\5&1\end{pmatrix}$ (lignes $C,D$), parts $(0{,}5;0{,}5)$ : $f=(1{,}5;\,3)$, $\bar f=2{,}25$, nouvelle part de $C$ : $0{,}5\times1{,}5/2{,}25=1/3$. Ensuite $C$ : $0{,}18$, $0{,}06$, $0{,}01$, puis $0$ : la coopérante disparaît.

**Exemple chiffré (tournoi à 6, $\varepsilon=0$, parts égales $1/6$).** Après 20 générations : toujours $D\approx0{,}0006$, aléatoire $\approx0{,}0001$ ; à la limite (300 générations) : rancunier $0{,}345$, TFT $0{,}283$, Pavlov $0{,}225$, toujours $C$ $0{,}147$. Les trahisseurs disparaissent : ils profitent des naïfs, mais quand il n'en reste plus ils font $\le1$ contre les autres. Entre gentils qui se donnent tous $3$, les parts ne bougent plus (ensemble de points fixes, dérive neutre) ; toujours $C$ survit tant qu'aucun $D$ n'est présent et serait envahi par un $D$. Avec bruit, tout change : à $\varepsilon=0{,}01$ TFT conquiert la population ($\approx100\,\%$), à $\varepsilon=0{,}05$ c'est Pavlov ($99{,}8\,\%$). Sous-population $\{C,D,\text{TFT}\}$ : départ à parts égales, limite $\approx(0{,}21;\,0;\,0{,}79)$ ; départ $(0{,}1;\,0{,}8;\,0{,}1)$ : TFT atteint $100\,\%$, même avec $80\,\%$ de traîtres au départ (mécanisme : toujours $C$, exploité, disparaît d'abord ; privés de proie, les traîtres retombent à environ $1$ alors que TFT garde $3$ contre ses semblables).

**Piège.** Le tournoi donne un classement **statique** (moyenne de ligne, parts égales) ; le réplicateur fait **bouger** les parts à chaque génération. Le résultat dépend des parts initiales et de la matrice $M$ (donc du bruit).

**Lien projet 6.** Fonction `replicateur(scores, x0, generations)` ; tests : parts positives et de somme $1$.

---

## 5. Information imparfaite et incomplète : Bayes, équilibre bayésien parfait, signalisation

**Statut : Complété (hors cours du prof).** Le guide (règle n°2 et projet 3) cite Bayes comme socle du cours et donne les formules reprises ici ; je n'ai pas les supports du prof. Les gains de Bière ou Quiche sont ceux de la version standard (Cho et Kreps, 1987), pas forcément ceux du prof.

### 5.1 Quatre mots à ne pas mélanger

**Définitions.**
- **Information parfaite** : chaque joueur sait, quand il joue, tout ce qui s'est passé avant (dans l'arbre, chaque ensemble d'information est un seul nœud). Les jeux séquentiels du chapitre 3 sont à information parfaite.
- **Information imparfaite** : un joueur ne sait pas exactement où il est dans l'arbre (coups simultanés, coups cachés). Un **ensemble d'information** regroupe les nœuds qu'il ne distingue pas.
- **Information complète** : la structure du jeu (joueurs, gains) est connue de tous.
- **Information incomplète** : un joueur ignore un élément du jeu, typiquement le **type** (gains, force) d'un autre. Harsanyi ramène ce cas à un jeu à information imparfaite : la **Nature** tire d'abord les types selon une loi $P$ connue de tous, chaque joueur observe son propre type seulement.

**Piège.** Imparfaite $\ne$ incomplète. Parfaite concerne l'**historique**, complète concerne les **gains**. Un dilemme simultané est à information complète mais imparfaite.

### 5.2 Jeu bayésien et équilibre bayésien de Nash

**Définition.** Chaque joueur $i$ a un type $t_i\in\Theta_i$ tiré avec la loi commune $P(t)$. Une stratégie est une fonction $s_i:\Theta_i\to A_i$ (un coup **par type**). Un profil $s^*$ est un **équilibre bayésien de Nash** si chaque type de chaque joueur maximise son gain espéré, sachant sa croyance sur les types des autres :
$$s_i^*(t_i)\in\arg\max_{a_i}\ \sum_{t_{-i}}P(t_{-i}\mid t_i)\,\pi_i\big(a_i,s_{-i}^*(t_{-i});t\big).$$

**Exemple.** L'enchère sous pli fermé à valeurs privées est un jeu bayésien : le type est la valeur $v$, la stratégie est la fonction de mise $b(v)$ (section 7.8).

**Piège.** Oublier que la stratégie est un plan **par type** : tester la déviation d'un seul type ne suffit pas.

### 5.3 Règle de Bayes

**Formule.** Pour un type $t$ et un message observé $m$ :
$$\mu(t\mid m)=\frac{P(t)\,\sigma(m\mid t)}{\sum_{t'}P(t')\,\sigma(m\mid t')}.$$
Elle n'est définie que si le message $m$ est joué avec une probabilité positive.

**Exemple chiffré.** $P(\text{Fort})=0{,}9$. Le Fort envoie toujours Bière ; le Faible envoie Bière avec probabilité $1/2$. Alors $P(\text{Bière})=0{,}9+0{,}1\times0{,}5=19/20$ et $\mu(\text{Fort}\mid\text{Bière})=0{,}9/(19/20)=18/19\approx0{,}947$. $P(\text{Quiche})=1/20$ et $\mu(\text{Faible}\mid\text{Quiche})=1$ : voir Quiche prouve la faiblesse. Test médical : prévalence $1\,\%$, sensibilité $95\,\%$, faux positifs $5\,\%$, donc $P(\text{malade}\mid+)=\dfrac{0{,}01\times0{,}95}{0{,}01\times0{,}95+0{,}99\times0{,}05}=\dfrac{19}{118}\approx16\,\%$ (et non $95\,\%$).

**Piège.** (1) Diviser par zéro sur un message hors équilibre : la règle ne s'y applique pas. (2) Confondre $P(m\mid t)$ et $P(t\mid m)$.

### 5.4 Équilibre bayésien parfait (EBP)

**Définition.** Un EBP est un profil de stratégies **avec** un système de croyances tel que : (1) à chaque ensemble d'information, l'action de celui qui joue est une **meilleure réponse à ses croyances** (rationalité séquentielle) ; (2) les croyances viennent de la règle de Bayes **sur le chemin d'équilibre** et sont **libres hors équilibre** (c'est là que se cachent les menaces et les subtilités).

**Pourquoi.** L'EPSJ du chapitre 3 suppose l'information parfaite. Dès qu'un joueur doit agir sans savoir où il est, il lui faut une croyance : l'EBP généralise l'EPSJ aux jeux à information imparfaite ou incomplète. Il élimine, comme l'EPSJ, les menaces non crédibles.

**Piège.** Dire que les croyances hors équilibre sont « fixées par Bayes » : faux, elles sont libres (on les explore sur une grille, comme le demande le guide). Ne tester que la déviation d'un seul type.

### 5.5 Signalisation : Bière ou Quiche

**Le jeu.** Un émetteur de type **Fort** (probabilité $P_F$) ou **Faible** ($1-P_F$) choisit un petit-déjeuner : Bière ($B$) ou Quiche ($Q$). Le récepteur observe le petit-déjeuner, pas le type, et choisit *Duel* ($D$) ou *Pas de duel* ($N$). Gains standard : l'émetteur gagne $1$ s'il prend son petit-déjeuner préféré (Fort : Bière ; Faible : Quiche) plus $2$ si le récepteur ne se bat pas ; le récepteur gagne $1$ s'il se bat contre un Faible ou ne se bat pas contre un Fort, $0$ sinon.

**Croyance critique.** Après un message avec la croyance $p=\mu(\text{Faible}\mid m)$ : $E[D]=p$, $E[N]=1-p$. Le récepteur se bat si $p>1/2$ : $p=0{,}2$ donne $N$, $p=0{,}5$ indifférent, $p=0{,}51$ et $p=0{,}6$ donnent $D$.

**Équilibres en stratégies pures, $P_F=0{,}9$** (énumération exhaustive des profils et des croyances hors équilibre sur une grille de pas $0{,}1$) : exactement deux, tous **poolants** (les deux types envoient le même message).
- **Poolant Bière** : Fort et Faible prennent Bière ; récepteur : $N$ après Bière (croyance $0{,}9$ Fort, $E[N]=0{,}9>E[D]=0{,}1$), $D$ après Quiche, **valide si la croyance hors équilibre $\mu(\text{Faible}\mid Q)\ge0{,}5$**. Gains : Fort $3$, Faible $2$. Déviation vers Quiche : le Fort aurait $0$ (Quiche puis Duel), le Faible aurait $1$ : aucune ne rapporte plus que $3$ et $2$. Avec $\mu(\text{Faible}\mid Q)=0{,}6$ l'équilibre est valide, avec $0{,}2$ il ne l'est pas (le récepteur ne se bat plus, le Faible gagnerait $1+2=3>2$ en déviant) : c'est le résultat annoncé par le guide.
- **Poolant Quiche** : tous prennent Quiche, $N$ après Quiche, $D$ après Bière si $\mu(\text{Faible}\mid B)\ge0{,}5$. Gains : Fort $2$, Faible $3$.
- **Aucun séparateur** : si Fort joue $B$ et Faible joue $Q$, le récepteur répond $N$ après $B$ et $D$ après $Q$, mais le Faible gagnerait $0+2=2>1$ en imitant le Fort.

**Critère intuitif.** Le poolant Quiche est écarté : le Fort a $2$ à l'équilibre et pourrait avoir jusqu'à $3$ en déviant vers Bière ; le Faible a $3$ à l'équilibre et au plus $2$ en déviant, donc **seul** un Fort peut vouloir envoyer Bière. Le récepteur devrait croire à un Fort après Bière, ne pas se battre, et le Fort dévierait. Le poolant Bière survit.

**Pour $P_F=0{,}3$** : avec ces gains je ne trouve aucun EBP en stratégies pures. Poolant Bière : le récepteur se battrait après Bière sur la seule croyance a priori ($0{,}7$ de Faible), le Faible aurait $0$ et dévierait vers Quiche ($1$). Poolant Quiche : le récepteur se battrait aussi après Quiche, le Fort aurait $0$ et gagnerait au moins $1$ en prenant Bière. Séparateur : impossible comme ci-dessus. Le guide cite un cas $0{,}3$ qui n'est donc pas reproduit ici (autres gains ?).

**Piège.** Croire qu'un EBP est unique ou que le message « révèle » toujours le type : en poolant il ne révèle rien. Une croyance hors équilibre arbitraire peut soutenir n'importe quel poolant ; le critère intuitif et d'autres raffinements servent à trier.

### 5.6 Lien avec le projet 6

**Lien projet 6.** (1) Le type de l'adversaire est inconnu : jouer contre un LLM ou contre une stratégie inconnue est un jeu à information incomplète. (2) **Réputation** : si un adversaire est un type « TFT » avec probabilité a priori $0{,}2$ et qu'un type rationnel imiterait la coopération avec probabilité $1/2$ à chaque tour, la croyance après $k$ coopérations consécutives est $\mu_k=\dfrac{0{,}2}{0{,}2+0{,}8\times0{,}5^k}$ : $0{,}2$ ; $0{,}33$ ; $0{,}5$ ; $0{,}67$ ; $0{,}8$ ; $0{,}89$ pour $k=0,\dots,5$. Coopérer en début de partie « construit une réputation » même quand la théorie prévoit la trahison finale (idée des modèles de réputation à la Kreps, Milgrom, Roberts et Wilson, de mémoire). (3) Le **bruit** est une observation imparfaite : on ne sait pas si une trahison était voulue ou accidentelle.

---

## 6. Jeux coopératifs : fonction caractéristique, cœur, valeur de Shapley

**Statut : Complété (hors cours du prof).** Le chapitre 1 ne fait que définir « coopératif » (accords contraignants, coalitions). Le guide (projet 4) donne les formules du cœur et de Shapley et un jeu du cours ($v(\{1,2\})=v(\{1,3\})=60$, $v(\{2,3\})=0$, $v(N)=90$, Shapley $(50,20,20)$, $(0,45,45)$ hors du cœur), repris ci-dessous ; je n'ai pas le support du prof.

### 6.1 Fonction caractéristique

**Définition.** Dans un jeu coopératif à utilité transférable, les joueurs $N=\{1,\dots,n\}$ peuvent former des **coalitions** $S\subseteq N$. La **fonction caractéristique** $v$ donne à chaque coalition le gain qu'elle peut s'assurer seule, avec $v(\varnothing)=0$. Le jeu est **superadditif** si $v(S\cup T)\ge v(S)+v(T)$ pour $S,T$ disjointes : la grande coalition $N$ se forme. Il reste à **partager** $v(N)$. Un partage $x=(x_1,\dots,x_n)$ est **efficace** si $\sum_ix_i=v(N)$.

**Exemple chiffré.** Trois joueurs, $v(\{i\})=0$, $v(\{1,2\})=v(\{1,3\})=60$, $v(\{2,3\})=0$, $v(N)=90$. Le joueur 1 est indispensable aux petites coalitions rentables.

**Piège.** Oublier $v(\varnothing)=0$ ; confondre jeu de gains (on maximise) et jeu de coûts (on minimise, les inégalités du cœur s'inversent).

### 6.2 Le cœur

**Définition.** Le **cœur** est l'ensemble des partages efficaces qu'aucune coalition ne peut rejeter :
$$\text{Cœur}(v)=\Big\{x\in\mathbb{R}^n:\ \sum_{i\in N}x_i=v(N),\ \ \sum_{i\in S}x_i\ge v(S)\ \ \forall S\subseteq N\Big\}.$$
C'est un système linéaire : un point s'obtient par programmation linéaire (`linprog`) ; si le système est infaisable, le cœur est **vide**.

**Exemple chiffré.** Jeu ci-dessus. Les contraintes sont $x_1+x_2\ge60$, $x_1+x_3\ge60$, $x_2+x_3\ge0$, $x_i\ge0$, $\sum x=90$. On en tire $x_1\in[30,90]$, $x_2\in[0,30]$, $x_3\in[0,30]$ (bornes calculées par programmation linéaire). Le cœur n'est pas vide : $(90,0,0)$ y est. Le partage $(0,45,45)$ n'y est pas : la coalition $\{1,2\}$ reçoit $0+45=45<60$ et la coalition $\{1,3\}$ aussi, elles se désolidarisent.

**Cœur vide.** Vote à majorité simple à 3 joueurs ($v(S)=1$ si $|S|\ge2$) : le système est infaisable, cœur vide (chaque paire peut réclamer toute la valeur). Le cœur n'est donc **pas** toujours non vide, et il peut contenir beaucoup de points (injuste ou non) : il ne choisit pas.

**Piège.** Croire que le cœur est toujours non vide ; distinguer cœur vide d'un échec du solveur (regarder le statut de `linprog`) ; utiliser des inégalités de jeu de gains pour un jeu de coûts.

### 6.3 Valeur de Shapley

**Définition.** La valeur de Shapley donne à chaque joueur sa contribution marginale **moyenne** sur tous les ordres d'arrivée dans la grande coalition :
$$\varphi_i(v)=\sum_{S\subseteq N\setminus\{i\}}\frac{|S|!\,(n-|S|-1)!}{n!}\Big[v(S\cup\{i\})-v(S)\Big]=\frac1{n!}\sum_{\text{ordres}}\Big[v(S_i^{\text{avant}}\cup\{i\})-v(S_i^{\text{avant}})\Big].$$
C'est l'**unique** valeur qui vérifie quatre axiomes : **efficacité** ($\sum\varphi_i=v(N)$), **symétrie** (deux joueurs interchangeables reçoivent autant), **joueur nul** (contribution toujours nulle $\Rightarrow$ part nulle), **additivité** ($\varphi(v+w)=\varphi(v)+\varphi(w)$).

**Exemple chiffré.** Jeu du 6.1, six ordres, contributions marginales $(1,2,3)$ :

| Ordre | Joueur 1 | Joueur 2 | Joueur 3 |
|---|---|---|---|
| 1, 2, 3 | 0 | 60 | 30 |
| 1, 3, 2 | 0 | 30 | 60 |
| 2, 1, 3 | 60 | 0 | 30 |
| 2, 3, 1 | 90 | 0 | 0 |
| 3, 1, 2 | 60 | 30 | 0 |
| 3, 2, 1 | 90 | 0 | 0 |
| Moyenne | **50** | **20** | **20** |

$\varphi=(50,20,20)$, de somme $90$ ; ce partage est dans le cœur ($50+20=70\ge60$). Jeu des gants (deux gants gauches 1 et 2, un gant droit 3, $v(S)=$ nombre de paires) : $\varphi=(1/6,1/6,2/3)$ ; son cœur est le seul point $(0,0,1)$ (le gant rare capte tout), preuve que Shapley et cœur peuvent différer. Jeu de l'aéroport (coûts de piste $1,2,3$, $v(S)=\max$ des coûts de $S$) : $\varphi=(1/3,\,5/6,\,11/6)$, de somme $3$ : chacun paie sa tranche de piste partagée avec ceux qui l'utilisent.

**Coût du calcul.** $n!$ ordres : $10!=3\,628\,800$ ; $20!\approx2{,}43\times10^{18}$. Le calcul par coalitions est en $2^n$ ($2^{20}=1\,048\,576$), raisonnable jusqu'à $n\approx20$. Au delà : **Monte-Carlo** sur des permutations tirées au hasard, erreur en $1/\sqrt m$. Sur le jeu du 6.1 : $m=10$ permutations donnent $(60;15;15)$, $m=100$ donnent $(45;21{,}6;23{,}4)$, $m=1\,000$ donnent $(51;19{,}56;19{,}44)$, $m=10\,000$ donnent $(50{,}42;19{,}69;19{,}9)$.

**Piège.** Shapley est **une** valeur, pas le seul partage raisonnable ; elle n'est pas forcément dans le cœur. Confondre contribution marginale et part du gain individuel $v(\{i\})$.

### 6.4 Vote pondéré et indice de Shapley-Shubik

**Définition.** Un vote pondéré $[q;w_1,\dots,w_n]$ est le jeu $v(S)=1$ si $\sum_{i\in S}w_i\ge q$, $0$ sinon. L'**indice de Shapley-Shubik** est la valeur de Shapley de ce jeu : la fraction des ordres d'arrivée où le joueur est **pivot**, celui qui fait atteindre le quota.

**Exemple chiffré.** $[51;49,48,3]$ : deux joueurs quelconques font déjà au moins $52$ ; le pivot est toujours le 2e arrivé ; chacun occupe la 2e place dans $2$ ordres sur $6$ : indices $(1/3,1/3,1/3)$. Le petit parti à $3$ sièges a **autant de pouvoir** que les deux grands. $[51;40,30,20,10]$ : $(5/12,1/4,1/4,1/12)$. $[51;60,20,20]$ : $(1,0,0)$ (le grand parti est dictateur, les autres joueurs nuls).

**Piège.** Confondre **poids** (sièges) et **pouvoir** (capacité de faire basculer un vote).

**Lien projet 6.** Le projet 6 n'utilise pas les jeux coopératifs. Un seul rapport : dans le tournoi, le score d'une stratégie dépend des adversaires présents, comme la contribution marginale d'un joueur dépend de la coalition ; et dans un système multi-agents, un contrat permet de dépasser le dilemme que seule la répétition résout autrement (section 7.6).

---

## 7. Métaheuristiques et systèmes multi-agents

**Statut : Complété (hors cours du prof).** Le notebook (chapitres 9 à 11) le dit explicitement : « le chapitre 1 s'arrête aux jeux », sources Russell et Norvig, Wooldridge, Shoham et Leyton-Brown. Le guide cite PSO, ACO, boids dans le code du cours, avec les formules PSO et ACO reprises en 7.3 et 7.4 ; je n'ai pas les supports. Les simulations de 7.2 à 7.5 sont **mes implémentations** (graines fixées), pas le code du prof.

### 7.1 Agent, environnement, architectures

**Définitions.** Un **agent** perçoit son environnement par des capteurs et agit par des actionneurs. **Fonction agent** $f:\text{historique des perceptions}\to\text{action}$ (idée mathématique) ; **programme agent** : son code. Un **agent rationnel** choisit l'action qui maximise la valeur **attendue** de la mesure de performance, vu ses perceptions. Dictionnaire avec les jeux : agent $=$ joueur, fonction agent $=$ stratégie, performance $=$ gain. **PEAS** spécifie un agent : Performance, Environnement, Actionneurs, Senseurs. Propriétés d'un environnement : observable ou partiellement, déterministe ou stochastique, épisodique ou séquentiel, statique ou dynamique, discret ou continu, mono-agent ou multi-agent (compétitif ou coopératif). Dans un système multi-agents, les autres agents font partie de l'environnement et **s'adaptent** : il n'est plus stationnaire.

**Architectures.** Réflexe simple (règle condition $\to$ action, sans mémoire), à modèle (état interne), à but (recherche, planification), à utilité (maximise l'utilité espérée : l'agent des jeux), apprenant. Architectures en couches : **subsumption** (Brooks, les couches basses réactives l'emportent en urgence), **BDI** (croyances, désirs, intentions), **hybride** (couche réactive + couche délibérative).

**Exemple chiffré.** Aspirateur à deux cases, performance $=$ cases propres moins $0{,}5$ par déplacement, 10 pas, moyenne sur les 8 états initiaux : agent réflexe (« si sale aspirer, sinon bouger ») $14{,}75$ ; agent à modèle (il retient les cases propres et s'arrête) $18{,}75$. Pour le départ « tout propre » : réflexe $10\times2-10\times0{,}5=15$, modèle $20-0{,}5=19{,}5$. L'écart vient du coût de déplacement, pas de la propreté.

**Piège.** Rationnel $\ne$ omniscient. Fonction agent $\ne$ programme agent. Échecs $\ne$ mono-agent : l'adversaire est un agent.

**Lien projet 6.** Tit-for-Tat est une fonction agent dont la perception est l'historique adverse : agent réactif à mémoire. Un agent LLM est un agent dont la fonction agent est un modèle de langage (section 8).

### 7.2 Algorithme génétique

**Définition.** Population de solutions (chromosomes). À chaque génération : **sélection** (les meilleures se reproduisent plus : roue proportionnelle ou tournoi), **croisement** (on mélange deux parents), **mutation** (on inverse au hasard quelques gènes), **élitisme** (on garde le meilleur). Le but est de maximiser une **fitness**. Pour le voyageur de commerce, croisement d'ordre (OX) et mutation par échange (guide, projet 5), car il faut rester une permutation.

**Formules.** Sélection proportionnelle : $P(i)=f_i/\sum_jf_j$. Mutation par gène avec la probabilité $p_m\approx1/L$ ($L$ longueur du chromosome).

**Exemple chiffré.** Fitness $(4,2,3,1)$ : probabilités $(0{,}4;\,0{,}2;\,0{,}3;\,0{,}1)$. Croisement à un point après le 3e gène de $11010010$ et $00111100$ : enfants $11011100$ et $00110010$ (nombre de 1 : $5$ et $3$, parents $4$ et $4$). Croisement d'ordre OX : parents $[1..8]$ et $[3,7,5,1,6,8,2,4]$, segment des positions $2$ à $4$ pris au premier parent $[3,4,5]$, le reste complété dans l'ordre du second : enfant $[7,1,3,4,5,6,8,2]$, une permutation valide. Expérience OneMax (maximiser le nombre de 1 d'un mot de 40 bits, population 30, tournoi de taille 3, croisement $0{,}9$, mutation $1/40$, un élite) : à la génération 0 meilleur $25$, moyenne $20{,}03$ ; génération 10 : meilleur $35$, moyenne $33{,}57$ ; il faut en moyenne $23{,}25$ générations pour atteindre $40/40$ sur 20 graines (extrêmes $15$ et $30$). Sans mutation la population se fige : meilleur final moyen $34{,}4$ sur 100 générations.

**Piège.** Comparer deux métaheuristiques sur une seule graine ou avec des budgets d'évaluations différents. La mutation n'est pas un luxe : elle restaure la diversité.

### 7.3 Optimisation par essaim de particules (PSO)

**Définition.** Chaque particule a une position $x$, une vitesse $v$, sa meilleure position personnelle $p_{\text{best}}$ ; l'essaim a la meilleure position globale $g_{\text{best}}$.
$$v\leftarrow w\,v+c_1r_1\,(p_{\text{best}}-x)+c_2r_2\,(g_{\text{best}}-x),\qquad x\leftarrow x+v,$$
avec $w$ l'inertie, $c_1,c_2$ les coefficients cognitif et social, $r_1,r_2$ aléatoires dans $[0,1]$ (formule du guide, projet 5).

**Exemple chiffré (à la main).** $x=4$, $v=1$, $p_{\text{best}}=3$, $g_{\text{best}}=0$, $w=0{,}7$, $c_1=c_2=1{,}5$, $r_1=0{,}4$, $r_2=0{,}6$ : $v'=0{,}7+1{,}5\times0{,}4\times(3-4)+1{,}5\times0{,}6\times(0-4)=0{,}7-0{,}6-3{,}6=-3{,}5$ et $x'=4-3{,}5=0{,}5$.

**Rôle de l'inertie.** Sphère en dimension 2, 20 particules, 100 itérations, médiane sur 10 graines : meilleure valeur $4\times10^{-31}$ pour $w=0{,}4$, $1{,}9\times10^{-13}$ pour $w=0{,}7$, $2{,}5\times10^{-4}$ pour $w=0{,}9$, $5{,}2\times10^{-2}$ pour $w=1{,}2$. Pour $w=1{,}2$ les positions finales atteignent en médiane $1{,}5\times10^{8}$ (l'essaim **diverge**) contre $8{,}5\times10^{-3}$ pour $w=0{,}7$ (il converge) : cohérent avec le guide, « $w=0{,}7$ converge, $w=1{,}2$ diverge ». Rastrigin en dimension 10 (optimum $0$, meilleure valeur initiale médiane $\approx120$), 30 particules, 300 itérations ($9\,030$ évaluations), $w=0{,}7$ : valeur finale médiane $6{,}47$, meilleure $2{,}98$ sur 10 graines : bonne descente mais pas l'optimum global (Rastrigin a une multitude de minima locaux).

**Piège.** Un $w$ trop grand fait diverger ; on borne les positions et on limite les vitesses. Ne pas conclure à partir d'une graine.

### 7.4 Optimisation par colonies de fourmis (ACO)

**Définition.** Des fourmis construisent des tours (voyageur de commerce) ; le choix d'une ville dépend de la phéromone $\tau_{ij}$ et de la visibilité $\eta_{ij}=1/d_{ij}$ :
$$p_{ij}=\frac{\tau_{ij}^{\alpha}\,\eta_{ij}^{\beta}}{\sum_{k\ \text{libre}}\tau_{ik}^{\alpha}\,\eta_{ik}^{\beta}},\qquad \tau_{ij}\leftarrow(1-\rho)\,\tau_{ij}+\sum_{\text{fourmis}}\frac QL\ \ (\text{si l'arête est dans le tour de longueur }L).$$
$\rho$ est le taux d'évaporation ; les arêtes des courts tours reçoivent plus (formule du guide).

**Exemple chiffré.** Cinq villes, distances $d_{01}=2,\,d_{02}=9,\,d_{03}=10,\,d_{04}=7$, $\tau=1$, $\alpha=1$, $\beta=2$ : probabilités de partir de la ville 0 vers $1,2,3,4$ : $(0{,}854;\,0{,}042;\,0{,}034;\,0{,}070)$. Mise à jour avec $\rho=0{,}5$, $Q=1$ après un tour 0-1-4-2-3 de longueur $2+3+5+8+10=28$ : dépôt $Q/L=1/28=0{,}0357$ ; $\tau_{01}=0{,}5+0{,}0357=0{,}536$ (arête du tour), $\tau_{02}=0{,}5$ (non utilisée). Sur ces cinq villes l'optimum vaut $26$ (énumération) et l'ACO le trouve sur 20 graines sur 20. Vingt villes aléatoires : tour aléatoire moyen $11{,}38$, plus proche voisin $4{,}43$, ACO $4{,}07$.

**Piège.** Confondre $\alpha$ (poids de la phéromone), $\beta$ (poids de la visibilité), $\rho$ (évaporation, **pas** une probabilité de choix).

### 7.5 Boids (comportements collectifs émergents)

**Définition.** Reynolds (1986) : chaque oiseau suit trois règles locales sur ses voisins : **séparation** (ne pas heurter), **alignement** (prendre la direction moyenne), **cohésion** (aller vers le centre). Aucun chef : le vol collectif **émerge**.

**Exemple chiffré** (mon implémentation : 40 oiseaux sur un tore $10\times10$, vitesse de norme constante, rayon de voisinage $2$, 300 pas). Mesure : polarisation $=\|\text{moyenne des vitesses}\|/v_{\max}$ (0 : désordre, 1 : tous alignés). Départ aléatoire : $0{,}23$ en moyenne sur 5 graines. Poids d'alignement $0$ : $0{,}16$ à la fin (pas d'ordre) ; poids $0{,}1$, $0{,}3$ ou $1$ : $1{,}0$ sur les 5 graines. Pour la graine 0 avec le poids $0{,}3$ : $0{,}36$ au pas 0, $0{,}91$ au pas 25, $0{,}98$ au pas 50, $1{,}0$ au pas 100.

**Piège.** Dire que « le chef décide » : c'est de l'auto-organisation. Le résultat dépend de la normalisation de la vitesse (dans une première version à vitesse bornée sans renormalisation, la polarisation restait faible : détail d'implémentation à tester).

**Lien projet 6.** Les stratégies à voisinage ressemblent à TFT : une règle locale simple produit un comportement collectif (coopération qui s'étend ou s'effondre).

### 7.6 Coordination

**Définition.** Quand un jeu a plusieurs équilibres (bataille des sexes, chasse au cerf), la théorie ne dit pas lequel sera joué. Des agents doivent s'accorder sans maître. **Coordination pure** (conduire à droite ou à gauche) : gains $(1,1)$ si les choix sont égaux, $(0,0)$ sinon ; deux équilibres purs équivalents et un mixte $(1/2,1/2)$ de gain $1/2$ (pire que $1$). Mécanismes : **convention** préétablie, **point focal** (Schelling : option saillante), communication gratuite (*cheap talk*), rôles imposés, signal commun, **leader** (Stackelberg). **Anti-coordination** (faucon-colombe, route) : on veut choisir **différemment**.

**Exemple chiffré.** Chasse au cerf : le cerf est rationnel si $10q\ge5$, soit $q\ge1/2$ (croyance que l'autre chasse le cerf). Faucon-colombe $V=4$, $C=6$ : $P(F)=2/3$, gain $2/3$ (section 2.2).

**Piège.** Coordination (aligner les choix) $\ne$ coopération (renoncer à un gain individuel : dilemme).

### 7.7 Négociation : Contract Net et offres alternées de Rubinstein

**Contract Net.** Un gestionnaire annonce une tâche, les contractants répondent par une offre (leur coût), il attribue au meilleur : simple, décentralisé, mais **glouton**. Coûts (agent $\times$ tâche) : $\begin{pmatrix}6&8&4\\7&9&2\\4&1&4\end{pmatrix}$. Glouton dans l'ordre T1, T2, T3 : T1 $\to$ agent 3 ($4$), T2 $\to$ agent 1 ($8$), T3 $\to$ agent 2 ($2$) : total $14$. Optimum (confirmé par l'algorithme hongrois) : agent 1 $\to$ T1 ($6$), agent 3 $\to$ T2 ($1$), agent 2 $\to$ T3 ($2$) : total $9$.

**Offres alternées (Rubinstein).** Deux agents se partagent une valeur $1$ ; à chaque tour un proposant fait une offre, l'autre accepte ou refuse puis devient proposant ; le temps coûte : facteurs $\delta_1,\delta_2<1$. L'EPSJ (induction à rebours) est un accord **immédiat**, la part du premier proposant valant
$$\frac{1-\delta_2}{1-\delta_1\delta_2}\qquad(\text{symétrique : }\tfrac1{1+\delta}).$$
Exemple : $\delta_1=0{,}9$, $\delta_2=0{,}8$ : $0{,}2/0{,}28=5/7\approx0{,}714$ pour J1 et $2/7$ pour J2. Même patience $\delta=0{,}9$ : $10/19\approx0{,}526$ (petit avantage du premier). $\delta=0{,}5$ : $2/3$ ; $\delta=0{,}99$ : $0{,}5025$. À horizon fini ($T$ tours, $\delta_1=\delta_2=0{,}9$) la part du premier proposant vaut $1$ ($T=1$, ultimatum), $0{,}10$ ($T=2$ : le dernier proposant a le pouvoir), $0{,}91$ ($T=3$), $0{,}181$ ($T=4$), $0{,}837$ ($T=5$), $0{,}343$ ($T=10$), $0{,}504$ ($T=30$) : elle oscille et converge vers $10/19$.

**Piège.** Le pouvoir vient de la **patience** ($\delta$ grand) et de l'ordre de parole ; ne pas lire la formule avec les $\delta$ inversés. Contract Net : glouton $\ne$ optimal ($14$ contre $9$).

### 7.8 Enchères

**Définitions.** Quatre formats : **anglaise** (montante, ouverte), **hollandaise** (descendante), sous pli fermé au **premier prix** (le gagnant paie sa mise), sous pli fermé au **second prix** ou **Vickrey** (le gagnant paie la deuxième mise). Valeurs privées : chaque enchérisseur connaît sa valeur $v$. Équivalences : anglaise $\approx$ Vickrey, hollandaise $\approx$ premier prix.

**Vickrey : dire sa vraie valeur est (faiblement) dominant.** Soit $m$ la meilleure mise des autres. Miser $v$ gagne exactement quand $v>m$, c'est-à-dire quand le gain $v-m$ est positif ; miser plus ne fait qu'ajouter des cas où $v-m<0$, miser moins en fait perdre où $v-m>0$. Vérification exhaustive sur les entiers de $0$ à $10$ : vraie. Exemple : valeurs $70,60,50$ ; si tous misent leur valeur, le $70$ gagne et paie $60$ (gain $10$).

**Premier prix : on sous-enchérit.** Miser $v$ donne un gain nul. Avec $n$ valeurs uniformes sur $[0,1]$, mise d'équilibre $b(v)=\dfrac{n-1}{n}v$ (formule du guide). Exemple : le $70$ qui mise $60{,}01$ gagne $9{,}99$ ; en misant $65$ il gagne $5$. Pour $n=3$ : mise $2v/3$. Gain espéré selon le facteur de mise $k$ (autres à $2/3$ de leur valeur) : $k=0{,}4$ : $0{,}054$ ; $0{,}5$ : $0{,}070$ ; $0{,}6$ : $0{,}081$ ; $2/3$ : **$0{,}083$** ($=1/12$, maximum) ; $0{,}75$ : $0{,}076$ ; $0{,}9$ : $0{,}036$ ; $1$ : $0$.

**Équivalence des revenus.** Valeurs privées indépendantes : les quatre formats rapportent le **même revenu espéré** au vendeur, $\dfrac{n-1}{n+1}$ : $1/3$ ($n=2$), $1/2$ ($n=3$), $2/3$ ($n=5$), $0{,}818$ ($n=10$). Simulation $n=3$ (400 000 tirages) : premier prix $0{,}5002$, second prix $0{,}5002$.

**Piège.** « Au second prix on paie moins, donc le vendeur gagne moins » : faux, on mise **plus**. « Au premier prix on mise sa valeur » : faux (gain nul).

**Lien projet 6.** Vickrey est un exemple de **conception de mécanisme** : on choisit la règle de paiement pour que dire la vérité soit dominant, comme les gains du dilemme sont choisis pour que $D$ le soit, mais ici l'équilibre est bon.

### 7.9 Vote

**Définitions.** **Pluralité** : gagne le plus souvent classé 1er. **Borda** : avec $m$ candidats, $m-1$ points au 1er, ..., $0$ au dernier. **Deux tours** : on départage les deux premiers. **Condorcet** : le candidat qui bat chacun des autres en duel (s'il existe).

**Exemple chiffré** (100 votants : 40 votent $A\succ B\succ C$, 35 votent $B\succ C\succ A$, 25 votent $C\succ B\succ A$). Pluralité : $A$ ($40$, $35$, $25$). Borda : $A=80$, $B=135$, $C=85$ : $B$. Condorcet : $B$ bat $A$ ($60$ à $40$) et $C$ ($75$ à $25$) : $B$. Deux tours : $A$ contre $B$, $B$ gagne $60$ à $40$. Le gagnant à la pluralité n'est **pas** le gagnant de Condorcet.

**Paradoxe de Condorcet.** Trois votants $A\succ B\succ C$, $B\succ C\succ A$, $C\succ A\succ B$ : $A$ bat $B$, $B$ bat $C$, $C$ bat $A$, chacun $2$ à $1$ : préférence collective **cyclique**. Avec 3 candidats et 101 votants tirés uniformément (« culture impartiale »), la fréquence simulée de cycle est d'environ $8{,}8\,\%$ (20 000 tirages).

**Théorèmes.** **Arrow** : aucune règle ne satisfait un petit jeu d'axiomes raisonnables. **Gibbard-Satterthwaite** : toute règle non dictatoriale à au moins 3 candidats est **manipulable**. Exemple : cinq votants $C\succ A\succ B$, $A\succ B\succ C$, $B\succ C\succ A$, $B\succ A\succ C$, $C\succ A\succ B$, Borda avec départage alphabétique : scores $A=B=C=5$, gagnant $A$ (le pire pour le 3e votant). Si le 3e vote $C\succ B\succ A$ : $A=5$, $B=4$, $C=6$, $C$ gagne, qu'il préfère à $A$.

**Piège.** Un vote sincère n'est pas toujours la meilleure stratégie. Aucune règle d'agrégation n'est parfaite.

### 7.10 Apprentissage multi-agent

**Pourquoi.** Nash suppose que chacun connaît les gains et prévoit les choix des autres. En pratique on **apprend en jouant**. Le problème : les autres apprennent aussi, donc l'environnement de chacun **n'est plus stationnaire** et les garanties de convergence du Q-learning tombent.

**Q-learning.** $Q(s,a)\leftarrow Q(s,a)+\alpha\,[\,r+\gamma\max_{a'}Q(s',a')-Q(s,a)\,]$ ($\alpha$ taux d'apprentissage, $\gamma$ actualisation, $\varepsilon$ exploration). Exemples : $Q=0$, $\alpha=0{,}5$, $r=5$, $\max Q'=0$, $\gamma=0{,}9$ donne $2{,}5$ ; $Q=20$, $\alpha=0{,}1$, $\gamma=0{,}9$, $r=3$, $\max Q'=30$ donne $20+0{,}1(3+27-20)=21$.

**Jeu fictif.** Chaque joueur joue la meilleure réponse aux **fréquences passées** de l'autre. Pile ou face (J1 veut les coups égaux, J2 différents), tour 1 : Pile / Face ; les huit premiers tours : J1 P, F, F, F, P, P, P, P ; J2 F, F, P, P, P, P, P, F ; fréquences de Pile $5/8$ chacun, qui tendent vers $1/2$ (équilibre mixte) alors que chaque coup est **pur** : ce sont les **fréquences** qui convergent, pas les coups.

**Regret matching.** Regret cumulé $R_T(a)=\sum_t[u(a,b_t)-u(a_t,b_t)]$ ; on joue $a$ avec la probabilité proportionnelle à $\max(R_T(a),0)$. Pierre-feuille-ciseaux, J1 joue Pierre contre Feuille : regrets $(0,1,2)$, probabilités du tour suivant $(0,1/3,2/3)$. Si tous les regrets sont $\le0$ : loi uniforme. La fréquence jointe converge vers l'ensemble des équilibres **corrélés** (vers Nash en somme nulle).

**Meilleure réponse à TFT.** Contre un adversaire fixe (TFT), le Q-learning à deux états (prochain coup de TFT) converge : à $\gamma=0{,}9$, $Q(C,C)=30{,}0$, $Q(C,D)=29{,}3$, $Q(D,C)=27{,}0$, $Q(D,D)=24{,}7$ et il coopère $95\,\%$ du temps ; à $\gamma=0{,}5$ (sous le seuil $2/3$) il alterne ($50\,\%$). Sans mémoire, deux apprenants convergent vers $(D,D)$ (dominance).

**Piège.** « Le jeu fictif converge donc ils jouent le mixte à chaque tour » : faux. « Le Q-learning converge toujours même à plusieurs » : faux (non stationnarité). « Le regret matching mène à Nash » : faux en général, à un équilibre corrélé. Confondre $\gamma$, $\alpha$, $\varepsilon$, $\delta$.

**Lien projet 6.** Les agents LLM du projet sont des agents à mémoire (historique dans le prompt) : leur comportement se compare à TFT, au rancunier et à l'apprenant. Convergence vers $(D,D)$, vers la coopération ou vers un cycle : à mesurer, pas à supposer.

---

## 8. Agents LangChain : outil `@tool`, boucle agent, Ollama, risques

**Statut : Complété (hors cours du prof).** Sources : guide des projets (règles d'or n°2, 3, 5, annexe B, tableau des phases), notebook (chapitre 9 §7 et chapitre 12), et mes essais. Je n'ai ni `agent_tj_sma.py` (« 10 outils ») ni le support du prof sur LangChain. **Vérifié ici** : le comportement du décorateur `@tool` avec `langchain_core` 1.6.3, les plafonds, la validation de types, la boucle (avec un faux modèle). **Non vérifié** : `create_agent`, `langchain-ollama`, Ollama lui-même (`langchain` et `langchain_ollama` ne sont pas installés dans l'environnement de rédaction, aucun modèle local n'a été lancé).

### 8.1 La boucle agent

**Définition.** Un agent LLM avec outils répète : (1) lire la question et l'historique ; (2) le modèle décide soit de répondre, soit d'**appeler un outil** (nom + arguments typés) ; (3) le programme exécute l'outil et renvoie le résultat au modèle ; (4) retour en (2) jusqu'à la réponse finale ou un **plafond d'étapes**. Le modèle ne calcule pas : il choisit l'outil et traduit l'énoncé en arguments ; le calcul exact est fait par une fonction pure testée à part.

**Exemple (faux modèle SCRIPTÉ).** Question « qui gagne entre TFT, toujours $D$ et rancunier avec 5 % de bruit ? ». Étape 1 : le faux modèle émet l'appel `tournoi_axelrod(strategies=[TFT, toujours_D, rancunier], manches=200, bruit=0.05, repetitions=3)`. Le programme l'exécute et renvoie le JSON. Étape 2 : le faux modèle lit le dernier message et répond « Premier du classement : TFT ($1{,}45$) ». La boucle s'arrête en 2 étapes et 4 messages. Ce test prouve la **mécanique** ; il ne dit rien sur la qualité d'un vrai LLM (règle n°3 du guide : étiqueter « scripté »).

**Piège.** Une boucle sans plafond d'étapes peut tourner indéfiniment ; un résultat faux peut venir de l'énoncé mal traduit en arguments alors que l'outil est juste (relire les arguments avec `verbose=True`).

### 8.2 L'outil `@tool`

**Définition.** Le décorateur `@tool` transforme une fonction Python en outil appelable par un modèle : le **nom** est celui de la fonction, la **description** vient de la docstring, le **schéma des arguments** vient des annotations de type. Une docstring vague empêche le modèle d'appeler l'outil (guide, annexe B). Règles du guide : types annotés, docstring claire, **sortie JSON**, paramètres **plafonnés**, test avec `.invoke()` **sans LLM** d'abord.

**Code vérifié** (`langchain_core` 1.6.3) :

```python
from langchain_core.tools import tool
import json

@tool
def tournoi_axelrod(strategies: list[str], manches: int = 200, bruit: float = 0.0,
                    seed: int = 42, repetitions: int = 5) -> str:
    """Tournoi du dilemme répété entre des stratégies nommées ; renvoie le classement en JSON.
    manches plafonné à 1000, bruit plafonné à 0.5."""
    ok = [s for s in strategies if s in STRATEGIES]            # liste blanche
    if len(ok) < 2:
        return json.dumps({"erreur": "au moins 2 stratégies connues"})
    manches = max(1, min(int(manches), 1000))                   # plafonds
    bruit = max(0.0, min(float(bruit), 0.5))
    ...                                                         # calcul (fonction pure)
    return json.dumps({"manches": manches, "bruit": bruit, "classement": classement})
```

**Résultats observés.** `tournoi_axelrod.name` vaut `tournoi_axelrod` ; le schéma d'arguments généré est `strategies` (tableau de chaînes), `manches` (entier, défaut 200), `bruit` (nombre, défaut 0), `seed` (entier, défaut 42), `repetitions` (entier, défaut 5). Appel `.invoke({"strategies": ["TFT","toujours_D","rancunier"], "manches": 200, "bruit": 0.0, "seed": 42, "repetitions": 3})` : classement `[["TFT",2.332],["rancunier",2.332],["toujours_D",1.013]]` (TFT et rancunier à égalité sans bruit contre ces adversaires). Appel absurde `manches=10**9, bruit=2, strategies=["TFT","toujours_D","pirate"]` : ramené à `manches=1000`, `bruit=0.5`, le nom inconnu `pirate` ignoré, classement `[["TFT",2.271],["toujours_D",2.24]]`. Appel avec `"manches": "beaucoup"` : **ValidationError** (le type est contrôlé avant que la fonction s'exécute).

**Piège.** Les types NumPy ne sont pas sérialisables en JSON : convertir (le guide cite une fonction `_json()`). Un outil qui accepte un nom de fonction doit le vérifier contre une **liste blanche**, jamais l'exécuter tel quel.

### 8.3 Agent, Ollama et chaîne « prompt | modèle | parser »

**Éléments (guide).** Bibliothèques : LangChain (`create_agent`, `@tool`), `langchain-ollama`. **Ollama** exécute un LLM **en local** (gratuit) ; modèles cités : `llama3.1`, `qwen2.5`, `mistral-nemo` ; installation d'un modèle : `ollama pull llama3.1` ; lancement : l'application Ollama ou `ollama serve` dans un autre terminal. Dépannage (annexe B, tableau abîmé par l'OCR, appariement reconstitué) : « Ollama ne répond pas » : lancer l'application Ollama ou `ollama serve` dans un autre terminal ; « model not found » : `ollama pull llama3.1` (ou le nom donné dans la variable `OLLAMA_MODEL`) ; « does not support tools » : choisir `llama3.1`, `qwen2.5` ou `mistral-nemo` ; l'agent n'appelle aucun outil : docstring trop vague, consigne n°1 absente du system prompt, ou modèle trop petit ; résultat faux alors que l'outil est juste : énoncé mal traduit, relire les arguments ; `TypeError` dans un outil : types NumPy non convertis.

**Squelette typique (non exécuté ici, signature à vérifier dans la version installée) :**

```python
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
modele = ChatOllama(model="llama3.1", temperature=0)
agent = create_agent(modele, tools=[tournoi_axelrod, replicateur],
                     system_prompt="Utilise les outils ; n'invente aucun chiffre.")
reponse = agent.invoke({"messages": [{"role": "user", "content": "Qui gagne à 5 % de bruit ?"}]})
```

**Agent LLM joueur (projet 6).** Chaîne « prompt | modèle | parser » : le prompt contient l'historique des coups ; la sortie attendue est `CHOIX : COOPERER` ou `CHOIX : TRAHIR` ; le parseur cherche `CHOIX :`. Une sortie **sans** `CHOIX :` prend une valeur **par défaut** (coopérer) et est **comptée** à part. Parseur testé : `"Je réfléchis... CHOIX : TRAHIR"` donne $(D,\text{valide})$ ; `"choix : coopérer"` donne $(C,\text{valide})$ ; `"Je préfère ne pas choisir."` donne $(C,\text{invalide})$.

**Protocole du guide.** Au moins **10 parties de 10 manches** par configuration (horizon annoncé ou non, deux modèles Ollama), fréquence de coopération **par manche**, comparaison à TFT, comptage des sorties sans `CHOIX :` (un taux élevé signale un modèle trop petit ou un prompt à revoir). **Prédiction à tester** : horizon annoncé de 10 manches $\Rightarrow$ la théorie prévoit $D$ à la dernière manche (et par induction avant) ; un TFT coopère jusqu'au bout.

**Piège.** Les valeurs par défaut biaisent les résultats vers l'issue théorique (guide, projet 2) : toujours compter les sorties invalides et dire combien il y en a. Conclure sur un LLM à partir d'une **seule** partie : interdit.

### 8.4 Risques et plafonds

| Risque | Parade | Vérifié ici |
|---|---|---|
| Exécution de code produit par le LLM (`eval`, `exec`) | **jamais** ; les outils reçoivent des **données** (matrices, noms de fonctions de test), pas du code ; `json.loads` et `ast.literal_eval` refusent `__import__('os').getcwd()` (`JSONDecodeError`, `ValueError`) | oui |
| Paramètres coûteux (manches, répétitions, itérations, nombre de joueurs, $N$ de Monte-Carlo) | **plafonds** : manches $\le1000$, répétitions $\le50$, bruit $\le0{,}5$, $N\le$ environ un million | oui (1000 et 0,5 observés) |
| Nom d'outil ou de stratégie inventé ou malveillant | **liste blanche** ; chaîne `"__import__('os').system('echo X')"` rejetée avec message d'erreur | oui |
| Arguments de mauvais type | validation par le schéma | oui (`ValidationError`) |
| Boucle infinie | plafond d'étapes de l'agent | oui (5 étapes dans la démo) |
| Serveur Ollama exposé | n'écoute que sur `127.0.0.1` ; ne pas l'exposer sur Internet (règle n°5) | non |
| Conclure d'un faux modèle | étiqueter « scripté » | règle du guide |
| Texte renvoyé par un outil ou une page web qui donne des ordres au modèle (injection de prompt) | traiter toute sortie d'outil comme une **donnée non fiable** (standard, hors guide) | non |

**Pourquoi `eval` est interdit.** `eval(texte)` exécute n'importe quelle expression Python : si le texte vient d'un LLM, qu'un utilisateur peut influencer, c'est de l'exécution de code arbitraire. Le plafonnement protège contre le déni de service involontaire : un LLM peut très bien demander $10^9$ manches.

**Lien projet 6.** Les deux outils obligatoires sont `tournoi_axelrod` et `replicateur`, plafonnés, testés avec `.invoke()` sans LLM, puis branchés à l'agent avec un faux modèle (étiqueté « scripté »), puis Ollama avec `verbose=True`. Question d'oral : « pourquoi `eval` est-il interdit ? »

---

## 9. Glossaire (25 termes)

| N° | Terme | Définition courte |
|---|---|---|
| 1 | Agent rationnel | Joueur ou programme qui choisit l'action maximisant son gain (ou performance) **attendu**, vu ce qu'il perçoit ; pas omniscient. |
| 2 | Connaissance commune | Chacun sait que les autres sont rationnels, qu'ils savent qu'il l'est, etc. à l'infini (*common knowledge*). |
| 3 | Gain (payoff) | Nombre réel $\pi_i(a)$ associé à chaque profil de stratégies ; ici années de prison négatives ou points $T,R,P,S$. |
| 4 | Forme normale | Matrice des gains d'un jeu simultané, case $=$ (gain ligne, gain colonne). |
| 5 | Forme extensive | Arbre d'un jeu séquentiel : nœuds, branches, feuilles. |
| 6 | Stratégie mixte | Loi de probabilité sur les stratégies pures, choisie pour rendre l'adversaire indifférent. |
| 7 | Dominance stricte | $a_i$ domine si $\pi_i(a_i,a_{-i})>\pi_i(a_i',a_{-i})$ pour tout $a_{-i}$. |
| 8 | Équilibre de Nash | Profil où nul ne gagne à dévier **seul** : $\pi_i(a_i^*,a_{-i}^*)\ge\pi_i(a_i,a_{-i}^*)$. |
| 9 | Meilleure réponse | Stratégie qui maximise le gain **face à un choix donné** des autres (la dominante l'est face à tous). |
| 10 | Optimum de Pareto | Profil où l'on ne peut améliorer un joueur sans détériorer un autre. |
| 11 | Maximin | $\max_i\min_ju_1(i,j)$ : maximiser son gain minimum (prudence). |
| 12 | Somme nulle | Gain total **constant** (échecs, Matching Pennies) ; le dilemme ne l'est pas. |
| 13 | Induction à rebours | Résoudre un arbre du dernier nœud vers la racine, chaque joueur maximisant son gain. |
| 14 | Équilibre parfait en sous-jeux | Équilibre de Nash dans chaque sous-jeu ; élimine les menaces non crédibles. |
| 15 | Menace non crédible | Menace dont l'exécution n'est pas dans l'intérêt du menaçant au moment de jouer (combattre : $0<50$). |
| 16 | Facteur d'actualisation $\delta$ | Poids de l'avenir ou probabilité de continuer ; longueur moyenne $1/(1-\delta)$. |
| 17 | Tit-for-Tat | Coopère au 1er coup puis copie le dernier coup adverse ; seuil $\delta\ge2/3$ au projet. |
| 18 | Rancunier (grim trigger) | Coopère jusqu'à la première trahison, puis trahit toujours ; seuil $\delta\ge\dfrac{T-R}{T-P}=\dfrac12$. |
| 19 | Théorème de folklore | À $\delta$ proche de 1, tout gain moyen réalisable et individuellement rationnel est un gain d'équilibre du jeu répété. |
| 20 | Bruit $\varepsilon$ | Chaque coup est inversé avec la probabilité $\varepsilon$ (« main qui tremble » de Selten). |
| 21 | Dynamique du réplicateur | $x_i(t+1)=x_i(t)\,f_i/\bar f$ : les stratégies au-dessus de la moyenne se multiplient. |
| 22 | Équilibre bayésien parfait | Stratégies et croyances, ces dernières par Bayes sur le chemin d'équilibre et libres hors équilibre, avec rationalité à chaque ensemble d'information. |
| 23 | Cœur | Partages efficaces qu'aucune coalition ne rejette : $\sum_{i\in S}x_i\ge v(S)$ pour tout $S$ ; peut être vide. |
| 24 | Valeur de Shapley | Contribution marginale moyenne d'un joueur sur tous les ordres d'arrivée ; somme $=v(N)$. |
| 25 | Outil `@tool` | Fonction Python décorée, exposée à un LLM avec nom, description (docstring) et schéma d'arguments (annotations). |

---

## 10. Quinze pièges d'examen

1. **Nash $\ne$ Pareto.** Le dilemme : $(D,D)=(1,1)$ est l'équilibre, $(C,C)=(3,3)$ le domine. Aucune implication dans un sens ni dans l'autre (route : $(S,S)$ est Pareto-optimal sans être un équilibre).
2. **Dominante.** Elle doit être meilleure **colonne par colonne**, pas contenir le plus gros gain. Route : aucune dominante ($2>0$ face à $S$, mais $-1>-10$ face à $C$). Dominante $\Rightarrow$ Nash, jamais l'inverse.
3. **Méthode des cases.** Joueur ligne : comparer dans la **colonne** ; joueur colonne : dans la **ligne** ; jamais en diagonale ; lister **tous** les équilibres (route : deux ; trois jeux $3\times3$ du notebook en ont jusqu'à trois).
4. **Mixte.** L'indifférence est celle de **l'autre** joueur ; vérifier $p,q\in[0,1]$ ; ne pas réutiliser $(1/2,1/2)$ par symétrie (asymétrique : $2/5$) ; le mixte peut être pire que les purs (bataille : $1{,}875$ contre $5$ ou $3$).
5. **Cours $\ne$ TD.** Route : $(S,S)=(-1,-1)$ au cours (mixte : continuer avec la probabilité $1/4$) contre $(0,0)$ au TD (continuer avec $2/11$). Bataille : $(5,2),(2,5)$ au cours, $(5,3),(3,5)$ au TD. Relire la matrice avant d'appliquer un corrigé.
6. **Induction à rebours.** Partir de la **fin** ; au nœud de I utiliser les gains de I ; une stratégie est un plan **complet** (« Coopérer si E entre ») ; $(\text{Ne pas entrer},\text{Combattre})$ est un Nash mais pas un EPSJ.
7. **Horizon.** Fini et connu : $(D,D)$ à toutes les manches (induction), quelle que soit la longueur ; indéterminé avec $\delta$ assez grand : la coopération est possible. Répondre à « un joueur rationnel coopère-t-il dans le dilemme répété ? » sans préciser l'horizon est incomplet.
8. **Seuils de $\delta$.** Rancunier $\dfrac{T-R}{T-P}=\dfrac12$, TFT $\dfrac{T-R}{R-S}=\dfrac23$ ; utiliser $P$ (pas $S$) après la trahison ; $\delta$ **grand** $=$ patience ; ne pas confondre $\delta$, $\gamma$ (RL), $\alpha$ (taux), $\varepsilon$ (exploration ou bruit).
9. **Conventions du tournoi.** Comparer des **moyennes par manche**, pas des totaux de durées différentes ; inclure l'auto-jeu ; appliquer le bruit à **chaque coup de chaque joueur**, pas à un seul.
10. **TFT.** Il ne gagne pas toujours : rancunier $2{,}66>$ TFT $2{,}54$ sans bruit, toujours $D$ ($2{,}37$) en tête à $\varepsilon=0{,}05$. Il n'est pas indulgent : une erreur donne l'écho $5,0,5,0,\dots$ soit $2{,}5$ par manche ; deux erreurs peuvent l'enfermer en $(D,D)$ (moyenne $1{,}56$ dans l'exemple). TFT ne bat jamais directement un adversaire ($0{,}995$ contre $1{,}02$).
11. **Réplicateur.** Ce n'est pas le tournoi : les parts bougent, le résultat dépend des **parts initiales** et du **bruit** ($\varepsilon=0$ : rancunier $0{,}345$, TFT $0{,}283$, Pavlov $0{,}225$, toujours $C$ $0{,}147$ ; $\varepsilon=0{,}05$ : Pavlov $99{,}8\,\%$). Entre gentils, les parts ne bougent plus (dérive neutre).
12. **Information.** Imparfaite (on ne voit pas un coup) $\ne$ incomplète (on ignore un type) ; la règle de Bayes ne s'applique pas à un message hors équilibre : la croyance y est **libre** (Bière ou Quiche : poolant Bière valide ssi $\mu(\text{Faible}\mid Q)\ge1/2$).
13. **Jeux coopératifs.** Le cœur peut être vide (majorité à 3 joueurs) ; Shapley n'est pas forcément dans le cœur (gants : $(1/6,1/6,2/3)$ contre cœur $\{(0,0,1)\}$) ; poids $\ne$ pouvoir ($[51;49,48,3]$ : indices $1/3$ chacun) ; ne pas oublier $v(\varnothing)=0$.
14. **Enchères et vote.** Vickrey : miser sa **vraie** valeur est dominant ; premier prix : miser $\frac{n-1}{n}v$ ($2v/3$ pour $n=3$), jamais $v$ ; revenus espérés **égaux** ($1/2$) ; pluralité $\ne$ Condorcet (profil 40/35/25 : $A$ contre $B$) ; Rubinstein : lire $\dfrac{1-\delta_2}{1-\delta_1\delta_2}$ sans inverser les $\delta$ ; Contract Net glouton $14$ contre optimum $9$.
15. **Agents LLM.** Jamais `eval`/`exec` sur une sortie du modèle ; paramètres **plafonnés** (manches $\le1000$, bruit $\le0{,}5$) ; liste blanche de noms ; sortie d'un faux modèle étiquetée « scripté » ; au moins 10 parties de 10 manches par configuration ; compter les sorties sans `CHOIX :` ; aucune conclusion sur un LLM à partir d'**une** partie.

---

## 11. Ce qui n'a pas pu être vérifié, et limites

1. **Supports du prof au delà du chapitre 1** : absents. Les sections 5 (Bayes, EBP), 6 (Shapley, cœur), 7 (PSO, ACO, boids, AG) et 8 (agent à 10 outils) sont reconstruites à partir du guide et du savoir standard. Notations et exemples du prof peuvent différer.
2. **Bataille des sexes du guide** ($p=2/3$, $q=1/3$) : non reproduite avec les gains du cours ($5/7$, $2/7$) ni du TD ($5/8$, $3/8$).
3. **Bière ou Quiche du guide** ($P(\text{Fort})=0{,}9$ puis $0{,}3$) : le cas $0{,}9$ est reproduit avec les gains standard (poolant Bière valide pour $0{,}6$, non valide pour $0{,}2$) ; le cas $0{,}3$ ne l'est pas ; les gains du prof sont inconnus.
4. **Références historiques citées de mémoire** : tournoi d'Axelrod (14 programmes plus un aléatoire, puis 62 participants), Friedman (1971) et Fudenberg-Maskin (1986), Cho et Kreps (1987), Reynolds (1986), Kreps-Milgrom-Roberts-Wilson, Brooks (subsumption), Schelling (point focal).
5. **LangChain** : `create_agent`, `langchain-ollama` et Ollama n'ont pas été exécutés ; le squelette de la section 8.3 est à vérifier dans la version installée.
6. **Mille-pattes** : seuls les gains de l'EPSJ $(1,0)$ viennent du guide ; les autres sont de moi.
7. **Implémentations** de l'algorithme génétique, du PSO, de l'ACO et des boids : les miennes (graines fixées, paramètres choisis par moi), pas `agent_tj_sma.py`.
8. **Tournoi et réplicateur** : chiffres obtenus avec le `jeux.py` du groupe (graine 42, 20 répétitions par paire) ; ils redonnent exactement ceux du notebook. D'autres graines donneraient des décimales voisines.
9. **PDF « Google Gemini »** : non lu.
10. **Valeurs par défaut de `tournoi()` dans le guide** : illisibles (OCR), ignorées.
