# Dilemme du prisonnier répété : tournoi d'Axelrod et agents LLM

Projet intégrateur n° 6 du module Théorie des Jeux et Systèmes Multi-Agents (Pr Abdelilah JRAIFI), cycle ingénieur Informatique Décisionnelle et IA (IDIA3), ENSA Safi, année 2026-2027.

Groupe 6 : MARZAQ Jihane, SADOUR Assia, TSETSE Komla Edem Wilfried, ZERBAOUI Marwane.

Calcul sur GPU gratuit (parties LLM et essais de l'agent, environ cinq minutes au lieu d'une heure) : [![Ouvrir dans Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/wekt2k04/projet-groupe6-dilemme-repete-axelrod/blob/prep/passation/notebooks/00_colab_ollama.ipynb)

## Sujet

On simule un tournoi entre six stratégies du dilemme du prisonnier répété (toujours coopérer, toujours trahir, tit-for-tat, rancunier, Pavlov, aléatoire), on mesure l'effet du bruit et l'évolution d'une population par la dynamique du réplicateur, puis on fait jouer des agents LLM locaux (Ollama) et on compare leur comportement aux stratégies classiques. Le lien avec le cours : à horizon fini connu, l'induction à rebours prédit la trahison à chaque manche.

## Contenu du dépôt

| Chemin | Rôle |
|---|---|
| `src/jeux.py` | fonctions pures : stratégies, `match`, `tournoi`, `replicateur`, seuils de δ |
| `src/experiences.py` | protocoles d'expérience, graines, tableaux |
| `src/agent_tj_sma.py` | outils `@tool` et agent LangChain, étendus pour le projet |
| `tests/` | tests pytest ; `test_hors_ligne.py` utilise un faux modèle étiqueté « scripté » |
| `notebooks/` | prototype théorique, outils de l'agent, expériences |
| `docs/` | fiche de lecture, Gantt (image et source), points d'avancement, rapport, cours expliqué, fiches des membres |
| `tools/` | scripts qui régénèrent le Gantt et les points d'avancement PDF |
| `CONVENTIONS.md` | conventions du groupe (auto-jeu, bruit, scores par manche, format LLM) |

Selon la semaine, certains fichiers ne sont pas encore présents : le dépôt se construit au fil des sept séances.

## Installation

```
python -m venv .venv
.venv\Scripts\activate          # Windows ; sous Linux ou macOS : source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

Pour les agents LLM, installer Ollama (https://ollama.com), le laisser écouter uniquement sur 127.0.0.1 (réglage par défaut ; ne jamais le définir à 0.0.0.0), puis :

```
ollama pull llama3.1
ollama pull qwen2.5
```

## Lancer

```
python -m pytest                    # tous les tests
python tools/build_gantt.py          # Gantt prévisionnel et source xlsx
python tools/build_gantt_realise.py 1   # Gantt réalisé (état à la fin de la semaine donnée)
python tools/build_avancement.py 1      # point d'avancement PDF de la semaine
```

## Règles du groupe

Un commit au moins par semaine et par membre, au format `[Prénom] verbe + objet`. Les conventions de calcul sont dans `CONVENTIONS.md`. Un résultat obtenu avec le faux modèle est toujours étiqueté « scripté » ; aucune conclusion n'est tirée d'une seule partie.
