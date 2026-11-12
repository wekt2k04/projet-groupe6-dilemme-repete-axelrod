# -*- coding: utf-8 -*-
"""Outils @tool et agent LangChain du projet 6 (dilemme répété).

Ce module étend l'agent du cours. Le code du cours (agent_tj_sma.py et ses 10 outils) n'étant pas dans nos supports,
l'agent est reconstruit d'après les conventions du guide : outils à types annotés, docstring claire, sortie JSON,
paramètres plafonnés, conversion NumPy par `_json`. Les nouveaux outils sont `tournoi_axelrod`, `replicateur`
et `seuils_actualisation`.

Sécurité : les outils reçoivent des données (noms de stratégies pris dans une liste fermée, nombres bornés),
jamais du code ; aucun eval ni exec n'est utilisé nulle part sur un texte venant d'un modèle.
"""
import json
import os

import numpy as np
from langchain_core.tools import tool

from jeux import (STRATEGIES, STRATEGIES_ETENDUES, est_un_dilemme, replicateur as _replicateur_pur, seuil_rancunier,
                  seuil_tft, tournoi as _tournoi)

PLAFOND_MANCHES = 1000
PLAFOND_GENERATIONS = 2000
PLAFOND_REPETITIONS = 20
PLAFOND_STRATEGIES = len(STRATEGIES_ETENDUES)


def _json(objet):
    """Sérialise en JSON en convertissant les types NumPy (évite le TypeError des types non natifs)."""
    def convertir(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(f"type non sérialisable : {type(o)}")
    return json.dumps(objet, ensure_ascii=False, default=convertir)


def _erreur(message):
    return _json({"erreur": message})


def _plafonner(valeur, minimum, plafond, nom, avertissements):
    """Ramène `valeur` dans [minimum, plafond] et consigne l'ajustement dans `avertissements`."""
    ajustee = max(minimum, min(int(valeur), plafond))
    if ajustee != valeur:
        avertissements.append(f"{nom} ramené de {valeur} à {ajustee} (plafond {plafond})")
    return ajustee


def _preparer(strategies, manches, bruit, seed, repetitions):
    """Valide et plafonne les paramètres communs. Renvoie (dictionnaire de stratégies, paramètres, avertissements)."""
    avertissements = []
    if not isinstance(strategies, (list, tuple)):
        raise ValueError("strategies doit être une liste de noms")
    noms = list(strategies) or list(STRATEGIES)
    if len(noms) != len(set(noms)):
        raise ValueError("noms de stratégies en double")
    inconnus = [n for n in noms if n not in STRATEGIES_ETENDUES]
    if inconnus:
        raise ValueError(f"stratégie(s) inconnue(s) : {inconnus} ; connues : {sorted(STRATEGIES_ETENDUES)}")
    if len(noms) > PLAFOND_STRATEGIES:
        raise ValueError(f"au plus {PLAFOND_STRATEGIES} stratégies")
    if not 0 <= float(bruit) <= 1:
        raise ValueError("bruit doit être dans [0, 1]")
    params = {
        "manches": _plafonner(manches, 1, PLAFOND_MANCHES, "manches", avertissements),
        "bruit": float(bruit),
        "seed": int(seed),
        "repetitions": _plafonner(repetitions, 1, PLAFOND_REPETITIONS, "repetitions", avertissements),
    }
    return {n: STRATEGIES_ETENDUES[n] for n in noms}, params, avertissements


@tool
def tournoi_axelrod(strategies: list[str], manches: int = 200, bruit: float = 0.0, seed: int = 0,
                    repetitions: int = 1) -> str:
    """Simule un tournoi d'Axelrod du dilemme du prisonnier répété entre des stratégies connues.

    Joue toutes les paires, y compris une stratégie contre elle-même (score d'auto-jeu = moyenne des deux côtés).
    Gains par manche : T=5, R=3, P=1, S=0. Les scores sont des gains moyens PAR MANCHE.
    Args:
        strategies: noms parmi toujours_C, toujours_D, TFT, rancunier, Pavlov, aleatoire, TFT_genereux ;
            une liste vide signifie les six stratégies du guide.
        manches: nombre de manches par rencontre (plafonné à 1000).
        bruit: probabilité epsilon, dans [0, 1], qu'un coup soit inversé, pour chaque joueur et chaque manche.
        seed: graine du générateur aléatoire (reproductibilité).
        repetitions: nombre de rencontres moyennées par paire (plafonné à 20).
    Returns: JSON avec noms, matrice[i][j] (score moyen de i contre j), classement et paramètres effectifs.
    """
    try:
        dico, p, avert = _preparer(strategies, manches, bruit, seed, repetitions)
        noms, M, classement = _tournoi(dico, manches=p["manches"], bruit=p["bruit"], seed=p["seed"],
                                       repetitions=p["repetitions"])
    except ValueError as e:
        return _erreur(str(e))
    return _json({"outil": "tournoi_axelrod", "parametres": p, "noms": noms, "matrice": M,
                  "classement": [{"strategie": n, "score_moyen": v} for n, v in classement],
                  "avertissements": avert})


@tool("replicateur")
def replicateur_outil(strategies: list[str], generations: int = 200, manches: int = 200, bruit: float = 0.0,
                      seed: int = 0, repetitions: int = 5) -> str:
    """Fait évoluer une population de stratégies par la dynamique du réplicateur, à partir de parts égales.

    La matrice des scores moyens par manche vient d'un tournoi (mêmes conventions que tournoi_axelrod) ;
    puis x_i(t+1) = x_i(t) f_i / f_moyen avec f = M x. Les parts restent positives et de somme 1.
    Args:
        strategies: noms de stratégies connues (liste vide = les six du guide).
        generations: nombre de générations (plafonné à 2000).
        manches: manches par rencontre du tournoi (plafonné à 1000).
        bruit: probabilité epsilon dans [0, 1] ; seed: graine ; repetitions: rencontres moyennées (plafonné à 20).
    Returns: JSON avec les parts finales, quelques points de la trajectoire et les paramètres effectifs.
    """
    try:
        dico, p, avert = _preparer(strategies, manches, bruit, seed, repetitions)
        g = _plafonner(generations, 1, PLAFOND_GENERATIONS, "generations", avert)
        noms, M, _ = _tournoi(dico, manches=p["manches"], bruit=p["bruit"], seed=p["seed"], repetitions=p["repetitions"])
        traj = _replicateur_pur(M, np.ones(len(noms)) / len(noms), g)
    except ValueError as e:
        return _erreur(str(e))
    points = sorted(set(int(round(k)) for k in np.linspace(0, g, 11)))
    return _json({"outil": "replicateur", "parametres": {**p, "generations": g}, "noms": noms,
                  "parts_finales": dict(zip(noms, traj[-1])),
                  "trajectoire": {str(t): dict(zip(noms, traj[t])) for t in points},
                  "somme_parts_finales": float(traj[-1].sum()), "avertissements": avert})


@tool
def seuils_actualisation(t: float = 5.0, r: float = 3.0, p: float = 1.0, s: float = 0.0) -> str:
    """Calcule les seuils d'actualisation delta au-delà desquels la coopération est stable à horizon indéterminé.

    Args:
        t: gain de la tentation (trahir un coopérateur), 5 par défaut ; r: récompense de la coopération mutuelle (3) ;
        p: punition de la trahison mutuelle (1) ; s: gain du naïf (0).
    Returns: JSON avec la condition du dilemme (T > R > P > S et 2R > T + S), le seuil du rancunier
        (T-R)/(T-P) et le seuil de TFT, plus grand de (T-R)/(T-P) et (T-R)/(R-S).
    """
    dilemme = est_un_dilemme(t, r, p, s)
    if not dilemme:
        return _json({"outil": "seuils_actualisation", "dilemme": False,
                      "message": "Les gains ne vérifient pas T > R > P > S et 2R > T + S : ce n'est pas un dilemme répété."})
    return _json({"outil": "seuils_actualisation", "dilemme": True, "gains": {"T": t, "R": r, "P": p, "S": s},
                  "seuil_rancunier": seuil_rancunier(t, r, p), "seuil_tft": seuil_tft(t, r, p, s)})


OUTILS = [tournoi_axelrod, replicateur_outil, seuils_actualisation]

SYSTEM_PROMPT = (
    "Tu es un assistant de théorie des jeux spécialisé dans le dilemme du prisonnier répété. "
    "Règle n°1 : pour tout résultat chiffré sur un tournoi, une population ou un seuil d'actualisation, appelle l'outil "
    "correspondant (tournoi_axelrod, replicateur, seuils_actualisation) et ne donne jamais un chiffre de mémoire. "
    "Règle n°2 : les stratégies s'écrivent exactement toujours_C, toujours_D, TFT, rancunier, Pavlov, aleatoire, "
    "TFT_genereux. Règle n°3 : les scores sont des gains moyens par manche ; indique les paramètres utilisés (manches, "
    "bruit, graine). Règle n°4 : si un outil renvoie une erreur ou un avertissement, dis-le. Réponds en français, brièvement."
)


def construire_agent(modele=None, nom_modele=None):
    """Construit l'agent LangChain. Sans `modele`, utilise Ollama local (127.0.0.1) avec OLLAMA_MODEL (llama3.1 par défaut)."""
    from langchain.agents import create_agent
    if modele is None:
        from langchain_ollama import ChatOllama
        modele = ChatOllama(model=nom_modele or os.getenv("OLLAMA_MODEL", "llama3.1"),
                            base_url="http://127.0.0.1:11434", temperature=0)
    return create_agent(modele, OUTILS, system_prompt=SYSTEM_PROMPT)


def interroger(agent, question, verbose=True):
    """Pose une question à l'agent et renvoie la liste des messages ; avec verbose=True, affiche chaque appel d'outil."""
    messages = agent.invoke({"messages": [{"role": "user", "content": question}]})["messages"]
    if verbose:
        for m in messages:
            for appel in getattr(m, "tool_calls", None) or []:
                print(f"[appel d'outil] {appel['name']}({appel['args']})")
            if m.type == "tool":
                print(f"[résultat de {m.name}] {str(m.content)[:300]}")
            elif m.type == "ai" and m.content:
                print(f"[réponse] {m.content}")
    return messages
