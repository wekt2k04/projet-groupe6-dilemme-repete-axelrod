# -*- coding: utf-8 -*-
"""Joueur LLM du dilemme répété : chaîne prompt | modèle | parseur, format « CHOIX : COOPERER » ou « CHOIX : TRAHIR ».

Un joueur LLM suit la signature d'une stratégie, (mon_historique, historique_adverse, rng) -> 'C' ou 'D',
donc `jeux.match_detail` s'utilise sans modification. Une réponse sans ligne « CHOIX : » reçoit le coup par défaut
(`DEFAUT`, coopérer : on évite ainsi de biaiser vers l'issue théorique, la trahison) et est COMPTÉE À PART.
Le texte d'un modèle n'est jamais exécuté : il est seulement lu par une expression régulière.
"""
import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

DEFAUT = "C"
MOTIF = re.compile(r"CHOIX\s*:\s*(COOP[ÉE]RER|TRAHIR)", re.IGNORECASE)

REGLES = (
    "Tu joues au dilemme du prisonnier répété contre un adversaire. À chaque manche, vous choisissez en même temps "
    "COOPERER ou TRAHIR. Gains de la manche, pour toi puis pour l'adversaire : si vous coopérez tous les deux, 3 et 3 ; "
    "si tu coopères et que l'adversaire trahit, 0 et 5 ; si tu trahis et que l'adversaire coopère, 5 et 0 ; "
    "si vous trahissez tous les deux, 1 et 1. Ton but est de maximiser ton total de points sur toute la partie. "
    "{info_horizon}"
)
TOUR = (
    "Historique des manches jouées :\n{historique}\n\nManche {numero}. "
    "Réponds uniquement par une ligne au format exact : CHOIX : COOPERER   ou   CHOIX : TRAHIR"
)
PROMPT = ChatPromptTemplate.from_messages([("system", REGLES), ("human", TOUR)])
NOM_COUP = {"C": "COOPERER", "D": "TRAHIR"}


def analyser_reponse(texte):
    """Renvoie 'C' ou 'D' d'après la DERNIÈRE ligne « CHOIX : ... » du texte, ou None si elle est absente."""
    trouves = MOTIF.findall(texte or "")
    if not trouves:
        return None
    return "C" if trouves[-1].upper().startswith("COOP") else "D"


def formater_historique(mes_coups, coups_adverses):
    """Texte de l'historique : un coup exécuté par joueur et par manche (vide au premier tour)."""
    if not mes_coups:
        return "(aucune manche jouée)"
    return "\n".join(f"Manche {k}: toi = {NOM_COUP[a]}, adversaire = {NOM_COUP[b]}"
                     for k, (a, b) in enumerate(zip(mes_coups, coups_adverses), 1))


def info_horizon(manches, annonce):
    if annonce:
        return f"La partie compte exactement {manches} manches."
    return "Le nombre total de manches n'est pas annoncé."


class JoueurLLM:
    """Stratégie pilotée par un modèle de chat. `modele` : ChatOllama, ou faux modèle étiqueté « scripté » pour les tests."""

    def __init__(self, modele, manches, horizon_annonce, nom="llm"):
        self.chaine = PROMPT | modele | StrOutputParser()
        self.manches, self.horizon_annonce, self.nom = manches, horizon_annonce, nom
        self.appels = 0
        self.defauts = 0
        self.reponses = []                      # (numéro de manche, texte brut, coup joué, valeur par défaut ?)

    def __call__(self, mes_coups, coups_adverses, rng):
        numero = len(mes_coups) + 1
        texte = self.chaine.invoke({
            "info_horizon": info_horizon(self.manches, self.horizon_annonce),
            "historique": formater_historique(mes_coups, coups_adverses),
            "numero": numero,
        })
        self.appels += 1
        coup = analyser_reponse(texte)
        par_defaut = coup is None
        if par_defaut:
            self.defauts += 1
            coup = DEFAUT
        self.reponses.append((numero, texte, coup, par_defaut))
        return coup
