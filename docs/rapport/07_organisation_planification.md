## 7. Organisation et planification

### 7.1 Rôles et rotation

Le groupe compte quatre membres, et chacun tient un rôle, comme le demande le guide : chef de projet, quant (Python), développeur de l'agent et testeur. À la fin de la semaine 4, les rôles ont tourné d'un cran, de sorte que chacun a travaillé sur une autre partie du projet pendant la seconde période.

| Membre | Rôle, semaines 1 à 4 | Rôle, semaines 5 à 7 | Présente en |
|---|---|---|---|
| Wilfried | Chef de projet et théorie | Quant / Python | S1, S5 |
| Assia | Quant / Python | Développeuse de l'agent | S2, S6 |
| Marwane | Développeur de l'agent | Testeur | S3, S7 |
| Jihane | Testeuse | Cheffe de projet | S4 |

Dans la première période, la théorie, les formules et le Gantt revenaient à Wilfried, `jeux.py` et le notebook 01 à Assia, les outils de l'agent et le joueur LLM à Marwane, la suite de tests et le dépôt à Jihane. Après la rotation, le notebook 03 et le protocole multi-graines sont revenus à Wilfried, les tests du module d'expériences et la relecture du prompt à Assia, les parties LLM et le contrôle des résultats à Marwane, le point d'avancement, le Gantt réalisé et la relecture des pull requests à Jihane. Un présentateur différent expose chaque point d'avancement.

### 7.2 Gantt prévu contre Gantt réalisé

Le Gantt prévisionnel (`docs/gantt_previsionnel.png`) a été établi à la première séance. Il découpe le projet en 19 tâches réparties en cinq phases (cadrage, Python, agents, expériences, rapport), chacune avec un responsable et une durée en semaines, et quatre jalons : la fiche de lecture en S1, la rotation des rôles en S4, le rapport à 80 % en S6 et la remise en S7. Les dates des séances sont indicatives (de 11/11 à 23/12, une par semaine, avec une réserve pour le 18/11, jour férié à confirmer).

![Gantt prévisionnel établi en semaine 1](docs/gantt_previsionnel.png)

La source éditable est le classeur `docs/gantt_source.xlsx`, dont les colonnes de début réel, de fin réelle et de statut sont mises à jour à chaque séance, après quoi l'image du Gantt réalisé est régénérée par `tools/build_gantt_realise.py`.

![Gantt réalisé, prévu en gris et réalisé en couleur](docs/gantt_realise.png)

À la fin de la semaine 5, 16 tâches sur 19 étaient terminées, une était en cours (la rédaction du rapport) et deux restaient à faire (le code finalisé avec l'archive, puis le bilan du Gantt), toutes deux prévues en S6 et S7. Sur les tâches terminées, un seul écart de calendrier apparaît : les parties LLM, prévues sur les semaines 5 et 6, sont terminées en semaine 5, parce qu'un GPU gratuit joue une partie en 2 à 3 secondes une fois le modèle chargé, contre 42 à 84 secondes sur CPU, ce qui a permis de jouer les quatre configurations dans la semaine. Toutes les autres tâches ont été faites dans la fenêtre prévue. Un écart ne se voit pas sur le Gantt : les essais de la question 4 de l'agent sur CPU, perdus par un bug de notre contrôle en semaine 4, ont dû être rejoués sur le GPU (chapitre 6). ⟦à compléter : état réel des tâches « code finalisé, archive » et « Gantt réalisé et bilan » à la remise, avec la semaine de fin⟧.

### 7.3 Discipline Git

Le dépôt privé du groupe est organisé selon l'annexe A du guide. Nos règles sont écrites dans `CONVENTIONS.md` : au moins un commit par semaine et par membre, au format `[Prénom] verbe + objet (id étape)`, et jamais de commit sous le nom d'un autre membre. Chaque modification passe par une branche et une pull request relue par un autre membre, et un ordre de fusion est fixé quand des fichiers dépendent les uns des autres : par exemple, le module d'expériences avant les tests qui l'importent. Le prénom dans le message permet de vérifier la contribution de chacun : un nom absent de l'historique ferait passer la note de collective à individuelle. ⟦à compléter : sortie de `git shortlog -sn` à la remise, avec le nombre de commits par membre et la liste des semaines couvertes par chacun⟧. ⟦à compléter : nombre de pull requests relues par un autre membre que son auteur⟧.

Un risque de sécurité a été corrigé à l'échelle du groupe : Ollama écoutait par défaut sur toutes les interfaces réseau du poste du chef de projet. Il a été restreint à `127.0.0.1`, et cette règle est inscrite dans les conventions et dans le README, avec l'interdiction de la changer en `0.0.0.0`. ⟦à compléter : confirmation de l'installation d'Ollama et du lancement des tests chez Assia, Jihane et Marwane⟧.

### 7.4 Points d'avancement

Chaque semaine, un mini livrable PDF de deux pages au plus est présenté en dix minutes par le membre désigné. Il suit toujours la même trame : l'objet, ce qui a été réalisé, les choix, les écarts entre le prévu et le réalisé, les questions au professeur, le plan de la semaine suivante et le Gantt en annexe. Les semaines 1 à 5 ont porté sur le cadrage et la théorie, le prototype Python, les outils LangChain, l'agent testé avec Ollama avec la rotation, puis le protocole complet et les résultats. La semaine 6 est consacrée au code finalisé (74 tests verts) et à un rapport rédigé à 80 %. La semaine 7 porte la remise du rapport et de l'archive du projet, ainsi que le bilan du Gantt. ⟦à compléter : réponses du professeur aux questions posées en séance, notamment sur le code du cours `agent_tj_sma.py`, sur l'adversaire des agents LLM et sur l'usage d'un GPU gratuit⟧. ⟦à compléter : présence des quatre membres à chaque séance⟧.
