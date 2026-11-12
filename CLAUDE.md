# CLAUDE.md : Groupe 6, Projet 6 « Dilemme du prisonnier répété : tournoi d'Axelrod et agents LLM »

Fichier de pilotage : ce qui est fait, ce qui reste, qui le fait, avec quelles commandes et quelle preuve. Il est mis à jour à chaque jalon (journal, §11).

## 1. Aiguillage selon le lecteur

| Tu es… | Lis dans cet ordre |
|---|---|
| Membre du groupe qui ouvre le dépôt | §12 « Guide du membre », puis `docs/COMPRENDRE.md`, puis l'étape de §8 qui te concerne |
| Une session d'IA (quel que soit le membre qui la lance) | §2 en entier, puis §10 (règles selon l'utilisateur de la session) |

## 2. Reprise d'une session en 6 gestes

0. Identifier l'utilisateur (lui demander son prénom s'il ne l'a pas donné) : identité Git et accord avant de pousser en dépendent (§10).
1. Lire ce fichier, puis `docs/COMPRENDRE.md` et `CONVENTIONS.md`.
2. Installer (`pip install -r requirements.txt`) et lancer `python -m pytest` à la racine. Sur `main` à l'état S1 : **8 tests verts** (`tests/test_jeux.py`). Sinon, corriger avant tout.
3. Lire §7 (état) et §8 (plan) ; reprendre à la première case non cochée.
4. Ne rien faire de visible par d'autres (push, PR, invitation, message) sans l'accord de l'utilisateur.
5. Avant de terminer : mettre à jour §7 et §11.

Vocabulaire : `[x]` fait et prouvé (commande ou fichier cité) ; `[ ]` à faire ; **scripté** : sortie du faux modèle, ne prouve que la mécanique ; **non vérifié** : écrit, jamais exécuté ; **proposé** : choix non validé ; **figé** : décidé. Sources de vérité par ordre de priorité : tests, `CONVENTIONS.md`, ce fichier, `README.md`, `docs/`.

## 3. Contexte et spécification

**Équipe.** Quatre membres : MARZAQ Jihane (`jihane-marzaq`), SADOUR Assia (`as7ia`), TSETSE Komla Edem Wilfried (`wekt2k04`, propriétaire du dépôt), ZERBAOUI Marwane (`MarwaneZe`). Cycle ingénieur IDIA3, ENSA Safi, 2026-2027. Module : Théorie des Jeux et Systèmes Multi-Agents, Pr Abdelilah JRAIFI. Dépôt : `github.com/wekt2k04/projet-groupe6-dilemme-repete-axelrod` (privé).

**Rôles S1 à S4** (proposition, à valider en séance) : Wilfried chef de projet et théorie ; Assia quant / Python ; Marwane développeur de l'agent ; Jihane testeuse. **Rotation à la fin de la S4** : Jihane cheffe de projet, Wilfried quant, Assia développeuse de l'agent, Marwane testeur. Présentateurs : S1 Wilfried, S2 Assia, S3 Marwane, S4 Jihane, S5 Wilfried, S6 Assia, S7 Marwane.

**Calendrier.** Une séance par semaine à partir du 11/11/2026 (S2 18/11, S3 25/11, S4 02/12, S5 09/12, S6 16/12, S7 23/12), indicatif ; le 18/11 est férié au Maroc, la S2 est probablement déplacée. Pas de soutenance finale : à chaque début de séance, un membre présente 10 minutes d'avancement appuyé sur le Gantt, avec un livrable concret.

**Spécification du projet 6 (guide, page 16).**

| Rubrique | Contenu imposé |
|---|---|
| Gains | (C,C)=(3,3), (C,D)=(0,5), (D,C)=(5,0), (D,D)=(1,1) ; T=5, R=3, P=1, S=0 ; dilemme : T>R>P>S et 2R>T+S |
| Horizon indéterminé | rancunier : coopération stable si δ ≥ (T−R)/(T−P) = 1/2 |
| Réplicateur | x_i(t+1) = x_i(t) f_i / f̄ |
| Lien avec le cours | à horizon fini connu, l'induction à rebours prédit la trahison (mille-pattes) |
| Hypothèses | 200 manches par rencontre ; bruit ε : chaque coup inversé avec la probabilité ε, pour les deux joueurs ; six stratégies : toujours_C, toujours_D, TFT, rancunier, Pavlov, aleatoire |
| Données | tournoi à toutes les paires, auto-jeu compris (convention écrite) ; ε ∈ {0 ; 0,01 ; 0,05} ; graine fixée ; scores moyens par manche |
| Fonctions | `STRATEGIES`, `match(s1, s2, manches, bruit, rng)`, `tournoi(strategies, manches=200, bruit=0.0, seed=0)`, `replicateur(scores, x0, generations)` |
| Tests | TFT/TFT sans bruit = (3,3) ; D contre C = (5,0) ; TFT ne perd que la 1re manche contre D ; parts du réplicateur positives de somme 1 ; seuil δ = 1/2 vérifié par partie à arrêt aléatoire |
| Outils agent | `tournoi_axelrod(strategies, manches, bruit, seed)`, `replicateur(strategies, generations)`, plafonds ; option : spécialiste « jeux répétés » du superviseur du chapitre 6 |
| Expériences | classement selon ε ; TFT résiste-t-il ; TFT généreux ; réplicateur depuis parts égales ; agents LLM : prompt \| modèle \| parseur du TP6, `CHOIX : COOPERER/TRAHIR`, au moins 10 parties de 10 manches par configuration (horizon annoncé ou non × 2 modèles Ollama), fréquence de coopération par manche, comparaison à TFT, comptage à part des réponses sans `CHOIX :` |

Piège connu : le texte extrait du PDF du guide affiche `tournoi(manches=260, bruit=0.8, seed=8)` (erreur d'OCR) ; l'image de la page 16 fait foi : `manches=200, bruit=0.0, seed=0`.

## 4. Cadre imposé par le guide

Règles d'or : (1) tous les membres comprennent tout le code ; (2) le code du cours est le socle, on l'étend (fonctions pures, au moins 2 nouveaux outils `@tool`, nouveaux tests) ; (3) honnêteté expérimentale (faux modèle = « scripté », aucune conclusion sur une seule exécution) ; (4) Git : au moins un commit par semaine et par étudiant, `[Prénom] verbe + objet`, un nom absent de l'historique donne une note individuelle ; (5) sécurité : jamais `eval`/`exec` sur un texte de LLM, outils sans code, paramètres plafonnés, Ollama sur 127.0.0.1 ; (6) Gantt obligatoire (prévisionnel S1, réalisé, rotation en S4, dans le rapport section « Organisation et planification » et dans `docs/` avec sa source).

Phases : 0 fiche de lecture (2 pages, S1) ; 1 théorie ; 2 données et paramètres ; 3 Python ; 4 agents (`.invoke()` sans LLM, puis Ollama avec `verbose=True`) ; 5 expériences.

| Sem. | Attendu pour le point d'avancement |
|---|---|
| S1 | dépôt ; Ollama et llama3.1 ; fiche de lecture ; fonctions du cours à étendre ; Gantt prévisionnel |
| S2 | formules expliquées ; notebook qui retrouve les résultats du cours |
| S3 | outils `@tool` fonctionnels avec `.invoke()` ; premiers tests pytest |
| S4 | agent testé (faux modèle puis Ollama) ; premières expériences ; rotation ; Gantt prévu contre réalisé |
| S5 | protocole complet exécuté ; tableaux ; tests verts |
| S6 | code finalisé ; rapport à 80 % avec Gantt |
| S7 | rapport et code zippé ; bilan du Gantt réalisé |

Barème : mini-comptes rendus 20 %, code et théorie 25 %, agents et expériences 25 %, rapport 15 %, avancement hebdomadaire 15 %.

## 5. Décisions

| Sujet | Décision | Statut |
|---|---|---|
| Auto-jeu | une stratégie joue contre elle-même ; score = moyenne des deux côtés | figé (`CONVENTIONS.md`) |
| Bruit | indépendant pour chaque joueur et chaque coup ; les historiques contiennent les coups exécutés | figé |
| Scores | gains moyens par manche, jamais de totaux | figé |
| Seuil de TFT | 2/3 (déviation alternée T,S,T,S) ; seuil du rancunier 1/2 | figé, vérifié par calcul ; Monte-Carlo pour le rancunier |
| Emplacement de l'agent | `src/agent_tj_sma.py` (l'annexe A du guide le place à la racine) | proposé |
| Code du cours | absent de nos supports : l'agent est reconstruit d'après le guide | **à trancher** (le demander au professeur) |
| Adversaire d'un agent LLM | stratégie classique (TFT en priorité) ; LLM contre LLM en option | proposé, question posée au professeur |
| Modèles Ollama | llama3.1 et qwen2.5 | proposé |
| Rôles et rotation | voir §3 | proposé, à valider en séance |

## 6. Arborescence et contrats

| Chemin | Contenu | État |
|---|---|---|
| `src/jeux.py` | S1 : prototype (six stratégies, `match`, `tournoi`, `replicateur`, `seuil_rancunier`, `match_arret_aleatoire`) | fait, 8 tests |
| `src/experiences.py`, `src/agent_tj_sma.py` | protocoles ; outils et agent | à faire (S3 à S5) |
| `tests/` | `test_jeux.py` ; `test_hors_ligne.py` (faux modèle « scripté ») | S1 fait ; le reste à faire |
| `notebooks/` | `01_theorie_prototype`, `02_outils_agent`, `03_experiences` | à faire |
| `docs/fiche_lecture.pdf` (+ `.md`) | fiche de 2 pages | fait |
| `docs/gantt_previsionnel.png`, `gantt_realise.png`, `gantt_source.xlsx` | Gantt, grilles prévue et réalisée | fait (S1) |
| `docs/avancement/` | points d'avancement PDF (`SN.pdf`) et leurs sources `sources/SN.json` | S1 fait |
| `docs/MATIERE.md`, `docs/COMPRENDRE.md` | le cours expliqué ; le projet expliqué à l'équipe | faits |
| `docs/membres/` | premier commit de chaque membre | modèle fait |
| `tools/` | `build_gantt.py`, `build_gantt_realise.py`, `build_avancement.py` | faits |
| `CONVENTIONS.md`, `README.md`, `requirements.txt`, `pytest.ini` | conventions, installation | faits |

Contrats actuels de `src/jeux.py` : `match(s1, s2, manches=200, bruit=0.0, rng=None) -> (score1, score2)` ; `tournoi(strategies=None, manches=200, bruit=0.0, seed=42, repetitions=1) -> (noms, M, classement)` (la graine par défaut passe à 0 en S2, conformément au guide) ; `replicateur(M, x0, generations) -> trajectoire` ; `seuil_rancunier() = 0,5`.

Régénérer les documents : `python tools/build_gantt.py`, `python tools/build_gantt_realise.py <semaine>`, `python tools/build_avancement.py <semaine>`, `pandoc docs/fiche_lecture.md -o docs/fiche_lecture.pdf --pdf-engine=xelatex`.

## 7. État (S1, 12/11/2026)

- [x] Dépôt privé créé ; invitations (droit d'écriture) envoyées à `as7ia`, `jihane-marzaq`, `MarwaneZe` ; acceptation en attente.
- [x] Prototype `src/jeux.py` et 8 tests : `python -m pytest` donne 8 passed.
- [x] Fiche de lecture (2 pages), Gantt prévisionnel et source xlsx, point d'avancement S1 (4 pages : garde, 2 pages, annexe), `COMPRENDRE.md`, `MATIERE.md`.
- [x] Ollama sur le poste de Wilfried, restreint à 127.0.0.1 ; modèles llama3.1 et qwen2.5 téléchargés.
- [ ] Installation d'Ollama et premier commit nominatif chez Assia, Jihane et Marwane.
- Non vérifié : aucune partie LLM n'a été jouée. Scripté : rien pour l'instant.

## 8. Plan en étapes atomiques

Chaque étape : identifiant, responsable (casquette S1 à S4, puis après rotation), commande ou fichier, preuve, repli.

| Id | Qui | Étape | Preuve | Repli |
|---|---|---|---|---|
| S1-01 | tous | accepter l'invitation, créer `docs/membres/<prénom>.md`, premier commit | `git log` montre le prénom | modèle dans `docs/membres/README.md` |
| S1-02 | Marwane | `ollama pull llama3.1`, vérifier `ollama list`, Ollama sur 127.0.0.1 | sortie `ollama list` | utiliser le poste de Wilfried |
| S2-01 | Assia | `src/jeux.py` complété (validations, TFT généreux, seuils) | tests verts | prototype S1 |
| S2-02 | Wilfried | notebook `01_theorie_prototype` : retrouver les résultats du cours | notebook exécuté | formules à la main |
| S2-03 | Jihane | tests du seuil δ par arrêt aléatoire | `pytest` vert | marge de tolérance plus large |
| S3-01 | Marwane | outils `tournoi_axelrod` et `replicateur` avec `.invoke()` | sortie JSON | appel direct des fonctions |
| S3-02 | Jihane | `tests/test_hors_ligne.py` : outils et boucle avec faux modèle « scripté » | tests verts | tests des outils seuls |
| S4-01 | Marwane | agent testé : faux modèle (scripté) puis Ollama avec `verbose=True` | trace de l'agent | faux modèle seul, à signaler |
| S4-02 | Jihane | premières expériences (classement selon ε, TFT généreux) | tableau | une seule valeur de ε |
| S4-03 | Wilfried | Gantt prévu contre réalisé, rotation | `docs/gantt_realise.png` | tableau texte |
| S5-01 | Marwane (testeur) | protocole complet : 10 parties de 10 manches × (horizon annoncé ou non) × 2 modèles | `resultats/` | réduire à un modèle, à signaler |
| S5-02 | Wilfried (quant) | notebook `03_experiences`, réplicateur, écarts à la théorie | notebook exécuté | tableaux CSV |
| S6-01 | Jihane (cheffe) | rapport à 80 % avec Gantt | `docs/rapport/` | plan détaillé |
| S7-01 | tous | rapport final, archive zippée, bilan du Gantt | archive | rapport PDF seul |

## 9. Pièges

Auto-jeu oublié ; bruit appliqué à un seul joueur ; totaux comparés sur des horizons différents ; conclusion tirée d'une seule partie LLM ; OCR du guide (`manches=260`) ; confondre plan complet et chemin joué (induction à rebours) ; comparer des flottants sans tolérance ; réponses LLM sans ligne `CHOIX :` (les compter à part, ne pas les remplacer silencieusement par la valeur théorique) ; Ollama exposé en `0.0.0.0` (le restreindre à `127.0.0.1`) ; `eval` d'une sortie de modèle (interdit) ; un commit fait sous le nom d'un autre membre (interdit).

## 10. Règles selon l'utilisateur de la session

- **Wilfried** (propriétaire) : français, concis, tranché ; il autorise les opérations Git de préparation sur ce dépôt, mais jamais de fusion de PR ni de push sur `main` après le premier commit sans son accord.
- **Un autre membre** : identité Git à son nom (`git config user.name`), messages `[Prénom] verbe + objet (id étape)` ; il récupère ses fichiers depuis la branche de la semaine (`git checkout origin/prep/sN -- <fichiers>`), les exécute chez lui, les commite à son nom et ouvre sa PR. Jamais de commit sous le nom d'un autre.
- **Toute session** : aucun `eval`/`exec` sur une sortie de modèle ; résultats du faux modèle étiquetés « scripté » ; aucun chiffre sans sortie exécutée ; ne pas écrire de lignes d'attribution à une IA dans les commits ni les PR ; demander avant toute action visible par d'autres ou irréversible.

## 11. Journal

- 12/11/2026 : socle S1 : structure, conventions, prototype `jeux.py` (8 tests), fiche de lecture, Gantt, point d'avancement S1, `COMPRENDRE.md`, `MATIERE.md`. Dépôt privé créé, trois invitations envoyées. Ollama restreint à 127.0.0.1, llama3.1 et qwen2.5 téléchargés.

## 12. Guide du membre

**Ce qui compte pour la note** : au moins un commit par semaine à ton nom (`[Prénom] verbe + objet`), comprendre tout le code, présenter ton point d'avancement quand c'est ton tour, aucune conclusion tirée d'une seule exécution.

**Installer une fois.**
```
git clone https://github.com/wekt2k04/projet-groupe6-dilemme-repete-axelrod.git
cd projet-groupe6-dilemme-repete-axelrod
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```
Pour les agents : installer Ollama, vérifier qu'il n'écoute que sur 127.0.0.1, puis `ollama pull llama3.1` et `ollama pull qwen2.5`.

**Lire pour comprendre, dans cet ordre** : `docs/COMPRENDRE.md`, `CONVENTIONS.md`, `docs/fiche_lecture.pdf`, puis `docs/MATIERE.md` selon les besoins.

**Premier commit (2 minutes)** : accepter l'invitation GitHub, créer `docs/membres/<prénom>.md` d'après le modèle de `docs/membres/README.md`, le commiter avec le message `[Prénom] Ajout de ma fiche membre`.

**Chaque semaine** : ouvrir `docs/semaines/SN.md` sur la branche `prep/sN`, récupérer tes fichiers, les exécuter chez toi, commiter à ton nom, ouvrir ta PR, la faire relire par un autre membre.

**Ce qu'on ne fait jamais** : commiter sous le nom d'un autre, fusionner sa propre PR sans relecture, pousser directement sur `main`, exposer Ollama sur le réseau, exécuter le texte d'un modèle.
