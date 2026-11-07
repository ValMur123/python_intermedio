"""Gráficos de pobreza monetaria ENAHO a partir de salidas/personas_AAAA.parquet.

    uv run graficar.py --grafico area|sexo|departamento|todos [--sexo-de persona|jefe] [--anio 2024]

Todas las cifras se ponderan con facpob07 (porcentaje de personas). Barras desde cero, un solo
color, valor en cada barra, título analítico, fuente al pie. PNG a 200 dpi en --figuras.
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Reutiliza la función de ponderación y los nombres de departamento de la skill de limpieza.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "limpiando-enaho" / "scripts"))
from limpiar import DEPARTAMENTOS, tasa_ponderada  # noqa: E402

COLOR = "#1F5F8B"      # único color de las barras
TEXTO = "#222222"
GRIS = "#6B6B6B"
REJILLA = "#E3E3E3"
DPI = 200
NOMBRES = {"ANCASH": "Áncash", "APURIMAC": "Apurímac", "HUANUCO": "Huánuco", "JUNIN": "Junín",
           "SAN MARTIN": "San Martín", "MADRE DE DIOS": "Madre de Dios", "LA LIBERTAD": "La Libertad"}


def nombre(cod: str) -> str:
    n = DEPARTAMENTOS[cod]
    return NOMBRES.get(n, n.title())


def pct(x: float) -> str:
    return f"{x:.1f}".replace(".", ",") if False else f"{x:.1f} %"


def grupo(df: pd.DataFrame, por: str) -> pd.Series:
    """Pobreza ponderada (% de personas) por grupo."""
    return df.groupby(por).apply(lambda g: tasa_ponderada(g["pobre"], g["facpob07"]), include_groups=False)


def base_figura(titulo: str, subtitulo: str, nota: str, ancho: float, alto: float, left: float = 0.12):
    """Figura con título analítico, subtítulo y fuente; el espacio se calcula según las líneas de texto."""
    chars = int(ancho * 8.2)  # caracteres por línea aprox. a 14 pt negrita
    t = textwrap.fill(titulo, width=chars)
    st = textwrap.fill(subtitulo, width=int(ancho * 13))
    n = textwrap.fill(nota, width=int(ancho * 14))
    h_t, h_s, h_n = 0.27 * (t.count(chr(10)) + 1), 0.2 * (st.count(chr(10)) + 1), 0.17 * (n.count(chr(10)) + 1)
    top_in, bot_in = 0.25 + h_t + 0.08 + h_s + 0.35, 0.25 + h_n + 0.55
    fig, ax = plt.subplots(figsize=(ancho, alto))
    fig.subplots_adjust(top=1 - top_in / alto, bottom=bot_in / alto, left=left, right=0.95)
    fig.text(0.02, 1 - 0.25 / alto, t, fontsize=14, fontweight="bold", color=TEXTO, va="top", ha="left", linespacing=1.15)
    fig.text(0.02, 1 - (0.25 + h_t + 0.08) / alto, st, fontsize=10.5, color=GRIS, va="top", ha="left")
    fig.text(0.02, 0.2 / alto, n, fontsize=8.5, color=GRIS, va="bottom", ha="left")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    return fig, ax


def guardar(fig, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"Guardado: {ruta}")


def barras_verticales(df_vals: pd.Series, etiquetas: list[str], titulo: str, subtitulo: str, nota: str,
                      nacional: float, ruta: Path) -> None:
    fig, ax = base_figura(titulo, subtitulo, nota, 7.5, 6)
    x = np.arange(len(df_vals))
    ax.bar(x, df_vals.values, width=0.5, color=COLOR, zorder=3)
    for xi, val in zip(x, df_vals.values):
        ax.text(xi, val + 0.8, f"{val:.1f} %", ha="center", va="bottom", fontsize=12, fontweight="bold", color=TEXTO,
                zorder=5, bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.axhline(nacional, color=GRIS, lw=1, ls="--", zorder=2)
    ax.text((len(df_vals) - 1) / 2, nacional + 0.3, f"Total nacional: {nacional:.1f} %", ha="center",
            va="bottom", fontsize=9, color=GRIS, zorder=5)
    ax.set_xlim(-0.6, len(df_vals) - 0.4)
    ax.set_xticks(x, etiquetas, fontsize=11, color=TEXTO)
    ax.set_ylim(0, max(df_vals.max(), nacional) * 1.2)
    ax.set_ylabel("% de personas en situación de pobreza", fontsize=10, color=GRIS)
    ax.yaxis.grid(True, color=REJILLA, zorder=0)
    ax.tick_params(axis="y", colors=GRIS, length=0)
    ax.tick_params(axis="x", length=0)
    ax.spines["left"].set_visible(False)
    guardar(fig, ruta)


def grafico_area(df, anio, nota, nacional, carpeta):
    urb = df["urbano"]
    vals = pd.Series({"Urbano": tasa_ponderada(df.loc[urb, "pobre"], df.loc[urb, "facpob07"]),
                      "Rural": tasa_ponderada(df.loc[~urb, "pobre"], df.loc[~urb, "facpob07"])})
    dif = vals["Rural"] - vals["Urbano"]
    titulo = f"La pobreza rural ({vals['Rural']:.1f} %) supera en {dif:.1f} puntos porcentuales a la urbana ({vals['Urbano']:.1f} %), Perú {anio}"
    barras_verticales(vals, list(vals.index), titulo.replace(", Perú", ",\nPerú"),
                      "Pobreza monetaria por área de residencia · % de personas · urbano = estrato 1 a 5",
                      nota, nacional, carpeta / f"pobreza_urbano_rural_{anio}.png")


def grafico_sexo(df, anio, nota, nacional, carpeta, sexo_de):
    if sexo_de == "jefe":
        jefes = df.loc[df["p203"] == 1, ["conglome", "vivienda", "hogar", "p207"]].rename(columns={"p207": "sexo_jefe"})
        d = df.merge(jefes, on=["conglome", "vivienda", "hogar"], how="inner", validate="m:1")
        col, etiq = "sexo_jefe", ("Jefe hombre", "Jefa mujer")
        frase = ("las personas en hogares con jefe hombre", "las personas en hogares con jefa mujer")
        sub = (f"Pobreza monetaria según el sexo de quien jefatura el hogar · % de personas · "
               f"n = {len(d):,} residentes en hogares con jefe/a residente habitual")
        arch = f"pobreza_sexo_jefe_hogar_{anio}.png"
    else:
        d, col, etiq = df, "p207", ("Hombres", "Mujeres")
        frase = ("los hombres", "las mujeres")
        sub = "Pobreza monetaria según el sexo de la persona · % de personas"
        arch = f"pobreza_sexo_{anio}.png"
    g = grupo(d, col)
    vals = pd.Series({etiq[0]: g[1], etiq[1]: g[2]})
    dif = vals.iloc[1] - vals.iloc[0]
    if abs(dif) < 1:
        titulo = (f"La pobreza apenas difiere entre {frase[0].split(' ', 1)[0] if sexo_de == 'persona' else 'hogares'} "
                  f"según sexo: {vals.iloc[0]:.1f} % frente a {vals.iloc[1]:.1f} % (diferencia de {abs(dif):.1f} pp), Perú {anio}")
        if sexo_de == "persona":
            titulo = (f"La pobreza apenas difiere entre hombres ({vals.iloc[0]:.1f} %) y mujeres ({vals.iloc[1]:.1f} %): "
                      f"{abs(dif):.1f} puntos porcentuales, Perú {anio}")
    else:
        k = 1 if dif > 0 else 0
        titulo = (f"La pobreza afecta más a {frase[k]} ({vals.iloc[k]:.1f} %) que a {frase[1 - k]} "
                  f"({vals.iloc[1 - k]:.1f} %): {abs(dif):.1f} puntos porcentuales, Perú {anio}")
    barras_verticales(vals, list(vals.index), titulo, sub, nota, nacional, carpeta / arch)


def grafico_departamento(df, anio, nota, nacional, carpeta):
    g = grupo(df, "departamento").sort_values(ascending=False)
    etiquetas = [nombre(c) for c in g.index]
    fig, ax = base_figura(
        f"{etiquetas[0]} ({g.iloc[0]:.1f} %) tiene la mayor pobreza y {etiquetas[-1]} ({g.iloc[-1]:.1f} %) la menor entre los 25 departamentos, Perú {anio}",
        "Pobreza monetaria por departamento · % de personas · ordenado de mayor a menor",
        nota, 9, 9.6, left=0.16)
    y = np.arange(len(g))
    ax.barh(y, g.values, height=0.65, color=COLOR, zorder=3)
    for yi, val in zip(y, g.values):
        ax.text(val + 0.5, yi, f"{val:.1f} %", va="center", ha="left", fontsize=9.5, color=TEXTO, zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.2))
    ax.axvline(nacional, color=GRIS, lw=1, ls="--", zorder=2)
    ax.text(nacional + 0.4, len(g) - 1, f"Total nacional: {nacional:.1f} %", fontsize=9, color=GRIS, va="center")
    ax.set_yticks(y, etiquetas, fontsize=10, color=TEXTO)
    ax.invert_yaxis()
    ax.set_xlim(0, g.max() * 1.12)
    ax.set_xlabel("% de personas en situación de pobreza", fontsize=10, color=GRIS)
    ax.xaxis.grid(True, color=REJILLA, zorder=0)
    ax.tick_params(axis="x", colors=GRIS, length=0)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    guardar(fig, carpeta / f"pobreza_departamento_{anio}.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grafico", choices=["area", "sexo", "departamento", "todos"], default="todos")
    ap.add_argument("--sexo-de", choices=["persona", "jefe"], default="persona")
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--base", type=Path, default=None)
    ap.add_argument("--figuras", type=Path, default=Path("figuras"))
    a = ap.parse_args()
    base = a.base or Path("salidas") / f"personas_{a.anio}.parquet"
    if not base.exists():
        print(f"ERROR: no existe {base}. Ejecuta primero la skill limpiando-enaho.", file=sys.stderr)
        return 1
    df = pd.read_parquet(base)
    df["departamento"] = df["departamento"].astype(str)
    nacional = tasa_ponderada(df["pobre"], df["facpob07"])
    nota = f"Fuente: INEI, ENAHO {a.anio} (módulos 02 y 34). Residentes habituales, n = {len(df):,}. Estimaciones ponderadas con facpob07."
    if a.grafico in ("area", "todos"):
        grafico_area(df, a.anio, nota, nacional, a.figuras)
    if a.grafico in ("sexo", "todos"):
        grafico_sexo(df, a.anio, nota, nacional, a.figuras, a.sexo_de)
    if a.grafico in ("departamento", "todos"):
        grafico_departamento(df, a.anio, nota, nacional, a.figuras)
    return 0


if __name__ == "__main__":
    sys.exit(main())
