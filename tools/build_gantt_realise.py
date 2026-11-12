# -*- coding: utf-8 -*-
"""Gantt réalisé (livrable final obligatoire) à partir de docs/gantt_source.xlsx.

Prévu en gris clair, réalisé en couleur (vert : terminé, orange : en cours). Les colonnes sont repérées
par leur titre, ligne 4 de la feuille « Gantt ». Usage : python tools/build_gantt_realise.py [numéro de semaine]
Le numéro de semaine, s'il est donné, figure dans le titre (« état à la fin de la semaine n »).
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

RACINE = Path(__file__).resolve().parents[1]
ws = load_workbook(RACINE / "docs/gantt_source.xlsx")["Gantt"]
entetes = {str(c.value).strip(): c.column - 1 for c in ws[4] if c.value}
col = {k: entetes[k] for k in ("Tâche", "Responsable", "Début prévu (S)", "Fin prévue (S)", "Début réel (S)", "Fin réelle (S)")}
col_statut = entetes.get("Statut")

taches = []
for ligne in ws.iter_rows(min_row=5, values_only=True):
    if not ligne[col["Tâche"]]:
        break
    statut = ligne[col_statut] if col_statut is not None else None
    taches.append((ligne[col["Tâche"]], ligne[col["Responsable"]], ligne[col["Début prévu (S)"]], ligne[col["Fin prévue (S)"]],
                   ligne[col["Début réel (S)"]], ligne[col["Fin réelle (S)"]], statut))

fig, ax = plt.subplots(figsize=(14, 0.42 * len(taches) + 2), dpi=150)
for i, (nom, resp, dp, fp, dr, fr, statut) in enumerate(taches):
    y = len(taches) - 1 - i
    ax.barh(y + 0.18, fp - dp + 1, left=dp - 1, height=0.32, color="#D9D9D9")
    if isinstance(dr, (int, float)):
        fin = fr if isinstance(fr, (int, float)) else dr
        ax.barh(y - 0.18, fin - dr + 1, left=dr - 1, height=0.32, color="#009E73" if statut == "Terminé" else "#E69F00")
    ax.text(max(fp, fr if isinstance(fr, (int, float)) else 0) + 0.08, y, resp or "", va="center", fontsize=7.5, color="#555555")
ax.set_yticks(range(len(taches)))
ax.set_yticklabels([t[0] for t in taches][::-1], fontsize=8.5)
ax.set_xticks([w + 0.5 for w in range(7)])
ax.set_xticklabels([f"S{w + 1}" for w in range(7)])
ax.set_xlim(0, 8.3)
for w in range(8):
    ax.axvline(w, color="#EEEEEE", lw=0.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
suffixe = f" (état à la fin de la semaine {sys.argv[1]})" if len(sys.argv) > 1 else ""
ax.set_title("Gantt réalisé — Groupe 6 · Dilemme du prisonnier répété" + suffixe, loc="left", fontsize=12, fontweight="bold")
ax.legend(handles=[Patch(color="#D9D9D9", label="prévu"), Patch(color="#009E73", label="réalisé, terminé"),
                   Patch(color="#E69F00", label="réalisé, en cours")], loc="upper right", frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(RACINE / "docs/gantt_realise.png")
print(f"docs/gantt_realise.png : {len(taches)} tâches")
