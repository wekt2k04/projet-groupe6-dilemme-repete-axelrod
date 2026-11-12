# -*- coding: utf-8 -*-
"""Contrôles automatiques des essais de l'agent : l'outil appelé et ses arguments sont-ils ceux que la question exige ?

Les contrôles sont volontairement tolérants sur le TYPE des nombres : un modèle peut écrire "200" au lieu de 200 ; le schéma de
l'outil convertit la chaîne et le calcul est correct, donc l'appel est jugé conforme. Ils sont appliqués aux arguments
ENREGISTRÉS, ce qui permet de recalculer le contrôle de tous les essais de la même façon, quelle que soit la version du script
qui a joué l'essai.
"""


def _nombre(valeur, defaut):
    """Convertit en float ; renvoie `defaut` si l'argument est absent et None s'il n'est pas convertible."""
    if valeur is None:
        return float(defaut)
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def _noms(args):
    s = args.get("strategies", [])
    return set(s) if isinstance(s, (list, tuple)) else {str(s)}


def _egal(a, b, defaut, tol=1e-9):
    x = _nombre(a, defaut)
    return x is not None and abs(x - b) < tol


def ok_q1(appels):
    return any(n == "tournoi_axelrod" and _noms(a) == {"TFT", "rancunier", "toujours_D"} and _egal(a.get("bruit"), 0, 0)
               and _egal(a.get("manches"), 200, 200) and _egal(a.get("seed"), 0, 0) for n, a in appels)


def ok_q2(appels):
    return any(n == "seuils_actualisation" and _egal(a.get("t"), 5, 5) and _egal(a.get("r"), 3, 3)
               and _egal(a.get("p"), 1, 1) and _egal(a.get("s"), 0, 0) for n, a in appels)


def ok_q3(appels):
    return any(n == "replicateur" and _egal(a.get("bruit"), 0.05, 0) and _egal(a.get("generations"), 200, 200)
               and len(_noms(a)) in (0, 6) for n, a in appels)


def ok_q4(appels):
    bruits = {round(_nombre(a.get("bruit"), 0) or 0.0, 4) for n, a in appels if n == "tournoi_axelrod"}
    return {0.0, 0.01} <= bruits


def ok_q5(appels):
    return len(appels) == 0         # question hors sujet : aucun outil attendu


CONTROLES = {"Q1": ok_q1, "Q2": ok_q2, "Q3": ok_q3, "Q4": ok_q4, "Q5": ok_q5}


def controle(question_id, appels):
    """`appels` : liste de (nom d'outil, arguments). Renvoie True si l'essai respecte la consigne de la question."""
    return bool(CONTROLES[question_id](appels))
