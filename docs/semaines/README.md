# Le travail de la semaine : méthode

Tout le travail du projet est préparé à l'avance sur des branches `prep/s2` à `prep/s7` (une par semaine, chacune contient les précédentes). **Ces branches ne sont jamais fusionnées** dans `main` : chaque membre en récupère seulement ses fichiers, les exécute chez lui et les commite à son nom, pour que l'historique reflète le travail réel de chacun.

## Chaque semaine

1. Ouvrir la fiche de la semaine : `docs/semaines/S<n>.md` **sur la branche `prep/s<n>`** (sur GitHub : choisir la branche dans le menu, puis ouvrir le fichier). Elle dit qui prend quels fichiers, avec quelles commandes, et ce qu'il faut comprendre.
2. Récupérer **ses** fichiers dans **sa** branche, partie de `main` :
   ```
   git fetch origin
   git checkout -b <prenom>-s<n> origin/main
   git checkout origin/prep/s<n> -- <fichiers indiqués dans la fiche>
   ```
3. Exécuter chez soi (tests, notebook, Ollama quand la fiche le demande) et lire la partie « À comprendre » : il faut pouvoir expliquer chaque ligne.
4. Commiter **à son nom** : `git commit -m "[Prénom] <verbe + objet> (<étape>)"`, puis `git push -u origin <prenom>-s<n>`, ouvrir la PR, la faire relire par un autre membre, fusionner après approbation.

## Calendrier

| Semaine | Thème | Fiche | Point d'avancement (`docs/avancement/`) |
|---|---|---|---|
| S1 | cadrage et théorie | sur `main` | `S1.pdf` |
| S2 | prototype Python | `S2.md` | `S2.pdf` |
| S3 | outils LangChain | `S3.md` | `S3.pdf` |
| S4 | agent, premières expériences, rotation | `S4.md` | `S4.pdf` |
| S5 | protocole complet et résultats | `S5.md` | `S5.pdf` |
| S6 | rapport à 80 % | `S6.md` | `S6.pdf` |
| S7 | remise et bilan | `S7.md` | `S7.pdf` |

Le point d'avancement de la semaine n est présenté par un membre différent de la semaine n−1 : S1 Wilfried, S2 Assia, S3 Marwane, S4 Jihane, S5 Wilfried, S6 Assia, S7 Marwane. La rotation des rôles a lieu à la fin de la S4.

## Règles

Un commit par semaine et par membre au moins. Aucun commit sous le nom d'un autre. Aucune PR fusionnée sans relecture. Les résultats du faux modèle sont étiquetés « scripté ». Les résultats d'un vrai modèle indiquent le modèle, sa version, la graine et le nombre de parties. Aucune conclusion sur une seule exécution.
