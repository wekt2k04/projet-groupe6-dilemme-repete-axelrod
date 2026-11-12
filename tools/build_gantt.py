# -*- coding: utf-8 -*-
"""Gantt prévisionnel du groupe 6 : image docs/gantt_previsionnel.png et source éditable docs/gantt_source.xlsx.

Usage depuis la racine du dépôt :  python tools/build_gantt.py
Le classeur contient une grille « Prévu » et une grille « Réalisé » pilotées par des formules : renseigner Début réel,
Fin réelle et Statut (colonnes H, I, J) pour mettre à jour le Gantt réalisé, puis lancer tools/build_gantt_realise.py.
AVANCEMENT pré-remplit ces colonnes (état à la fin de la dernière semaine écrite) ; le modifier à chaque séance.
"""
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.formatting.rule import FormulaRule  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

OUT = str(pathlib.Path(__file__).resolve().parent.parent / "docs") + "/"
DATES = ["11/11", "18/11", "25/11", "02/12", "09/12", "16/12", "23/12"]   # indicatif : une séance par semaine
PH = {"Cadrage": "#0072B2", "Python": "#009E73", "Agents": "#E69F00", "Expériences": "#CC79A7", "Rapport": "#7F7F7F"}
# (tâche, phase, rôle, début S, fin S)
T = [
    ("Fiche de lecture théorique", "Cadrage", "Chef de projet", 1, 1),
    ("Dépôt GitHub, Ollama, conventions", "Cadrage", "Testeur", 1, 1),
    ("Gantt prévisionnel", "Cadrage", "Chef de projet", 1, 1),
    ("Formules, hypothèses, seuils δ (1/2 et 2/3)", "Python", "Chef de projet", 1, 2),
    ("jeux.py : match, tournoi, réplicateur", "Python", "Quant / Python", 1, 2),
    ("Notebook 01 : retrouver les résultats du cours", "Python", "Quant / Python", 2, 2),
    ("Tests pytest et seuil δ par Monte-Carlo", "Python", "Testeur", 2, 3),
    ("Outils @tool tournoi_axelrod et replicateur", "Agents", "Développeur agent", 3, 3),
    ("Tests hors ligne (faux modèle scripté)", "Agents", "Testeur", 3, 3),
    ("Agent LangChain avec Ollama (verbose=True)", "Agents", "Développeur agent", 4, 4),
    ("Chaîne prompt | modèle | parseur, format CHOIX", "Agents", "Développeur agent", 4, 4),
    ("Premiers classements selon ε, TFT généreux", "Expériences", "Quant / Python", 4, 4),
    ("Protocole complet, graines, tableaux", "Expériences", "Testeur", 5, 5),
    ("Parties LLM : 10 x 10 manches, 2 modèles", "Expériences", "Testeur", 5, 6),
    ("Réplicateur et écarts à la théorie", "Expériences", "Quant / Python", 5, 5),
    ("Gantt mis à jour (mi-parcours)", "Rapport", "Chef de projet", 4, 4),
    ("Rédaction du rapport (80 % en S6)", "Rapport", "Chef de projet", 5, 6),
    ("Code finalisé, archive zippée", "Rapport", "Tous", 6, 7),
    ("Gantt réalisé et bilan", "Rapport", "Chef de projet", 7, 7),
]
# Responsables proposés (à valider en séance) ; rotation obligatoire des rôles à la fin de la S4
R1 = {"Chef de projet": "Wilfried", "Quant / Python": "Assia", "Développeur agent": "Marwane",
      "Testeur": "Jihane", "Tous": "Tous"}
R2 = {"Chef de projet": "Jihane", "Quant / Python": "Wilfried", "Développeur agent": "Assia",
      "Testeur": "Marwane", "Tous": "Tous"}
PRESENTATEURS = ["Wilfried", "Assia", "Marwane", "Jihane", "Wilfried", "Assia", "Marwane"]   # un membre différent chaque semaine
# état réel, renseigné à chaque séance : tâche -> (début réel, fin réelle, statut)
AVANCEMENT = {
    "Fiche de lecture théorique": (1, 1, "Terminé"),
    "Dépôt GitHub, Ollama, conventions": (1, 1, "Terminé"),
    "Gantt prévisionnel": (1, 1, "Terminé"),
    "Formules, hypothèses, seuils δ (1/2 et 2/3)": (1, 2, "Terminé"),
    "jeux.py : match, tournoi, réplicateur": (1, 2, "Terminé"),
    "Notebook 01 : retrouver les résultats du cours": (2, 2, "Terminé"),
    "Tests pytest et seuil δ par Monte-Carlo": (2, 3, "Terminé"),
    "Outils @tool tournoi_axelrod et replicateur": (3, 3, "Terminé"),
    "Tests hors ligne (faux modèle scripté)": (3, 3, "Terminé"),
    "Agent LangChain avec Ollama (verbose=True)": (4, 4, "Terminé"),
    "Chaîne prompt | modèle | parseur, format CHOIX": (4, 4, "Terminé"),
    "Premiers classements selon ε, TFT généreux": (4, 4, "Terminé"),
    "Gantt mis à jour (mi-parcours)": (4, 4, "Terminé"),
    "Protocole complet, graines, tableaux": (5, 5, "Terminé"),
    "Parties LLM : 10 x 10 manches, 2 modèles": (5, 5, "Terminé"),
    "Réplicateur et écarts à la théorie": (5, 5, "Terminé"),
    "Prompts, parseur CHOIX, scripts d'expérience": (5, 5, "Terminé"),
    "Rédaction du rapport (80 % en S6)": (5, 7, "Terminé"),
    "Code finalisé, archive zippée": (6, 7, "Terminé"),
    "Gantt réalisé et bilan": (7, 7, "Terminé"),
}


def who(role, start):
    return (R1 if start <= 4 else R2)[role]


# un mini-compte rendu chaque semaine, plus ces jalons (pas de soutenance : le dernier point fait le bilan)
MILESTONES = [(1, "Fiche de lecture"), (4, "Rotation des rôles"), (6, "Rapport à 80 %"), (7, "Remise et bilan")]
EXTRA = dict(MILESTONES)


def png():
    fig, ax = plt.subplots(figsize=(14, 7.8), dpi=150)
    n = len(T)
    for i, (name, ph, role, a, b) in enumerate(T):
        y = n - 1 - i
        ax.barh(y, b - a + 1, left=a - 1, height=0.62, color=PH[ph], edgecolor="white")
        ax.text(b + 0.06, y, f"{who(role, a)} ({role})", va="center", fontsize=7.5, color="#555555")
    ax.set_yticks(range(n))
    ax.set_yticklabels([t[0] for t in T][::-1], fontsize=8.5)
    ax.set_xlim(0, 8.3)
    ax.set_xticks([w + 0.5 for w in range(7)])
    ax.set_xticklabels([f"S{w + 1}\n{DATES[w]}" for w in range(7)], fontsize=8.5)
    for w in range(8):
        ax.axvline(w, color="#DDDDDD", lw=0.8, zorder=0)
    ax.set_ylim(-2.7, n - 0.3)
    for wk in range(1, 8):
        ax.plot(wk - 0.5, -1.2, marker="D", color="#222222", markersize=7, clip_on=False)
        ax.text(wk - 0.5, -1.6, "Mini-CR" + ("\n" + EXTRA[wk] if wk in EXTRA else ""), ha="center", va="top",
                fontsize=7.5, color="#222222")
    ax.axvline(4, color="#D55E00", ls="--", lw=1.3, zorder=1)
    ax.text(4.05, n - 0.6, "rotation des rôles", color="#D55E00", fontsize=7.5)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title("Gantt prévisionnel — Groupe 6 · Dilemme du prisonnier répété (version S1)", fontsize=12,
                 fontweight="bold", loc="left", pad=28)
    ax.text(0, 1.018, "Dates indicatives : une séance par semaine à partir du 11/11/2026, à confirmer. "
            "Responsables proposés (rotation à la fin de la S4), à valider en séance. ◆ = jalon.",
            transform=ax.transAxes, fontsize=8, color="#555555")
    ax.legend(handles=[Patch(color=c, label=k) for k, c in PH.items()], loc="upper right", ncol=3, fontsize=8,
              frameon=False, bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout()
    fig.savefig(OUT + "gantt_previsionnel.png")
    print("png ok")


def xlsx():
    wb = Workbook()
    ws = wb.active
    ws.title = "Gantt"
    ws["A1"] = "Gantt — Groupe 6 · Dilemme du prisonnier répété"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = ("Renseigner Début/Fin réels (colonnes H, I) et le statut ; les barres se mettent à jour. "
                "Dates indicatives : S1 = 11/11/2026.")
    heads = ["Tâche", "Phase", "Rôle", "Responsable", "Début prévu (S)", "Fin prévue (S)", "Durée (sem.)",
             "Début réel (S)", "Fin réelle (S)", "Statut"]
    hr = 4
    PL, RL = 12, 20     # première colonne de la grille prévue / réelle (L, T)
    thin = Side(style="thin", color="BBBBBB")
    hdr_fill = PatternFill("solid", fgColor="0B3C5D")
    for c, h in enumerate(heads, 1):
        cell = ws.cell(hr, c, h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = hdr_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.cell(hr - 1, PL, "Prévu").font = Font(bold=True)
    ws.cell(hr - 1, RL, "Réalisé").font = Font(bold=True)
    for w in range(1, 8):
        for base in (PL, RL):
            cell = ws.cell(hr, base + w - 1, w)
            cell.number_format = '"S"0'
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="center")
    dv = DataValidation(type="list", formula1='"À faire,En cours,Terminé"', allow_blank=True)
    ws.add_data_validation(dv)
    for i, (name, ph, role, a, b) in enumerate(T):
        r = hr + 1 + i
        dr, fr, st = AVANCEMENT.get(name, (None, None, "À faire"))
        for c, v in enumerate([name, ph, role, who(role, a), a, b, f"=F{r}-E{r}+1", dr, fr, st], 1):
            cell = ws.cell(r, c, v)
            cell.border = Border(bottom=thin)
            if c in (5, 6, 7, 8, 9):
                cell.alignment = Alignment(horizontal="center")
        ws.cell(r, 2).fill = PatternFill("solid", fgColor=PH[ph].lstrip("#"))
        ws.cell(r, 2).font = Font(color="FFFFFF", bold=True)
        dv.add(ws.cell(r, 10))
        for w in range(1, 8):
            col_p, col_r = get_column_letter(PL + w - 1), get_column_letter(RL + w - 1)
            ws.cell(r, PL + w - 1, f'=IF(AND({col_p}${hr}>=$E{r},{col_p}${hr}<=$F{r}),"■","")')
            ws.cell(r, RL + w - 1, f'=IF(AND($H{r}<>"",{col_r}${hr}>=$H{r},{col_r}${hr}<=$I{r}),"■","")')
    last = hr + len(T)
    rng_p = f"{get_column_letter(PL)}{hr + 1}:{get_column_letter(PL + 6)}{last}"
    rng_r = f"{get_column_letter(RL)}{hr + 1}:{get_column_letter(RL + 6)}{last}"
    ws.conditional_formatting.add(rng_p, FormulaRule(formula=[f'{get_column_letter(PL)}{hr + 1}="■"'],
                                  fill=PatternFill("solid", bgColor="0072B2", fgColor="0072B2"),
                                  font=Font(color="0072B2")))
    ws.conditional_formatting.add(rng_r, FormulaRule(formula=[f'{get_column_letter(RL)}{hr + 1}="■"'],
                                  fill=PatternFill("solid", bgColor="009E73", fgColor="009E73"),
                                  font=Font(color="009E73")))
    for col, wd in zip("ABCDEFGHIJ", (46, 13, 22, 16, 9, 9, 8, 9, 9, 11)):
        ws.column_dimensions[col].width = wd
    ws.column_dimensions["K"].width = 3
    for w in range(7):
        ws.column_dimensions[get_column_letter(PL + w)].width = 5
        ws.column_dimensions[get_column_letter(RL + w)].width = 5
    ws.row_dimensions[hr].height = 32
    ws.freeze_panes = ws.cell(hr + 1, 2)
    ws2 = wb.create_sheet("Jalons")
    ws2.append(("Semaine", "Date indicative", "Présentateur", "Jalon"))
    for w in range(1, 8):
        ws2.append((f"S{w}", DATES[w - 1], PRESENTATEURS[w - 1],
                    "Mini-compte rendu (10 min)" + (" ; " + EXTRA[w] if w in EXTRA else "")))
    ws3 = wb.create_sheet("Rôles")
    ws3.append(("Rôle", "S1 à S4", "S5 à S7 (après rotation)"))
    for role in R1:
        if role != "Tous":
            ws3.append((role, R1[role], R2[role]))
    for col, wd in zip("ABC", (24, 18, 24)):
        ws3.column_dimensions[col].width = wd
    for col, wd in zip("ABCD", (10, 16, 16, 46)):
        ws2.column_dimensions[col].width = wd
    wb.save(OUT + "gantt_source.xlsx")
    print("xlsx ok")


if __name__ == "__main__":
    png()
    xlsx()
