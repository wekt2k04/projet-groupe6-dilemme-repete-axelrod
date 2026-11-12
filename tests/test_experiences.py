# -*- coding: utf-8 -*-
"""Tests de src/experiences.py sur des données synthétiques (aucun modèle de langage n'est appelé)."""
import json

import numpy as np
import pytest

from experiences import (bootstrap_moyenne, charger_parties, classement_multi_graines, comparer_horizons, coop_par_manche,
                         intervalle_wilson, moyenne_ic, replicateur_multi_graines, resume_config, theorie_induction)


def partie(h_llm, defauts=0, score=2.0):
    return {"h_llm": list(h_llm), "h_adv": ["C"] * len(h_llm), "score_llm": score, "score_adv": 2.0,
            "appels": len(h_llm), "defauts": defauts}


META = {"meta": True, "modele": "test", "horizon_annonce": True, "adversaire": "TFT"}


def test_wilson_valeurs_connues():
    bas, haut = intervalle_wilson(5, 10)
    assert bas == pytest.approx(0.2366, abs=1e-3) and haut == pytest.approx(0.7634, abs=1e-3)
    assert intervalle_wilson(0, 0) == (0.0, 1.0)
    b, h = intervalle_wilson(10, 10)
    assert h == pytest.approx(1.0) and b < 1


def test_moyenne_ic():
    m, ic = moyenne_ic([1, 2, 3, 4])
    assert m == 2.5 and ic == pytest.approx(1.96 * np.std([1, 2, 3, 4], ddof=1) / 2)
    assert np.isnan(moyenne_ic([1.0])[1])


def test_coop_par_manche_et_resume():
    parties = [partie("CCD"), partie("CDD"), partie("CCC"), partie("DDD")]
    taux, bas, haut = coop_par_manche(parties)
    assert taux.tolist() == [0.75, 0.5, 0.25]
    assert (bas <= taux).all() and (taux <= haut).all()
    r = resume_config(META, parties)
    assert r["coop"] == pytest.approx(6 / 12) and r["coop_premiere_manche"] == 0.75 and r["coop_derniere_manche"] == 0.25
    assert r["trajectoires_distinctes"] == 4 and r["coop_ic95"][0] <= r["coop"] <= r["coop_ic95"][1]
    assert r["defauts"] == 0 and r["taux_hors_format"] == 0


def test_defauts_comptes_a_part():
    r = resume_config(META, [partie("CCDD", defauts=1), partie("CCCC", defauts=2)])
    assert r["defauts"] == 3 and r["appels"] == 8 and r["taux_hors_format"] == pytest.approx(3 / 8)


def test_comparaison_des_horizons():
    a = [partie("DDDD")] * 6
    b = [partie("CCCD")] * 6
    r = comparer_horizons(a, b)
    assert r["coop_annonce"] == 0 and r["coop_non_annonce"] == 0.75 and r["p"] < 0.01 and r["n_annonce"] == 6


def test_theorie_induction():
    assert theorie_induction(10).tolist() == [0.0] * 10


def test_charger_parties(tmp_path):
    chemin = tmp_path / "p.jsonl"
    chemin.write_text("\n".join(json.dumps(x) for x in [META, partie("CD"), partie("CC")]), encoding="utf-8")
    meta, parties = charger_parties(chemin)
    assert meta["modele"] == "test" and len(parties) == 2


def test_multi_graines_tournoi():
    r = classement_multi_graines(bruit=0.0, graines=range(3), manches=50, repetitions=2)
    assert set(r) == {"toujours_C", "toujours_D", "TFT", "rancunier", "Pavlov", "aleatoire"}
    assert sum(v["premier"] for v in r.values()) == pytest.approx(1)
    assert r["aleatoire"]["rang_moyen"] > r["TFT"]["rang_moyen"]
    moyenne, ic = r["TFT"]["score"]
    assert 2 < moyenne < 3.1 and (np.isnan(ic) or ic >= 0)


def test_multi_graines_replicateur():
    r = replicateur_multi_graines(bruit=0.0, graines=range(3), manches=50, repetitions=2, generations=50)
    assert sum(v["part_moyenne"] for v in r.values()) == pytest.approx(1)
    assert sum(v["domine"] for v in r.values()) == pytest.approx(1)
    assert r["toujours_D"]["part_moyenne"] < 0.2


def test_bootstrap_au_niveau_des_parties():
    m, bas, haut = bootstrap_moyenne([1, 1, 1, 1, 1, 1])
    assert m == bas == haut == 1                                         # échantillon constant : aucun intervalle
    m, bas, haut = bootstrap_moyenne([0, 1, 0, 1, 1, 0, 1, 0, 1, 1])
    assert m == 0.6 and 0.2 < bas < 0.6 < haut < 1.0
    assert bootstrap_moyenne([0, 1, 1, 0]) == bootstrap_moyenne([0, 1, 1, 0])      # reproductible (graine fixée)


def test_trajectoires_identiques_comptees_une_fois():
    parties = [partie("CCDD")] * 9 + [partie("DDDD")]
    r = resume_config(META, parties)
    assert r["trajectoires_distinctes"] == 2 and r["parties"] == 10
