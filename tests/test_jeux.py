# -*- coding: utf-8 -*-
"""Tests du projet 6 (fonctions pures). Lancer depuis la racine du dépôt : python -m pytest"""
import random

import numpy as np
import pytest

from jeux import (STRATEGIES, STRATEGIES_ETENDUES, aleatoire, ecart_deviation_rancunier,
                  ecart_theorique_rancunier, est_un_dilemme, longueur_arret_aleatoire, match, match_detail,
                  pavlov, rancunier, replicateur, seuil_rancunier, seuil_tft, strategie_par_nom, tft,
                  tft_genereux, toujours_C, toujours_D, tournoi)


# ---- valeurs données par le guide -------------------------------------------------------------
def test_tft_contre_tft_sans_bruit():
    assert match(tft, tft, 200, 0.0, random.Random(1)) == (3, 3)


def test_trahir_contre_cooperer():
    assert match(toujours_D, toujours_C, 200, 0.0, random.Random(1)) == (5, 0)


def test_tft_contre_toujours_trahir_perd_seulement_la_premiere_manche():
    m1, m2, h1, h2 = match_detail(tft, toujours_D, 200, 0.0, random.Random(1))
    assert h1[0] == "C" and set(h1[1:]) == {"D"}
    assert (m1 * 200, m2 * 200) == (0 + 199 * 1, 5 + 199 * 1)


def test_condition_du_dilemme():
    assert est_un_dilemme()
    assert not est_un_dilemme(t=5, r=2, p=1, s=0)   # 2R = 4 < T + S = 5 : l'alternance bat la coopération


# ---- valeurs calculées à la main (sans bruit, 200 manches) ------------------------------------
@pytest.mark.parametrize("s1,s2,attendu", [
    (pavlov, toujours_D, (0.5, 3.0)),        # C,D,C,D... contre D : 0,1,0,1 -> 0,5 ; 5,1,5,1 -> 3
    (rancunier, toujours_D, (0.995, 1.02)),  # perd seulement la 1re manche
    (rancunier, tft, (3, 3)),
    (pavlov, pavlov, (3, 3)),
    (toujours_C, toujours_C, (3, 3)),
    (toujours_D, toujours_D, (1, 1)),
])
def test_valeurs_a_la_main(s1, s2, attendu):
    assert match(s1, s2, 200, 0.0, random.Random(1)) == pytest.approx(attendu)


# ---- bruit -----------------------------------------------------------------------------------
def test_bruit_applique_aux_deux_joueurs():
    _, _, h1, h2 = match_detail(toujours_C, toujours_C, 4000, 0.2, random.Random(3))
    f1, f2 = h1.count("D") / 4000, h2.count("D") / 4000
    assert abs(f1 - 0.2) < 0.03 and abs(f2 - 0.2) < 0.03      # les DEUX côtés sont perturbés


def test_bruit_total_inverse_tous_les_coups():
    _, _, h1, h2 = match_detail(toujours_C, toujours_D, 50, 1.0, random.Random(3))
    assert set(h1) == {"D"} and set(h2) == {"C"}


def test_historiques_contiennent_les_coups_executes():
    """Avec bruit, TFT copie le coup exécuté (pas le coup voulu) de l'adversaire."""
    _, _, h1, h2 = match_detail(tft, toujours_C, 300, 0.3, random.Random(11))
    voulus = ["C"] + h2[:-1]                  # ce que TFT voulait jouer
    ecarts = sum(a != b for a, b in zip(h1, voulus)) / 300
    assert 0.2 < ecarts < 0.4                 # environ 30 % d'inversions


def test_validation_des_entrees():
    with pytest.raises(ValueError):
        match(tft, tft, 0)
    with pytest.raises(ValueError):
        match(tft, tft, 10, 1.5)
    with pytest.raises(ValueError):
        strategie_par_nom("__import__('os')")
    with pytest.raises(ValueError):
        tft_genereux(2)


# ---- tournoi ---------------------------------------------------------------------------------
def test_reproductibilite():
    assert tournoi(seed=7, bruit=0.05)[1].tolist() == tournoi(seed=7, bruit=0.05)[1].tolist()
    assert tournoi(seed=7, bruit=0.05)[1].tolist() != tournoi(seed=8, bruit=0.05)[1].tolist()


def test_matrice_sans_bruit_et_convention_d_auto_jeu():
    noms, M, classement = tournoi(manches=200, bruit=0.0, seed=0)
    assert noms == list(STRATEGIES) and M.shape == (6, 6)
    i = {n: k for k, n in enumerate(noms)}
    assert M[i["TFT"], i["TFT"]] == 3 and M[i["toujours_D"], i["toujours_D"]] == 1   # auto-jeu : moyenne des 2 côtés
    assert M[i["toujours_D"], i["toujours_C"]] == 5 and M[i["toujours_C"], i["toujours_D"]] == 0
    assert M[i["TFT"], i["toujours_D"]] == pytest.approx(0.995)
    assert classement[0][0] == "rancunier" or classement[0][0] == "TFT"
    assert [c[1] for c in classement] == sorted((c[1] for c in classement), reverse=True)


def test_auto_jeu_est_la_moyenne_des_deux_cotes():
    # aleatoire contre elle-même : les deux côtés ont des scores différents ; M[i][i] doit être leur moyenne
    rng = random.Random(0)
    a, b = match(aleatoire, aleatoire, 200, 0.0, rng)
    _, M, _ = tournoi({"alea": aleatoire}, manches=200, seed=0)
    rng = random.Random(0)
    a2, b2 = match(aleatoire, aleatoire, 200, 0.0, rng)
    assert M[0][0] == pytest.approx((a2 + b2) / 2) and (a, b) == (a2, b2)


def test_scores_par_manche_independants_de_l_horizon():
    _, M50, _ = tournoi({"TFT": tft, "toujours_C": toujours_C}, manches=50)
    _, M200, _ = tournoi({"TFT": tft, "toujours_C": toujours_C}, manches=200)
    assert np.allclose(M50, M200)             # sans bruit, déterministe : même score moyen par manche


# ---- réplicateur -----------------------------------------------------------------------------
def test_replicateur_parts_positives_somme_1():
    _, M, _ = tournoi(bruit=0.01, repetitions=3)
    traj = replicateur(M, np.ones(6) / 6, 200)
    assert traj.shape == (201, 6) and (traj >= 0).all() and np.allclose(traj.sum(axis=1), 1)


def test_replicateur_point_fixe_et_domination():
    M = np.array([[3.0, 0.5], [5.0, 1.0]])    # la 2e stratégie domine : sa part tend vers 1
    traj = replicateur(M, [0.9, 0.1], 400)
    assert traj[-1, 1] > 0.99
    assert np.allclose(replicateur(M, [1, 0], 5)[-1], [1, 0])     # une part nulle le reste


def test_replicateur_refuse_les_entrees_invalides():
    with pytest.raises(ValueError):
        replicateur(np.ones((2, 3)), [1, 1], 3)
    with pytest.raises(ValueError):
        replicateur(np.zeros((2, 2)), [1, 1], 3)           # score moyen nul
    with pytest.raises(ValueError):
        replicateur(-np.ones((2, 2)), [1, 1], 3)           # scores négatifs
    assert replicateur(np.array([[3.0, 0.0], [5.0, 1.0]]), [1, 1], 3).shape == (4, 2)   # zéros autorisés


# ---- horizon indéterminé ---------------------------------------------------------------------
def test_seuils():
    assert seuil_rancunier() == 0.5
    assert seuil_tft() == pytest.approx(2 / 3)


def test_seuil_un_demi_par_arret_aleatoire():
    """Le seuil δ = 1/2 du rancunier est retrouvé par une partie à arrêt aléatoire."""
    m_bas, e_bas = ecart_deviation_rancunier(0.4)
    m_pile, e_pile = ecart_deviation_rancunier(0.5)
    m_haut, e_haut = ecart_deviation_rancunier(0.6)
    assert m_bas > 4 * e_bas            # δ < 1/2 : dévier rapporte
    assert m_haut < -4 * e_haut         # δ > 1/2 : coopérer rapporte plus
    assert abs(m_pile) < 4 * e_pile     # δ = 1/2 : indifférence
    for d, m, e in ((0.4, m_bas, e_bas), (0.6, m_haut, e_haut)):
        assert abs(m - ecart_theorique_rancunier(d)) < 4 * e


def test_longueur_arret_aleatoire():
    rng = random.Random(0)
    moyenne = np.mean([longueur_arret_aleatoire(0.75, rng) for _ in range(20000)])
    assert moyenne == pytest.approx(4.0, rel=0.05)     # E[L] = 1 / (1 - delta)
    with pytest.raises(ValueError):
        longueur_arret_aleatoire(1.0, rng)


def test_strategies_declarees():
    assert set(STRATEGIES) == {"toujours_C", "toujours_D", "TFT", "rancunier", "Pavlov", "aleatoire"}
    assert "TFT_genereux" in STRATEGIES_ETENDUES
