# -*- coding: utf-8 -*-
"""Génère docs/avancement/SN.pdf (point d'avancement hebdomadaire) au format du mini-livrable du groupe 1 de Finance.

Usage depuis la racine du dépôt :   python tools/build_avancement.py 1
Entrée : docs/avancement/sources/SN.json. Sortie : docs/avancement/SN.pdf et aperçus PNG (docs/avancement/apercu/, non versionnés).
Structure : page de garde (logo pleine largeur, filet bleu), corps de 2 pages au plus (sections 1 à 5), annexe Gantt en paysage.
Le script refuse un corps de plus de 2 pages. Prérequis : pip install playwright ; python -m playwright install chromium.
Le logo n'apparaît que sur la page de garde.
"""
import base64
import html
import json
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
BLEU = "#1f3864"


def b64(chemin):
    return base64.b64encode(pathlib.Path(chemin).read_bytes()).decode()


def e(texte):
    """Échappe le HTML ; la notation x_{i} devient un indice (les autres tirets bas restent intacts)."""
    return re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", html.escape(texte, quote=False))


def paragraphes(texte):
    return "".join(f"<p>{e(p.strip())}</p>" for p in texte.split("\n\n") if p.strip())


def tableau(lignes):
    entete = "".join(f"<th>{e(c)}</th>" for c in lignes[0])
    corps = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in lignes[1:])
    return f"<table><tr>{entete}</tr>{corps}</table>"


CSS = f"""
@page {{ size: A4; margin: 2.3cm 2.4cm 2.2cm 2.4cm; }}
@page paysage {{ size: A4 landscape; margin: 1.4cm 1.6cm; }}
body {{ font-family: 'Liberation Serif', 'Times New Roman', serif; font-size: 10.6pt; line-height: 1.42; text-align: justify; color: #1a1a1a; margin: 0; }}
h2 {{ font-size: 14.5pt; color: {BLEU}; margin: 15pt 0 6pt; }}
h3 {{ font-size: 11pt; margin: 9pt 0 3pt; }}
p {{ margin: 0 0 5.5pt; }}
ol {{ margin: 2pt 0 4pt 18pt; padding: 0; }} li {{ margin-bottom: 2pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 5pt 0 8pt; font-size: 10pt; }}
th, td {{ border: 0.7pt solid #8a8a8a; padding: 3pt 7pt; text-align: left; }} th {{ background: #e8edf5; }}
.garde {{ page-break-after: always; text-align: center; height: 24.6cm; position: relative; }}
.garde img {{ width: 100%; display: block; }}
.filet {{ border-top: 1.6pt solid {BLEU}; margin: 8pt 0 34pt; }}
.garde .inst {{ font-size: 12pt; line-height: 1.75; }}
.garde .mod {{ font-size: 12pt; line-height: 1.75; margin-top: 52pt; }}
.garde .titre {{ font-size: 23pt; font-weight: bold; color: {BLEU}; margin: 52pt 0 18pt; line-height: 1.25; }}
.garde .sous {{ font-size: 15pt; margin: 6pt 0; }} .garde .date {{ font-size: 12pt; color: #333; margin-top: 12pt; }}
.garde .bas {{ position: absolute; bottom: 0; left: 0; right: 0; display: flex; justify-content: space-between; text-align: left; font-size: 11.5pt; line-height: 1.65; }}
.corps {{ page-break-after: always; }}
.annexe {{ page: paysage; text-align: center; }} .annexe h2 {{ text-align: left; margin-top: 0; }}
.annexe img {{ max-width: 100%; max-height: 14.6cm; }} .annexe .leg {{ font-size: 11pt; margin-top: 6pt; color: #333; }}
"""


def construire_html(spec):
    n = spec["semaine"]
    logo = b64(RACINE / "docs/assets/logo_ensa.png")
    membres = "<br>".join(e(m) for m in spec["membres"])
    garde = f"""<div class="garde"><img src="data:image/png;base64,{logo}"><div class="filet"></div>
<div class="inst">Université Cadi Ayyad<br>École Nationale des Sciences Appliquées de Safi<br>Cycle ingénieur, année universitaire 2026-2027</div>
<div class="mod">Module : Théorie des Jeux et Systèmes Multi-Agents<br>Projet intégrateur n° 6</div>
<div class="titre">Dilemme du prisonnier répété :<br>tournoi d'Axelrod et agents LLM</div>
<div class="sous">{e(spec['titre_livrable'])}</div><div class="date">Séance du {e(spec['date'])}</div>
<div class="bas"><div><b>Réalisé par (groupe 6) :</b><br>{membres}</div><div><b>Encadré par :</b><br>Pr Abdelilah JRAIFI</div></div></div>"""
    realise = ""
    for s in spec["realise"]:
        realise += f"<h3>{e(s['titre'])}</h3>{paragraphes(s['texte'])}"
        if s.get("table"):
            realise += tableau(s["table"])
    questions = "".join(f"<li>{e(q)}</li>" for q in spec.get("questions", []))
    corps = f"""<div class="corps"><h2>1. Objet du projet</h2>{paragraphes(spec['objet'])}
<h2>2. Travail réalisé</h2>{realise}
<h2>3. Choix retenus</h2>{paragraphes(spec['choix'])}
<h2>4. Écarts, difficultés et questions à l'encadrant</h2>{paragraphes(spec['ecarts'])}{'<ol>' + questions + '</ol>' if questions else ''}
<h2>5. Objectifs de la semaine {n + 1}</h2>{paragraphes(spec['plan'])}</div>"""
    a = spec["annexe"]
    annexe = f"""<div class="annexe"><h2>{e(a['titre'])}</h2><img src="data:image/png;base64,{b64(RACINE / a['image'])}">
<div class="leg">{e(a['legende'])}</div></div>"""
    return f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{garde}{corps}{annexe}</body></html>"


def nb_pages(pdf):
    return len(re.findall(rb"/Type\s*/Page[^s]", pathlib.Path(pdf).read_bytes()))


def main(n):
    spec = json.loads((RACINE / f"docs/avancement/sources/S{n}.json").read_text(encoding="utf-8"))
    sortie = RACINE / f"docs/avancement/S{n}.pdf"
    page = RACINE / f"docs/avancement/sources/S{n}.html"
    page.write_text(construire_html(spec), encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page()
        pg.goto(page.resolve().as_uri())
        pg.pdf(path=str(sortie), format="A4", prefer_css_page_size=True, print_background=True)
        nav.close()
    page.unlink()
    pages = nb_pages(sortie)
    print(f"{sortie.name} : {pages} pages (garde + corps + annexe ; corps = {pages - 2})")
    apercu = RACINE / "docs/avancement/apercu"
    apercu.mkdir(exist_ok=True)
    try:
        subprocess.run(["pdftoppm", "-r", "70", "-png", str(sortie), str(apercu / f"S{n}")], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        print("pdftoppm indisponible : aperçu non généré")
    if pages - 2 > 2:
        sys.exit("ERREUR : le corps dépasse 2 pages ; raccourcir le texte du JSON.")


if __name__ == "__main__":
    main(int(sys.argv[1]))
