# -*- coding: utf-8 -*-
"""Protocoles d'expérience et analyse du projet 6 : tournois multi-graines et parties d'agents LLM.

Fonctions pures (sauf `charger_parties`, qui lit un JSONL). Conventions : scores en gain moyen PAR MANCHE ;
la fréquence de coopération est calculée sur les coups EXÉCUTÉS ; les réponses LLM sans « CHOIX : » reçoivent le coup
par défaut et sont comptées à part (champ `defauts`) : on rapporte toujours leur nombre avec les résultats.
Aucune conclusion ne doit reposer sur une seule partie : les intervalles de confiance rappellent la taille d'échantillon.
"""
import json
import math

import numpy as np
from scipy import stats

from jeux import STRATEGIES, replicateur, tournoi


# ----------------------------------------------------------------------------- statistiques
def intervalle_wilson(k, n, z=1.96):
    """Intervalle de confiance de Wilson à 95 % pour une proportion k/n (renvoie (bas, haut) ; (0, 1) si n = 0)."""
    if n <= 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    marge = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - marge), min(1.0, centre + marge)


def moyenne_ic(valeurs, z=1.96):
    """Moyenne et demi-largeur de l'intervalle de confiance normal (z * écart-type / racine de n)."""
    v = np.asarray(valeurs, dtype=float)
    if v.size < 2:
        return float(v.mean()) if v.size else float("nan"), float("nan")
    return float(v.mean()), float(z * v.std(ddof=1) / math.sqrt(v.size))


# ----------------------------------------------------------------------------- tournois multi-graines
def classement_multi_graines(strategies=None, bruit=0.0, graines=range(30), manches=200, repetitions=10):
    """Rejoue le tournoi pour chaque graine. Renvoie {nom: {"score": (moyenne, ic), "rang_moyen": r, "premier": fraction}}.

    La moyenne et l'intervalle portent sur les graines ; `premier` est la fraction de graines où la stratégie arrive première."""
    strategies = strategies if strategies is not None else STRATEGIES
    scores = {n: [] for n in strategies}
    rangs = {n: [] for n in strategies}
    premiers = {n: 0 for n in strategies}
    graines = list(graines)
    for g in graines:
        _, _, classement = tournoi(strategies, manches=manches, bruit=bruit, seed=g, repetitions=repetitions)
        for r, (nom, score) in enumerate(classement, 1):
            scores[nom].append(score)
            rangs[nom].append(r)
        premiers[classement[0][0]] += 1
    return {n: {"score": moyenne_ic(scores[n]), "rang_moyen": float(np.mean(rangs[n])),
                "premier": premiers[n] / len(graines)} for n in strategies}


def replicateur_multi_graines(strategies=None, bruit=0.0, graines=range(30), manches=200, repetitions=10, generations=200):
    """Parts finales du réplicateur (parts égales au départ) pour chaque graine.

    Renvoie {nom: {"part_moyenne": m, "part_ecart_type": s, "domine": fraction de graines où la part est maximale}}."""
    strategies = strategies if strategies is not None else STRATEGIES
    noms = list(strategies)
    finales = []
    for g in graines:
        _, M, _ = tournoi(strategies, manches=manches, bruit=bruit, seed=g, repetitions=repetitions)
        finales.append(replicateur(M, np.ones(len(noms)) / len(noms), generations)[-1])
    finales = np.array(finales)
    dominants = np.bincount(finales.argmax(axis=1), minlength=len(noms)) / len(finales)
    return {n: {"part_moyenne": float(finales[:, i].mean()), "part_ecart_type": float(finales[:, i].std(ddof=1)),
                "domine": float(dominants[i])} for i, n in enumerate(noms)}


# ----------------------------------------------------------------------------- parties d'agents LLM
def charger_parties(chemin):
    """Lit un JSONL produit par scripts/run_llm_games.py. Renvoie (meta, liste de parties)."""
    meta, parties = None, []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            d = json.loads(ligne)
            if d.get("meta"):
                meta = d
            else:
                parties.append(d)
    return meta, parties


def coop_par_manche(parties, cle="h_llm"):
    """Fréquence de coopération à chaque manche. Renvoie (taux, bas, haut), trois tableaux de longueur = nombre de manches."""
    H = np.array([[c == "C" for c in p[cle]] for p in parties])
    n = H.shape[0]
    taux = H.mean(axis=0)
    bornes = [intervalle_wilson(int(k), n) for k in H.sum(axis=0)]
    return taux, np.array([b[0] for b in bornes]), np.array([b[1] for b in bornes])


def bootstrap_moyenne(valeurs, repetitions=5000, seed=0):
    """Moyenne et intervalle de confiance bootstrap à 95 % (percentiles) d'un échantillon ; valeurs = une par partie."""
    v = np.asarray(valeurs, dtype=float)
    rng = np.random.default_rng(seed)
    moyennes = rng.choice(v, size=(repetitions, v.size), replace=True).mean(axis=1)
    return float(v.mean()), float(np.percentile(moyennes, 2.5)), float(np.percentile(moyennes, 97.5))


def resume_config(meta, parties):
    """Indicateurs d'une configuration (modèle, horizon) : coopération, scores moyens par manche, réponses hors format.

    L'unité statistique est la PARTIE : les coups d'une partie dépendent les uns des autres (et, à température 0,7, les parties
    d'un même modèle se répètent souvent), donc l'intervalle de la coopération globale est un bootstrap sur les parties,
    jamais un intervalle sur l'ensemble des coups. `trajectoires_distinctes` donne le nombre de séquences de coups différentes."""
    H = np.array([[c == "C" for c in p["h_llm"]] for p in parties])
    par_partie = H.mean(axis=1)
    coop, bas, haut = bootstrap_moyenne(par_partie)
    score_m, score_ic = moyenne_ic([p["score_llm"] for p in parties])
    appels = sum(p["appels"] for p in parties)
    defauts = sum(p["defauts"] for p in parties)
    return {"modele": meta["modele"], "horizon_annonce": meta["horizon_annonce"], "adversaire": meta["adversaire"],
            "parties": len(parties), "manches": H.shape[1], "coop": coop, "coop_ic95": (bas, haut),
            "trajectoires_distinctes": len({tuple(p["h_llm"]) for p in parties}),
            "coop_derniere_manche": float(H[:, -1].mean()), "coop_premiere_manche": float(H[:, 0].mean()),
            "score_moyen": score_m, "score_ic95": score_ic, "defauts": defauts, "appels": appels,
            "taux_hors_format": defauts / appels if appels else float("nan")}


def comparer_horizons(parties_annonce, parties_non):
    """Compare la coopération PAR PARTIE (unité statistique indépendante) entre horizon annoncé et non annoncé.

    Test de Mann-Whitney bilatéral ; avec 10 parties par groupe, la puissance est faible : un résultat non significatif
    ne prouve pas l'absence d'effet."""
    a = [np.mean([c == "C" for c in p["h_llm"]]) for p in parties_annonce]
    b = [np.mean([c == "C" for c in p["h_llm"]]) for p in parties_non]
    u = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {"coop_annonce": float(np.mean(a)), "coop_non_annonce": float(np.mean(b)), "U": float(u.statistic),
            "p": float(u.pvalue), "n_annonce": len(a), "n_non": len(b)}


def theorie_induction(manches):
    """Prédiction de l'induction à rebours à horizon annoncé : trahir à chaque manche (coopération nulle)."""
    return np.zeros(manches)
