# -*- coding: utf-8 -*-
"""Projet 6 (groupe 6) : dilemme du prisonnier répété, tournoi d'Axelrod, bruit, réplicateur.

Module de fonctions pures, sans LangChain. Conventions du groupe (voir CONVENTIONS.md) :

- coups : 'C' (coopérer) et 'D' (trahir) ; gains par manche T=5, R=3, P=1, S=0 ;
- une stratégie est une fonction (mon_historique, historique_adverse, rng) -> 'C' ou 'D' ;
  un joueur LLM suit la même signature, ce qui permet de réutiliser `match` ;
- les historiques contiennent les coups EXÉCUTÉS (après bruit), vus par les deux joueurs ;
- bruit : chaque coup de CHAQUE joueur est inversé indépendamment avec la probabilité `bruit` ;
- tournoi : toutes les paires, y compris une stratégie contre elle-même (auto-jeu) ;
  le score d'auto-jeu est la moyenne des deux côtés ;
- tous les scores sont des gains moyens PAR MANCHE (jamais de totaux sur des horizons différents).
"""
import random

import numpy as np

T, R, P, S = 5, 3, 1, 0
GAINS = {("C", "C"): (R, R), ("C", "D"): (S, T), ("D", "C"): (T, S), ("D", "D"): (P, P)}
COUPS = ("C", "D")


def est_un_dilemme(t=T, r=R, p=P, s=S):
    """Condition du dilemme du prisonnier répété : T > R > P > S et 2R > T + S."""
    return t > r > p > s and 2 * r > t + s


# --------------------------------------------------------------------------- stratégies
def toujours_C(h, g, rng):
    """Coopère toujours."""
    return "C"


def toujours_D(h, g, rng):
    """Trahit toujours."""
    return "D"


def tft(h, g, rng):
    """Tit-for-tat : coopère au premier coup, puis copie le dernier coup de l'adversaire."""
    return g[-1] if g else "C"


def rancunier(h, g, rng):
    """Grim trigger : coopère tant que l'adversaire n'a jamais trahi, puis trahit pour toujours."""
    return "D" if "D" in g else "C"


def pavlov(h, g, rng):
    """Win-stay, lose-shift : coopère au premier coup, puis si les deux ont joué pareil au tour précédent."""
    return "C" if not h or h[-1] == g[-1] else "D"


def aleatoire(h, g, rng):
    """Coopère avec la probabilité 1/2."""
    return "C" if rng.random() < 0.5 else "D"


def tft_genereux(pardon=1 / 3):
    """TFT qui pardonne une trahison avec la probabilité `pardon` (0 <= pardon <= 1)."""
    if not 0 <= pardon <= 1:
        raise ValueError("pardon doit être dans [0, 1]")

    def strategie(h, g, rng):
        if g and g[-1] == "D":
            return "C" if rng.random() < pardon else "D"
        return "C"
    return strategie


STRATEGIES = {"toujours_C": toujours_C, "toujours_D": toujours_D, "TFT": tft,
              "rancunier": rancunier, "Pavlov": pavlov, "aleatoire": aleatoire}
STRATEGIES_ETENDUES = {**STRATEGIES, "TFT_genereux": tft_genereux()}


def strategie_par_nom(nom):
    """Renvoie la fonction d'une stratégie connue ; refuse tout autre nom (jamais de code évalué)."""
    if nom not in STRATEGIES_ETENDUES:
        raise ValueError(f"stratégie inconnue : {nom!r} ; connues : {sorted(STRATEGIES_ETENDUES)}")
    return STRATEGIES_ETENDUES[nom]


# --------------------------------------------------------------------------- parties
def _inverse(coup):
    return "D" if coup == "C" else "C"


def match_detail(s1, s2, manches=200, bruit=0.0, rng=None):
    """Joue `manches` manches. Renvoie (score_moyen_1, score_moyen_2, historique_1, historique_2).

    Le bruit est tiré séparément pour chaque joueur et chaque manche ; les historiques sont ceux des coups exécutés."""
    if manches < 1:
        raise ValueError("manches doit être >= 1")
    if not 0 <= bruit <= 1:
        raise ValueError("bruit doit être dans [0, 1]")
    rng = rng if rng is not None else random.Random(0)
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
    return t1 / manches, t2 / manches, h1, h2


def match(s1, s2, manches=200, bruit=0.0, rng=None):
    """Scores moyens par manche (joueur 1, joueur 2) d'une rencontre de `manches` manches."""
    m1, m2, _, _ = match_detail(s1, s2, manches, bruit, rng)
    return m1, m2


def tournoi(strategies=None, manches=200, bruit=0.0, seed=0, repetitions=1):
    """Tournoi à toutes les paires, auto-jeu compris.

    Renvoie (noms, M, classement) : M[i][j] = score moyen par manche de i contre j (M[i][i] = moyenne des deux
    côtés de l'auto-jeu) ; classement = [(nom, score moyen sur les adversaires)] trié par ordre décroissant."""
    strategies = strategies if strategies is not None else STRATEGIES
    if repetitions < 1:
        raise ValueError("repetitions doit être >= 1")
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


def replicateur(scores, x0, generations):
    """Dynamique du réplicateur : x_i(t+1) = x_i(t) f_i / f_moyen, avec f = M x.

    `scores` est la matrice du tournoi (scores moyens >= 0, la moyenne de la population doit rester > 0). Renvoie la trajectoire,
    un tableau (generations + 1, n) dont chaque ligne est positive et de somme 1."""
    M = np.asarray(scores, dtype=float)
    x = np.asarray(x0, dtype=float)
    if M.ndim != 2 or M.shape[0] != M.shape[1] or x.shape != (M.shape[0],):
        raise ValueError("scores doit être carrée n x n et x0 de longueur n")
    if (x < 0).any() or x.sum() <= 0 or (M < 0).any():
        raise ValueError("x0 doit être positif non nul et les scores positifs ou nuls")
    x = x / x.sum()
    traj = [x.copy()]
    for _ in range(int(generations)):
        f = M @ x
        moyenne = x @ f
        if moyenne <= 0:
            raise ValueError("score moyen de la population nul : réplicateur non défini")
        x = x * f / moyenne
        traj.append(x.copy())
    return np.array(traj)


# --------------------------------------------------------------------------- horizon indéterminé
def seuil_rancunier(t=T, r=R, p=P):
    """Seuil d'actualisation du rancunier : coopérer est stable si delta >= (T - R) / (T - P)."""
    return (t - r) / (t - p)


def seuil_tft(t=T, r=R, p=P, s=S):
    """Seuil d'actualisation de TFT contre les deux déviations testées.

    Trahir toujours demande delta >= (T-R)/(T-P) ; alterner trahir/coopérer (T, S, T, S, ...)
    demande delta >= (T-R)/(R-S). Le seuil de TFT est le plus grand des deux."""
    return max((t - r) / (t - p), (t - r) / (r - s))


def longueur_arret_aleatoire(delta, rng):
    """Longueur d'une partie qui continue avec la probabilité delta après chaque manche (loi géométrique)."""
    if not 0 <= delta < 1:
        raise ValueError("delta doit être dans [0, 1[")
    n = 1
    while rng.random() < delta:
        n += 1
    return n


match_arret_aleatoire = longueur_arret_aleatoire  # nom du prototype S1, conservé


def ecart_deviation_rancunier(delta, parties=60000, seed=5):
    """Estimation Monte-Carlo de « gain en déviant - gain en coopérant » contre un rancunier.

    Partie de longueur L (arrêt aléatoire) : coopérer rapporte R*L ; trahir dès la 1re manche rapporte
    T + P*(L-1). L'espérance théorique vaut T - P + (P - R) / (1 - delta), nulle exactement pour
    delta = (T-R)/(T-P). Renvoie (moyenne, erreur standard)."""
    rng = random.Random(seed)
    ecarts = np.empty(parties)
    for k in range(parties):
        L = longueur_arret_aleatoire(delta, rng)
        ecarts[k] = (T + P * (L - 1)) - R * L
    return float(ecarts.mean()), float(ecarts.std(ddof=1) / np.sqrt(parties))


def ecart_theorique_rancunier(delta):
    """Valeur exacte de l'espérance estimée par `ecart_deviation_rancunier`."""
    return T - P + (P - R) / (1 - delta)
