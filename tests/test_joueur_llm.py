# -*- coding: utf-8 -*-
"""Tests hors ligne du joueur LLM avec le faux modèle (scripté) : la mécanique, jamais la qualité d'un vrai LLM."""
import random

import pytest

from jeux import match_detail, strategie_par_nom
from joueur_llm import (DEFAUT, JoueurLLM, analyser_reponse, formater_historique, info_horizon)
from modele_scripte import ETIQUETTE, ModeleScripte, reponse_finale


@pytest.mark.parametrize("texte,attendu", [
    ("CHOIX : COOPERER", "C"), ("CHOIX : TRAHIR", "D"), ("choix : trahir", "D"), ("CHOIX: COOPÉRER", "C"),
    ("Je réfléchis...\nCHOIX : COOPERER", "C"),
    ("CHOIX : COOPERER\npuis finalement\nCHOIX : TRAHIR", "D"),        # la dernière ligne CHOIX fait foi
    (f"{ETIQUETTE} CHOIX : TRAHIR", "D"),
    ("Je ne sais pas", None), ("", None), (None, None), ("CHOIX : PEUT-ETRE", None),
])
def test_analyse_de_la_reponse(texte, attendu):
    assert analyser_reponse(texte) == attendu


def test_historique_et_horizon():
    assert formater_historique([], []) == "(aucune manche jouée)"
    assert formater_historique(["C", "D"], ["D", "D"]) == (
        "Manche 1: toi = COOPERER, adversaire = TRAHIR\nManche 2: toi = TRAHIR, adversaire = TRAHIR")
    assert "exactement 10 manches" in info_horizon(10, True)
    assert "exactement" not in info_horizon(10, False) and "pas annoncé" in info_horizon(10, False)


def joueur(textes, manches=10, annonce=False):
    return JoueurLLM(ModeleScripte(reponses=[reponse_finale(t) for t in textes]), manches, annonce)


def test_partie_complete_contre_tft_avec_un_joueur_qui_trahit_toujours():
    j = joueur(["CHOIX : TRAHIR"] * 10)
    m1, m2, h1, h2 = match_detail(j, strategie_par_nom("TFT"), 10, 0.0, random.Random(0))
    assert h1 == ["D"] * 10 and h2 == ["C"] + ["D"] * 9
    assert (m1, m2) == (pytest.approx((5 + 9) / 10), pytest.approx(9 / 10))     # scores moyens par manche
    assert j.appels == 10 and j.defauts == 0


def test_les_reponses_sans_choix_sont_comptees_a_part():
    j = joueur(["CHOIX : TRAHIR", "euh", "", "CHOIX : COOPERER"], manches=4)
    _, _, h1, _ = match_detail(j, strategie_par_nom("toujours_C"), 4, 0.0, random.Random(0))
    assert h1 == ["D", DEFAUT, DEFAUT, "C"]
    assert j.defauts == 2 and j.appels == 4
    assert [r[3] for r in j.reponses] == [False, True, True, False]     # drapeau « valeur par défaut » par manche


def test_le_prompt_contient_l_historique_et_le_numero_de_manche():
    capture = {}

    class Espion(ModeleScripte):
        def _generate(self, messages, stop=None, run_manager=None, **kw):
            capture["texte"] = "\n".join(m.content for m in messages)
            return super()._generate(messages, stop, run_manager, **kw)

    j = JoueurLLM(Espion(reponses=[reponse_finale("CHOIX : COOPERER")] * 2), 10, True)
    j(["C"], ["D"], random.Random(0))
    texte = capture["texte"]
    assert "Manche 1: toi = COOPERER, adversaire = TRAHIR" in texte and "Manche 2." in texte
    assert "exactement 10 manches" in texte and "CHOIX : COOPERER" in texte


def test_aucun_texte_de_modele_n_est_execute():
    """Une réponse qui ressemble à du code est lue comme du texte : coup par défaut, rien n'est exécuté."""
    j = joueur(["__import__('os').system('echo pirate')"], manches=1)
    assert j([], [], random.Random(0)) == DEFAUT and j.defauts == 1
