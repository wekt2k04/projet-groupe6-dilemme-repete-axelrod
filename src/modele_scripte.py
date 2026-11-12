# -*- coding: utf-8 -*-
"""Faux modèle de chat « scripté » pour tester hors ligne les outils et la boucle de l'agent.

Il rejoue une liste de réponses préparées (appels d'outils, puis réponse finale). Il prouve que la mécanique de
l'agent fonctionne (outil appelé, résultat renvoyé, réponse produite) ; il ne dit RIEN sur la qualité d'un vrai LLM.
Toute sortie porte l'étiquette « scripté » dans son texte.
"""
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

ETIQUETTE = "[scripté]"


def appel_outil(nom, arguments, identifiant="appel_1"):
    """Réponse scriptée qui demande l'appel d'un outil."""
    return AIMessage(content=f"{ETIQUETTE} appel de l'outil {nom}",
                     tool_calls=[{"name": nom, "args": arguments, "id": identifiant, "type": "tool_call"}])


def reponse_finale(texte):
    """Réponse scriptée sans appel d'outil, qui termine la boucle."""
    return AIMessage(content=f"{ETIQUETTE} {texte}")


class ModeleScripte(BaseChatModel):
    """Rejoue `reponses` dans l'ordre ; lève une erreur si la boucle demande plus de réponses que prévu."""
    reponses: list
    indice: int = 0

    @property
    def _llm_type(self):
        return "modele-scripte"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if self.indice >= len(self.reponses):
            raise RuntimeError("le script du faux modèle est épuisé")
        message = self.reponses[self.indice]
        self.indice += 1
        return ChatResult(generations=[ChatGeneration(message=message)])
