# -*- coding: utf-8 -*-
"""Tests des contrôles automatiques des essais de l'agent (aucun modèle appelé)."""
import pytest

from controles_agent import controle

Q1 = ("tournoi_axelrod", {"strategies": ["TFT", "rancunier", "toujours_D"], "manches": 200, "bruit": 0, "seed": 0})


def test_q1_conforme_et_tolerant_sur_les_types():
    assert controle("Q1", [Q1])
    en_chaines = ("tournoi_axelrod", {"strategies": ["TFT", "rancunier", "toujours_D"], "manches": "200", "bruit": "0", "seed": "0"})
    assert controle("Q1", [en_chaines])            # observé avec llama3.1 : nombres écrits en chaînes, appel correct
    assert controle("Q1", [("tournoi_axelrod", {"strategies": ["rancunier", "TFT", "toujours_D"]})])   # valeurs par défaut


@pytest.mark.parametrize("appel", [
    ("tournoi_axelrod", {"strategies": ["TFT", "rancunier"], "manches": 200}),                  # stratégie manquante
    ("tournoi_axelrod", {"strategies": ["TFT", "rancunier", "toujours_D"], "bruit": 0.05}),    # mauvais bruit
    ("replicateur", {"strategies": ["TFT", "rancunier", "toujours_D"]}),                        # mauvais outil
    ("tournoi_axelrod", {"strategies": ["TFT", "rancunier", "toujours_D"], "manches": "beaucoup"}),
])
def test_q1_non_conforme(appel):
    assert not controle("Q1", [appel])


def test_autres_questions():
    assert controle("Q2", [("seuils_actualisation", {})]) and controle("Q2", [("seuils_actualisation", {"t": "5", "r": 3})])
    assert not controle("Q2", [("seuils_actualisation", {"t": 4})])
    assert controle("Q3", [("replicateur", {"strategies": [], "bruit": 0.05, "generations": 200})])
    assert not controle("Q3", [("replicateur", {"strategies": [], "bruit": 0.5})])
    assert controle("Q4", [("tournoi_axelrod", {"strategies": [], "bruit": 0}), ("tournoi_axelrod", {"strategies": [], "bruit": "0.01"})])
    assert not controle("Q4", [("tournoi_axelrod", {"strategies": [], "bruit": 0})])
    assert controle("Q5", []) and not controle("Q5", [Q1])
