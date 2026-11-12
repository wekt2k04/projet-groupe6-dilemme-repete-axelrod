# -*- coding: utf-8 -*-
"""Tests du projet 6. Lancer : python -m pytest."""
import random

import numpy as np

from jeux import (STRATEGIES, aleatoire, match, match_arret_aleatoire, pavlov, rancunier, replicateur,
                  seuil_rancunier, tft, toujours_C, toujours_D, tournoi)


def test_tft_contre_tft_sans_bruit():
    assert match(tft, tft, 200, 0.0, random.Random(1)) == (3, 3)


def test_trahir_contre_cooperer():
    assert match(toujours_D, toujours_C, 200, 0.0, random.Random(1)) == (5, 0)


def test_tft_contre_toujours_trahir_perd_seulement_la_premiere_manche():
    a, b = match(tft, toujours_D, 200, 0.0, random.Random(1))
    assert (a * 200, b * 200) == (0 + 199 * 1, 5 + 199 * 1)


def test_rancunier_et_pavlov_sans_bruit():
    assert match(rancunier, tft, 50, 0.0, random.Random(1)) == (3, 3)
    assert match(pavlov, pavlov, 50, 0.0, random.Random(1)) == (3, 3)


def test_reproductibilite():
    assert tournoi(seed=7, bruit=0.05)[1].tolist() == tournoi(seed=7, bruit=0.05)[1].tolist()


def test_replicateur_parts_positives_somme_1():
    _, M, _ = tournoi(bruit=0.01, repetitions=3)
    traj = replicateur(M, np.ones(6) / 6, 200)
    assert (traj >= 0).all() and np.allclose(traj.sum(axis=1), 1)


def test_seuil_rancunier_un_demi():
    assert seuil_rancunier() == 0.5


def test_seuil_par_arret_aleatoire():
    """Écart de valeur « dévier - coopérer » contre un rancunier : 3L contre 5 + (L-1)."""
    def ecart(delta, n=60000):
        rng, e = random.Random(5), 0.0
        for _ in range(n):
            L = match_arret_aleatoire(delta, rng)
            e += (5 + (L - 1)) - 3 * L
        return e / n
    assert ecart(0.4) > 0.3 and ecart(0.6) < -0.5


if __name__ == "__main__":
    for nom, f in list(globals().items()):
        if nom.startswith("test_"):
            f()
            print("OK", nom)
