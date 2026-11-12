# -*- coding: utf-8 -*-
"""Essaie l'agent LangChain avec un vrai modèle Ollama sur des questions types ; vérifie l'outil appelé et ses arguments.

Usage depuis la racine du dépôt (Ollama lancé, modèle téléchargé) :
    python scripts/essai_agent_ollama.py --modele llama3.1 --essais 3
Chaque question est posée `--essais` fois (jamais de conclusion sur un seul essai). Sortie : resultats/agent_<modele>.jsonl,
avec les appels d'outils, les arguments, le contrôle automatique (src/controles_agent.py, tolérant sur le type des nombres) et la réponse finale. Durée estimée sur un CPU de portable :
20 à 60 s par question, soit 30 à 45 minutes pour 5 questions x 3 essais. Le texte d'un modèle n'est jamais exécuté.
"""
import argparse
import json
import os
import sys
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

from agent_tj_sma import construire_agent, interroger  # noqa: E402
from controles_agent import controle  # noqa: E402


QUESTIONS = [
    ("Q1", "Fais un tournoi sans bruit entre TFT, rancunier et toujours_D sur 200 manches avec la graine 0 et donne le classement."),
    ("Q2", "Quels sont les seuils d'actualisation du rancunier et de TFT pour T=5, R=3, P=1, S=0 ?"),
    ("Q3", "Que devient une population des six stratégies avec un bruit de 5 % sur 200 générations ?"),
    ("Q4", "Compare le classement des six stratégies sans bruit puis avec un bruit de 1 %, sur 200 manches."),
    ("Q5", "Quelle est la capitale de la France ? Réponds sans outil."),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modele", default="llama3.1")
    ap.add_argument("--essais", type=int, default=3)
    ap.add_argument("--questions", default=None, help="liste d'identifiants séparés par des virgules (par défaut : toutes)")
    ap.add_argument("--ajouter", action="store_true", help="ajoute à la fin du fichier (reprise) au lieu de l'écraser")
    a = ap.parse_args()
    sortie = os.path.join(RACINE, "resultats", f"agent_{a.modele}.jsonl")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    agent = construire_agent(nom_modele=a.modele)
    choisies = set(a.questions.split(",")) if a.questions else None
    with open(sortie, "a" if a.ajouter else "w", encoding="utf-8") as f:
        for qid, question in QUESTIONS:
            if choisies and qid not in choisies:
                continue
            for essai in range(1, a.essais + 1):
                t0 = time.time()
                try:
                    messages = interroger(agent, question, verbose=True)
                    appels = [(c["name"], c["args"]) for m in messages for c in (getattr(m, "tool_calls", None) or [])]
                    erreurs_outil = [json.loads(m.content).get("erreur") for m in messages
                                     if m.type == "tool" and str(m.content).startswith('{"erreur"')]
                    final = next((m.content for m in reversed(messages) if m.type == "ai" and m.content), "")
                    ligne = {"modele": a.modele, "question_id": qid, "essai": essai, "reprise": a.ajouter, "appels_outils": appels,
                             "erreurs_outil": erreurs_outil, "controle_ok": controle(qid, appels), "reponse": final,
                             "duree_s": round(time.time() - t0, 1)}
                except Exception as e:      # noqa: BLE001 : on consigne l'échec au lieu de l'ignorer
                    ligne = {"modele": a.modele, "question_id": qid, "essai": essai, "reprise": a.ajouter, "exception": repr(e),
                             "controle_ok": False, "duree_s": round(time.time() - t0, 1)}
                f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
                f.flush()
                print(f"== {qid} essai {essai} : contrôle {'OK' if ligne['controle_ok'] else 'ÉCHEC'} ({ligne['duree_s']} s)",
                      flush=True)
    print("terminé :", sortie)


if __name__ == "__main__":
    main()
