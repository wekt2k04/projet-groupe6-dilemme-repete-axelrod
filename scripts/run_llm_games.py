# -*- coding: utf-8 -*-
"""Joue des parties du dilemme répété entre un agent LLM (Ollama) et une stratégie classique ; écrit un JSONL.

Usage depuis la racine du dépôt (Ollama lancé, modèle téléchargé) :
    python scripts/run_llm_games.py --modele llama3.1 --horizon annonce --parties 10 --manches 10 --adversaire TFT
    python scripts/run_llm_games.py --modele qwen2.5  --horizon non     --parties 10 --manches 10 --adversaire TFT

Chaque ligne du fichier est une partie (coups exécutés, scores moyens par manche, compteur de réponses sans « CHOIX : »,
réponses brutes) ; la première ligne décrit la configuration et la version du modèle. Le script reprend où il s'est
arrêté si le fichier existe déjà. Durée estimée sur un CPU de portable : 4 à 8 s par coup, soit 7 à 10 minutes par
configuration de 10 parties de 10 manches (mesuré ; environ 30 s sur un GPU T4). Aucun texte de modèle n'est exécuté ; Ollama doit n'écouter que sur 127.0.0.1.
"""
import argparse
import json
import os
import platform
import random
import sys
import time
import urllib.request
from datetime import datetime

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

from jeux import match_detail, strategie_par_nom  # noqa: E402
from joueur_llm import JoueurLLM  # noqa: E402

URL = "http://127.0.0.1:11434"


def infos_modele(nom):
    """Version du serveur et empreinte du modèle (pour tracer exactement ce qui a joué)."""
    def get(chemin):
        with urllib.request.urlopen(URL + chemin, timeout=15) as r:
            return json.loads(r.read())
    try:
        version = get("/api/version")["version"]
        modeles = {m["name"]: m for m in get("/api/tags")["models"]}
        m = modeles.get(nom) or modeles.get(nom + ":latest") or {}
        return {"serveur_ollama": version, "digest": m.get("digest"), "taille_octets": m.get("size")}
    except OSError as e:
        sys.exit(f"Ollama ne répond pas sur {URL} : {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modele", default="llama3.1")
    ap.add_argument("--horizon", choices=["annonce", "non"], required=True)
    ap.add_argument("--parties", type=int, default=10)
    ap.add_argument("--manches", type=int, default=10)
    ap.add_argument("--adversaire", default="TFT")
    ap.add_argument("--seed-base", type=int, default=1000)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--sortie", default=None)
    ap.add_argument("--materiel", default="non précisé", help="machine utilisée (consignée dans le fichier de résultats)")
    a = ap.parse_args()
    sortie = a.sortie or os.path.join(RACINE, "resultats", f"llm_{a.modele}_{a.horizon}_{a.adversaire}.jsonl")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    adversaire = strategie_par_nom(a.adversaire)
    deja = set()
    if os.path.exists(sortie):
        with open(sortie, encoding="utf-8") as f:
            for ligne in f:
                d = json.loads(ligne)
                if "partie" in d:
                    deja.add(d["partie"])
    else:
        meta = {"meta": True, "modele": a.modele, **infos_modele(a.modele), "horizon_annonce": a.horizon == "annonce",
                "adversaire": a.adversaire, "manches": a.manches, "temperature": a.temperature, "seed_base": a.seed_base,
                "num_predict": 100, "materiel": a.materiel, "date": datetime.now().isoformat(timespec="seconds"), "python": platform.python_version()}
        with open(sortie, "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
    from langchain_ollama import ChatOllama
    for k in range(a.parties):
        if k in deja:
            continue
        modele = ChatOllama(model=a.modele, base_url=URL, temperature=a.temperature, seed=a.seed_base + k,
                            num_predict=100, client_kwargs={"timeout": 300})
        joueur = JoueurLLM(modele, a.manches, a.horizon == "annonce", nom=a.modele)
        t0 = time.time()
        s_llm, s_adv, h_llm, h_adv = match_detail(joueur, adversaire, a.manches, 0.0, random.Random(a.seed_base + k))
        ligne = {"partie": k, "seed": a.seed_base + k, "score_llm": s_llm, "score_adv": s_adv, "h_llm": h_llm,
                 "h_adv": h_adv, "appels": joueur.appels, "defauts": joueur.defauts,
                 "reponses": [r[1] for r in joueur.reponses], "duree_s": round(time.time() - t0, 1)}
        with open(sortie, "a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
        print(f"partie {k + 1}/{a.parties} : coups LLM {''.join(h_llm)}  scores ({s_llm:.2f} ; {s_adv:.2f})  "
              f"hors format {joueur.defauts}/{joueur.appels}  {ligne['duree_s']} s", flush=True)
    print("terminé :", sortie)


if __name__ == "__main__":
    main()
