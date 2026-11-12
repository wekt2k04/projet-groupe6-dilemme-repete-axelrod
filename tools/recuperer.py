# -*- coding: utf-8 -*-
"""Prépare ta branche de la semaine : tes fichiers sont récupérés depuis prep/sN, tu n'as plus qu'à les exécuter et à les commiter.

Usage depuis la racine du dépôt cloné :   python tools/recuperer.py <Prénom> <semaine>     (exemple : python tools/recuperer.py Assia 2)
Le script crée la branche <prenom>-s<N> à partir de origin/main, y place TES fichiers et affiche les commandes suivantes. Il ne fait
JAMAIS de commit : le commit est le tien, sous ton nom (git config user.name / user.email), comme l'exige le guide.
"""
import subprocess
import sys

TACHES = {  # (prénom, semaine) -> (fichiers à récupérer, message de commit)
    ("Assia", 2): ("src/jeux.py", "[Assia] Fonctions pures du dilemme répété : validations, TFT généreux, seuils (S2-01)"),
    ("Jihane", 2): ("tests/test_jeux.py", "[Jihane] Tests du tournoi, du réplicateur et du seuil par arrêt aléatoire (S2-03)"),
    ("Wilfried", 2): ("notebooks/01_theorie_prototype.ipynb tools/build_gantt.py docs/gantt_realise.png docs/gantt_source.xlsx docs/avancement/S2.pdf docs/avancement/sources/S2.json", "[Wilfried] Notebook 01, Gantt réalisé et point d'avancement S2 (S2-02)"),
    ("Marwane", 2): ("", "[Marwane] Installation d'Ollama et vérification des modèles (S1-02)"),
    ("Marwane", 3): ("src/agent_tj_sma.py src/modele_scripte.py", "[Marwane] Outils tournoi_axelrod, replicateur et seuils_actualisation branchés à l'agent (S3-01)"),
    ("Jihane", 3): ("tests/test_hors_ligne.py", "[Jihane] Tests hors ligne des outils et de la boucle de l'agent (S3-02)"),
    ("Assia", 3): ("notebooks/02_outils_agent.ipynb", "[Assia] Notebook 02 : outils appelés avec invoke et boucle scriptée (S3-03)"),
    ("Wilfried", 3): ("docs/avancement/S3.pdf docs/avancement/sources/S3.json docs/gantt_realise.png docs/gantt_source.xlsx tools/build_gantt.py", "[Wilfried] Point d'avancement S3 et Gantt réalisé (S3-04)"),
    ("Marwane", 4): ("src/joueur_llm.py src/controles_agent.py scripts/essai_agent_ollama.py", "[Marwane] Agent testé avec Ollama : joueur LLM et essai sur cinq questions (S4-01)"),
    ("Jihane", 4): ("tests/test_joueur_llm.py tests/test_controles_agent.py", "[Jihane] Tests du joueur LLM : format CHOIX et valeur par défaut comptée (S4-02)"),
    ("Assia", 4): ("scripts/run_llm_games.py", "[Assia] Pilote d'une partie LLM contre TFT et durée par coup (S4-03)"),
    ("Wilfried", 4): ("docs/avancement/S4.pdf docs/avancement/sources/S4.json docs/gantt_realise.png docs/gantt_source.xlsx tools/build_gantt.py", "[Wilfried] Point d'avancement S4, rotation et Gantt réalisé (S4-04)"),
    ("Marwane", 5): ("scripts/run_llm_games.py resultats", "[Marwane] Parties LLM contre TFT : <modèle>, horizon annoncé (S5-01)"),
    ("Wilfried", 5): ("src/experiences.py notebooks/03_experiences.ipynb docs/figures", "[Wilfried] Protocole multi-graines et notebook 03 (S5-02)"),
    ("Assia", 5): ("tests/test_experiences.py", "[Assia] Tests du module d'expériences (S5-03)"),
    ("Jihane", 5): ("docs/avancement/S5.pdf docs/avancement/sources/S5.json docs/gantt_realise.png docs/gantt_source.xlsx tools/build_gantt.py", "[Jihane] Point d'avancement S5 et Gantt réalisé (S5-04)"),
    ("Jihane", 6): ("docs/rapport/01_introduction.md docs/rapport/07_organisation_planification.md docs/rapport/08_conclusion.md", "[Jihane] Introduction, organisation et conclusion du rapport (S6-01)"),
    ("Wilfried", 6): ("docs/rapport/02_theorie.md docs/rapport/03_donnees_python.md", "[Wilfried] Sections théorie et données Python du rapport (S6-02)"),
    ("Assia", 6): ("docs/rapport/04_agents.md", "[Assia] Section agents et outils du rapport (S6-03)"),
    ("Marwane", 6): ("docs/rapport/05_experiences.md docs/rapport/06_tests_qualite.md", "[Marwane] Sections expériences et tests du rapport (S6-04)"),
    ("Jihane", 7): ("docs/gantt_realise.png docs/gantt_source.xlsx docs/avancement/S7.pdf docs/avancement/sources/S7.json", "[Jihane] Gantt réalisé final et bilan du projet (S7-01)"),
    ("Wilfried", 7): ("tools/archiver.py", "[Wilfried] Outil d'archivage de la remise (S7-02)"),
    ("Assia", 7): ("", "[Assia] Vérification de l'installation à partir d'un clone propre (S7-03)"),
    ("Marwane", 7): ("", "[Marwane] Contrôle des chiffres du rapport final (S7-04)"),
}


def sh(*cmd):
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) != 3 or (sys.argv[1].capitalize(), int(sys.argv[2])) not in TACHES:
        sys.exit("Usage : python tools/recuperer.py <Prénom> <semaine>   (Prénoms : Assia, Jihane, Marwane, Wilfried ; semaines 2 à 7)")
    prenom, semaine = sys.argv[1].capitalize(), int(sys.argv[2])
    fichiers, message = TACHES[(prenom, semaine)]
    branche = f"{prenom.lower()}-s{semaine}"
    sh("git", "fetch", "origin")
    sh("git", "checkout", "-b", branche, "origin/main")
    if fichiers:
        sh("git", "checkout", f"origin/prep/s{semaine}", "--", *fichiers.split())
    print(f"\nBranche {branche} prête. Fichiers récupérés : {fichiers or 'aucun (tâche sans fichier : voir ton issue)'}")
    print("1. Exécute et lis la partie « À comprendre » de docs/semaines/S%d.md (sur la branche prep/s%d)." % (semaine, semaine))
    print("2. Vérifie ton identité : git config user.name && git config user.email")
    print(f"3. git add -A && git commit -m \"{message}\"")
    print(f"4. git push -u origin {branche}   puis ouvre la PR et fais-la relire par un autre membre.")


if __name__ == "__main__":
    main()
