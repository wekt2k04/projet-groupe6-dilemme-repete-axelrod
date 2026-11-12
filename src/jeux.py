# -*- coding: utf-8 -*-
"""Projet 6 (Groupe 6) : dilemme du prisonnier répété, tournoi d'Axelrod, bruit, réplicateur.

Fonctions pures, sans LangChain. Conventions du groupe (à documenter dans le rapport) :
- coups : 'C' (coopérer) et 'D' (trahir) ; gains T=5, R=3, P=1, S=0 ;
- une stratégie est une fonction (mon_historique, historique_adverse, rng) -> 'C' ou 'D' ;
- les historiques contiennent les coups EXÉCUTÉS (après bruit), vus par les deux joueurs ;
- bruit : chaque coup de CHAQUE joueur est inversé indépendamment avec la probabilité `bruit` ;
- tournoi : toutes les paires, y compris une stratégie contre elle-même (score = moyenne des deux côtés) ;
- scores = gain moyen PAR MANCHE (jamais de totaux sur des nombres de manches différents).
"""
import random

import numpy as np

T, R, P, S = 5, 3, 1, 0
GAINS = {("C", "C"): (R, R), ("C", "D"): (S, T), ("D", "C"): (T, S), ("D", "D"): (P, P)}


def toujours_C(h, g, rng):
    return "C"


def toujours_D(h, g, rng):
    return "D"


def tft(h, g, rng):
    """Tit-for-tat : coopère au premier coup, puis copie le dernier coup de l'adversaire."""
    return g[-1] if g else "C"


def rancunier(h, g, rng):
    """Grim trigger : coopère tant que l'adversaire n'a jamais trahi, puis trahit pour toujours."""
    return "D" if "D" in g else "C"


def pavlov(h, g, rng):
    """Win-stay, lose-shift : coopère si les deux ont joué pareil au tour précédent."""
    return "C" if not h or h[-1] == g[-1] else "D"


def aleatoire(h, g, rng):
    return "C" if rng.random() < 0.5 else "D"


def tft_genereux(pardon=1 / 3):
    """TFT qui pardonne une trahison avec la probabilité `pardon`."""
    def strategie(h, g, rng):
        if g and g[-1] == "D":
            return "C" if rng.random() < pardon else "D"
        return "C"
    return strategie


STRATEGIES = {"toujours_C": toujours_C, "toujours_D": toujours_D, "TFT": tft,
              "rancunier": rancunier, "Pavlov": pavlov, "aleatoire": aleatoire}


def _inverse(coup):
    return "D" if coup == "C" else "C"


def match(s1, s2, manches=200, bruit=0.0, rng=None):
    """Joue `manches` manches ; renvoie les scores moyens par manche (joueur 1, joueur 2)."""
    rng = rng or random.Random(0)
    h1, h2, t1, t2 = [], [], 0, 0
    for _ in range(manches):
        a1, a2 = s1(h1, h2, rng), s2(h2, h1, rng)
        if rng.random() < bruit:
            a1 = _inverse(a1)
        if rng.random() < bruit:
            a2 = _inverse(a2)
        g1, g2 = GAINS[(a1, a2)]
        t1, t2 = t1 + g1, t2 + g2
        h1.append(a1)
        h2.append(a2)
    return t1 / manches, t2 / manches


def tournoi(strategies=None, manches=200, bruit=0.0, seed=42, repetitions=1):
    """Toutes les paires (soi-même inclus). Renvoie (noms, matrice M, classement).
    M[i][j] = score moyen par manche de i contre j ; classement = [(nom, score moyen sur les adversaires)]."""
    strategies = strategies or STRATEGIES
    noms = list(strategies)
    n, rng = len(noms), random.Random(seed)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            tot1 = tot2 = 0.0
            for _ in range(repetitions):
                a, b = match(strategies[noms[i]], strategies[noms[j]], manches, bruit, rng)
                tot1, tot2 = tot1 + a, tot2 + b
            if i == j:
                M[i][i] = (tot1 + tot2) / (2 * repetitions)
            else:
                M[i][j], M[j][i] = tot1 / repetitions, tot2 / repetitions
    moyennes = M.mean(axis=1)
    classement = sorted(zip(noms, moyennes), key=lambda t: -t[1])
    return noms, M, classement


def replicateur(M, x0, generations):
    """Dynamique du réplicateur : x_i(t+1) = x_i(t) f_i / f_moyen, avec f = M x. Renvoie la trajectoire."""
    x = np.array(x0, dtype=float)
    x = x / x.sum()
    traj = [x.copy()]
    for _ in range(generations):
        f = M @ x
        x = x * f / (x @ f)
        traj.append(x.copy())
    return np.array(traj)


def seuil_rancunier(t=T, r=R, p=P):
    """Seuil d'actualisation du rancunier : coopérer est stable si delta >= (T - R) / (T - P)."""
    return (t - r) / (t - p)


def match_arret_aleatoire(delta, rng):
    """Longueur d'une partie qui continue avec la probabilité delta après chaque manche."""
    n = 1
    while rng.random() < delta:
        n += 1
    return n
