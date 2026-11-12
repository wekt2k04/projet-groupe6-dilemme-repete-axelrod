# -*- coding: utf-8 -*-
"""Crée l'archive de remise (code + rapport) : projet6_groupe6_remise.zip à la racine du dépôt.

Usage depuis la racine du dépôt :   python tools/archiver.py
Seuls les fichiers suivis par Git sont archivés (pas de .venv, de caches ni de fichiers temporaires) ;
le contenu est celui du dernier commit de la branche courante. Le script liste l'archive et vérifie que les
fichiers exigés par le guide (README, src, tests, notebooks, requirements, Gantt réalisé et sa source, rapport) y figurent.
"""
import subprocess
import sys
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "projet6_groupe6_remise.zip"
EXIGES = ["README.md", "requirements.txt", "src/jeux.py", "src/experiences.py", "src/agent_tj_sma.py",
          "tests/test_jeux.py", "tests/test_hors_ligne.py", "docs/gantt_realise.png", "docs/gantt_source.xlsx",
          "notebooks/01_theorie_prototype.ipynb", "notebooks/02_outils_agent.ipynb", "notebooks/03_experiences.ipynb"]


def main():
    suivis = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True, check=True,
                            encoding="utf-8").stdout.split("\n")
    fichiers = [f for f in suivis if f and (RACINE / f).is_file()]
    manquants = [f for f in EXIGES if f not in fichiers]
    if manquants:
        sys.exit(f"ERREUR : fichiers exigés absents du dépôt : {manquants}")
    with zipfile.ZipFile(SORTIE, "w", zipfile.ZIP_DEFLATED) as z:
        for f in fichiers:
            z.write(RACINE / f, f"projet6_groupe6/{f}")
    print(f"{SORTIE.name} : {len(fichiers)} fichiers, {SORTIE.stat().st_size / 1e6:.2f} Mo")


if __name__ == "__main__":
    main()
