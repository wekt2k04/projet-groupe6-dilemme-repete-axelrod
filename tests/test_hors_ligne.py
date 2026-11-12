# -*- coding: utf-8 -*-
"""Tests hors ligne des outils et de la boucle de l'agent, SANS modèle de langage réel.

La boucle de l'agent utilise un faux modèle étiqueté « scripté » : ces tests prouvent la mécanique
(outil appelé, résultat renvoyé, réponse produite), jamais la qualité d'un LLM.
"""
import json

import numpy as np
import pytest
from pydantic import ValidationError

from agent_tj_sma import (OUTILS, PLAFOND_GENERATIONS, PLAFOND_MANCHES, PLAFOND_REPETITIONS, SYSTEM_PROMPT,
                          construire_agent, interroger, replicateur_outil, seuils_actualisation, tournoi_axelrod)
from jeux import STRATEGIES_ETENDUES, tournoi
from modele_scripte import ETIQUETTE, ModeleScripte, appel_outil, reponse_finale


def appeler(outil, **args):
    return json.loads(outil.invoke(args))


# ---- description des outils -----------------------------------------------------------------
def test_les_outils_sont_decrits_pour_le_modele():
    assert {o.name for o in OUTILS} == {"tournoi_axelrod", "replicateur", "seuils_actualisation"}
    for o in OUTILS:
        assert len(o.description) > 80 and o.args           # docstring claire et arguments typés


# ---- tournoi_axelrod ---------------------------------------------------------------------------
def test_tournoi_valeurs_connues():
    r = appeler(tournoi_axelrod, strategies=["TFT", "toujours_D"], manches=50, bruit=0.0, seed=0)
    assert r["noms"] == ["TFT", "toujours_D"]
    M = np.array(r["matrice"])
    assert M[0][0] == 3 and M[1][1] == 1                      # auto-jeu
    assert M[0][1] == pytest.approx(49 / 50) and M[1][0] == pytest.approx(5 / 50 + 49 / 50)
    assert r["classement"][0]["strategie"] in ("TFT", "toujours_D")
    assert r["parametres"] == {"manches": 50, "bruit": 0.0, "seed": 0, "repetitions": 1}


def test_tournoi_identique_a_la_fonction_pure():
    r = appeler(tournoi_axelrod, strategies=[], manches=100, bruit=0.05, seed=3, repetitions=2)
    noms, M, _ = tournoi({n: STRATEGIES_ETENDUES[n] for n in r["noms"]}, 100, 0.05, 3, 2)
    assert noms == r["noms"] and np.allclose(M, r["matrice"])
    assert len(noms) == 6                                      # liste vide = les six stratégies du guide


def test_tournoi_reproductible_a_graine_fixee():
    a = tournoi_axelrod.invoke({"strategies": ["TFT", "aleatoire"], "manches": 60, "bruit": 0.1, "seed": 7})
    b = tournoi_axelrod.invoke({"strategies": ["TFT", "aleatoire"], "manches": 60, "bruit": 0.1, "seed": 7})
    assert a == b


def test_tournoi_plafonne_les_parametres_couteux():
    r = appeler(tournoi_axelrod, strategies=["TFT", "Pavlov"], manches=10 ** 9, repetitions=10 ** 6)
    assert r["parametres"]["manches"] == PLAFOND_MANCHES
    assert r["parametres"]["repetitions"] == PLAFOND_REPETITIONS
    assert len(r["avertissements"]) == 2


def test_tournoi_refuse_les_entrees_invalides():
    """Valeurs invalides : l'outil renvoie un JSON {"erreur": ...} que l'agent peut lire."""
    for args in ({"strategies": ["inconnue"]}, {"strategies": ["TFT"], "bruit": 1.5},
                 {"strategies": ["TFT", "TFT"]}):
        assert "erreur" in appeler(tournoi_axelrod, **args)


def test_le_schema_de_l_outil_refuse_les_mauvais_types():
    """Premier niveau de protection : les types annotés sont validés avant même l'exécution de l'outil."""
    with pytest.raises(ValidationError):
        tournoi_axelrod.invoke({"strategies": "TFT"})
    with pytest.raises(ValidationError):
        tournoi_axelrod.invoke({"strategies": ["TFT"], "manches": "beaucoup"})


def test_aucun_code_n_est_execute():
    """Un « nom de stratégie » qui contient du code est refusé tel quel : jamais eval ni exec."""
    r = appeler(tournoi_axelrod, strategies=["__import__('os').system('echo pirate')"])
    assert "erreur" in r and "inconnue" in r["erreur"]


# ---- replicateur -----------------------------------------------------------------------------
def test_replicateur_parts_positives_somme_1():
    r = appeler(replicateur_outil, strategies=[], generations=100, manches=100, bruit=0.01, seed=0, repetitions=3)
    parts = np.array(list(r["parts_finales"].values()))
    assert (parts >= 0).all() and parts.sum() == pytest.approx(1) and r["somme_parts_finales"] == pytest.approx(1)
    assert "0" in r["trajectoire"] and "100" in r["trajectoire"]
    assert list(r["trajectoire"]["0"].values()) == pytest.approx([1 / 6] * 6)      # parts égales au départ


def test_replicateur_plafonne_les_generations():
    r = appeler(replicateur_outil, strategies=["TFT", "toujours_D"], generations=10 ** 7, manches=20, repetitions=1)
    assert r["parametres"]["generations"] == PLAFOND_GENERATIONS and r["avertissements"]


def test_replicateur_refuse_une_strategie_inconnue():
    assert "erreur" in appeler(replicateur_outil, strategies=["magique"])


# ---- seuils ----------------------------------------------------------------------------------
def test_seuils_actualisation():
    r = appeler(seuils_actualisation)
    assert r["dilemme"] and r["seuil_rancunier"] == 0.5 and r["seuil_tft"] == pytest.approx(2 / 3)
    assert appeler(seuils_actualisation, t=5, r=2, p=1, s=0)["dilemme"] is False


# ---- boucle de l'agent avec le faux modèle (scripté) -----------------------------------------
def agent_scripte(*reponses):
    return construire_agent(ModeleScripte(reponses=list(reponses)))


def test_boucle_de_l_agent_appelle_l_outil_puis_repond():
    agent = agent_scripte(
        appel_outil("tournoi_axelrod", {"strategies": ["TFT", "toujours_D"], "manches": 40, "bruit": 0.0, "seed": 0}),
        reponse_finale("TFT et toujours_D ont été comparés sur 40 manches."))
    messages = interroger(agent, "Compare TFT et toujours_D.", verbose=False)
    outils = [m for m in messages if m.type == "tool"]
    assert len(outils) == 1 and outils[0].name == "tournoi_axelrod"
    assert "classement" in json.loads(outils[0].content)
    assert messages[-1].type == "ai" and messages[-1].content.startswith(ETIQUETTE)    # sortie étiquetée « scripté »


def test_boucle_gere_une_erreur_d_outil():
    agent = agent_scripte(appel_outil("tournoi_axelrod", {"strategies": ["inconnue"]}),
                          reponse_finale("L'outil a signalé une stratégie inconnue."))
    messages = interroger(agent, "Lance un tournoi avec une stratégie inconnue.", verbose=False)
    contenu = [m for m in messages if m.type == "tool"][0].content
    assert "erreur" in json.loads(contenu) and messages[-1].content.startswith(ETIQUETTE)


def test_boucle_enchaine_deux_outils():
    agent = agent_scripte(appel_outil("seuils_actualisation", {}, "a1"),
                          appel_outil("replicateur", {"strategies": ["TFT", "toujours_D"], "generations": 20,
                                                      "manches": 30, "repetitions": 1}, "a2"),
                          reponse_finale("Seuils puis population calculés."))
    messages = interroger(agent, "Donne les seuils puis la dynamique.", verbose=False)
    assert [m.name for m in messages if m.type == "tool"] == ["seuils_actualisation", "replicateur"]


def test_le_prompt_systeme_impose_l_usage_des_outils():
    assert "appelle l'outil" in SYSTEM_PROMPT and "jamais un chiffre de mémoire" in SYSTEM_PROMPT
