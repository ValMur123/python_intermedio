"""Gráficos verticales para el reel, con las cifras de datos/procesados/resumen.json.

Uso (desde tarea_3/):  python reel/graficos_reel.py
Genera recursos/chart_medianas.png, chart_robustez.png y chart_km2.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).parent
RESUMEN = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parent / "datos" / "procesados" / "resumen.json"
SALIDA = AQUI / "recursos"
R = json.loads(RESUMEN.read_text(encoding="utf-8"))

FONDO, PANEL, TEXTO, TENUE, LUZ, MINA, GRIS = "#0b1020", "#151d3a", "#e8ebf5", "#9aa3c4", "#ffc857", "#e0703a", "#6b7499"
plt.rcParams.update({"font.size": 22, "text.color": TEXTO, "axes.labelcolor": TENUE,
                     "xtick.color": TENUE, "ytick.color": TENUE, "font.family": "DejaVu Sans"})
coma = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")


def lienzo(titulo):
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=110)
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(PANEL)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(TENUE)
    ax.set_yticks([])
    ax.set_title(titulo, loc="left", fontsize=24, fontweight="bold", color=TEXTO, pad=18)
    return fig, ax


def barras(ax, etiquetas, valores, colores, fmt):
    b = ax.bar(etiquetas, valores, color=colores, width=0.62)
    for r, v in zip(b, valores):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height(), fmt(v), ha="center", va="bottom",
                fontsize=26, fontweight="bold", color=TEXTO)
    ax.set_ylim(0, max(valores) * 1.22)


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(SALIDA / nombre, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  ·", nombre)


# 1. Medianas de luz total
fig, ax = lienzo("Luz total mediana por distrito")
barras(ax, ["Con minería", "Sin minería"], [R["mediana_luz_minero"], R["mediana_luz_no_minero"]],
       [MINA, GRIS], lambda v: coma(v))
guardar(fig, "chart_medianas.png")

# 2. Robustez: a mayor mina, mayor brecha
fig, ax = lienzo("Veces más luz según el tamaño de la mina")
rob = R["robustez_umbral"]
barras(ax, [f"> {u['umbral_km2']} km²" for u in rob], [u["veces_mas_luz"] for u in rob],
       [LUZ, "#f5a94d", MINA, "#c4502a"], lambda v: coma(v) + "×")
ax.set_xlabel("Área minera del distrito (controlando tamaño, lluvia y departamento)", fontsize=16)
guardar(fig, "chart_robustez.png")

# 3. Luz por km²
fig, ax = lienzo("Luz por km² (intensidad)")
barras(ax, ["Con minería", "Sin minería"], [R["luz_media_km2_minero"], R["luz_media_km2_no_minero"]],
       [MINA, GRIS], lambda v: coma(v, 2))
guardar(fig, "chart_km2.png")
