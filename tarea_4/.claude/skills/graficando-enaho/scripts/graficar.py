"""Gráficos de pobreza monetaria ENAHO a partir de salidas/personas_AAAA.parquet.

    uv run graficar.py --grafico area|sexo|departamento|todos [--sexo-de persona|jefe] [--anio 2024]

Todas las cifras se ponderan con facpob07 (porcentaje de personas). Barras desde cero, un solo
color, valor en cada barra, título analítico, fuente al pie. PNG a 200 dpi en --figuras.
Ninguna etiqueta de valor queda sobre la línea del total nacional: el script lo verifica y falla si no.
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
import unicodedata
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


def y_o_e(siguiente: str) -> str:
    """'e' si la palabra siguiente empieza con 'i' o con 'hi' + consonante; en otro caso 'y'.

    Regla del proyecto: Ica -> 'e Ica'; Hilda -> 'e Hilda'; Ayacucho, Huánuco -> 'y'.
    (Casos con diptongo, como 'hielo' o 'hierro', conservan 'y'; no aparecen en nombres de departamento.)
    """
    s = unicodedata.normalize("NFD", siguiente.strip().lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "e" if re.match(r"(i|hi(?![aeiou]))", s) else "y"


def nota_fuente(anio: int, n: int, extra: str = "") -> str:
    base = f"Fuente: INEI, ENAHO {anio} (módulos 02 y 34). Residentes habituales, n = {n:,}. Estimaciones ponderadas con facpob07."
    return f"{base} {extra}".strip()


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


# --- colocación de etiquetas sin choques con la línea del total nacional ---------------------------
MARGEN_PX = 4  # separación mínima entre una etiqueta y la línea, en píxeles de pantalla


def _choca(bbox, pos_px: float, eje: str) -> bool:
    lo, hi = (bbox.y0, bbox.y1) if eje == "y" else (bbox.x0, bbox.x1)
    return lo - MARGEN_PX <= pos_px <= hi + MARGEN_PX


def poner_valor(fig, ax, texto: str, val: float, pos: float, x: float | None = None, y: float | None = None,
                fontsize: float = 12, bold: bool = True) -> plt.Text:
    """Escribe el valor de una barra. Prueba: fuera del extremo, dentro de la barra, o más allá de la línea.

    Barras verticales: x = posición de la barra, la línea es horizontal (pos = total nacional en y).
    Barras horizontales: y = posición de la barra, la línea es vertical (pos = total nacional en x).
    """
    r = fig.canvas.get_renderer()
    vertical = x is not None
    eje = "y" if vertical else "x"
    pos_px = ax.transData.transform((0, pos) if vertical else (pos, 0))[1 if vertical else 0]
    cero_px = ax.transData.transform((0, 0))[1 if vertical else 0]
    delta = 0.8 if vertical else 0.5
    if vertical:
        cands = [(val + delta, "bottom", TEXTO, "fuera"), (val - delta, "top", "white", "dentro"),
                 (max(val, pos) + 1.5 * delta, "bottom", TEXTO, "sobre la línea")]
    else:
        cands = [(val + delta, "left", TEXTO, "fuera"), (val - delta, "right", "white", "dentro"),
                 (max(val, pos) + delta, "left", TEXTO, "tras la línea")]
    for coord, alin, color, _ in cands:
        kw = dict(ha="center", va=alin) if vertical else dict(ha=alin, va="center")
        t = ax.text(x if vertical else coord, coord if vertical else y, texto, fontsize=fontsize,
                    fontweight="bold" if bold else "normal", color=color, zorder=5, **kw)
        bb = t.get_window_extent(r)
        dentro_ok = (bb.y0 if vertical else bb.x0) >= cero_px - 1 if color == "white" else True
        if not _choca(bb, pos_px, eje) and dentro_ok:
            return t
        t.remove()
    raise RuntimeError(f"No hay posición sin choque para la etiqueta '{texto}'.")


def verificar_sin_choques(fig, ax, etiquetas: list, pos: float, eje: str) -> None:
    """Falla si alguna etiqueta de valor queda sobre la línea del total nacional."""
    r = fig.canvas.get_renderer()
    pos_px = ax.transData.transform((0, pos) if eje == "y" else (pos, 0))[1 if eje == "y" else 0]
    malas = [t.get_text() for t in etiquetas if _choca(t.get_window_extent(r), pos_px, eje)]
    if malas:
        raise RuntimeError(f"Etiquetas sobre la línea del total nacional: {malas}")
    print(f"  verificado: {len(etiquetas)} etiquetas sin choque con la línea del total nacional")


def barras_verticales(df_vals: pd.Series, etiquetas: list[str], titulo: str, subtitulo: str, nota: str,
                      nacional: float, ruta: Path) -> None:
    fig, ax = base_figura(titulo, subtitulo, nota, 7.5, 6)
    x = np.arange(len(df_vals))
    ax.bar(x, df_vals.values, width=0.5, color=COLOR, zorder=3)
    ax.axhline(nacional, color=GRIS, lw=1, ls="--", zorder=2)
    # Espacio a la derecha para rotular el extremo de la línea fuera de las barras.
    ax.set_xlim(-0.6, len(df_vals) - 1 + 1.0)
    ax.set_ylim(0, max(df_vals.max(), nacional) * 1.25)
    fig.canvas.draw()
    textos = [poner_valor(fig, ax, f"{v:.1f} %", v, nacional, x=xi) for xi, v in zip(x, df_vals.values)]
    x_rot = len(df_vals) - 1 + 0.4
    rot = ax.text(x_rot, nacional + 0.4, f"Total nacional\n{nacional:.1f} %", ha="left", va="bottom",
                  fontsize=9, color=GRIS, zorder=5, linespacing=1.1)
    ax.set_xticks(x, etiquetas, fontsize=11, color=TEXTO)
    ax.set_ylabel("% de personas en situación de pobreza", fontsize=10, color=GRIS)
    ax.yaxis.grid(True, color=REJILLA, zorder=0)
    ax.tick_params(axis="y", colors=GRIS, length=0)
    ax.tick_params(axis="x", length=0)
    ax.spines["left"].set_visible(False)
    fig.canvas.draw()
    verificar_sin_choques(fig, ax, textos, nacional, "y")
    r = fig.canvas.get_renderer()
    rb = rot.get_window_extent(r)
    if any(rb.overlaps(p.get_window_extent(r)) for p in ax.patches):
        raise RuntimeError("El rótulo 'Total nacional' se superpone con una barra.")
    guardar(fig, ruta)


def grafico_area(df, anio, carpeta, nacional):
    urb = df["urbano"]
    vals = pd.Series({"Urbano": tasa_ponderada(df.loc[urb, "pobre"], df.loc[urb, "facpob07"]),
                      "Rural": tasa_ponderada(df.loc[~urb, "pobre"], df.loc[~urb, "facpob07"])})
    dif = vals["Rural"] - vals["Urbano"]
    titulo = f"La pobreza rural ({vals['Rural']:.1f} %) supera en {dif:.1f} puntos porcentuales a la urbana ({vals['Urbano']:.1f} %), Perú {anio}"
    barras_verticales(vals, list(vals.index), titulo,
                      "Pobreza monetaria por área de residencia · % de personas · urbano = estrato 1 a 5",
                      nota_fuente(anio, len(df)), nacional, carpeta / f"pobreza_urbano_rural_{anio}.png")


def grafico_sexo(df, anio, carpeta, nacional, sexo_de):
    if sexo_de == "jefe":
        jefes = df.loc[df["p203"] == 1, ["conglome", "vivienda", "hogar", "p207"]].rename(columns={"p207": "sexo_jefe"})
        d = df.merge(jefes, on=["conglome", "vivienda", "hogar"], how="inner", validate="m:1")
        col, etiq = "sexo_jefe", ("Jefe hombre", "Jefa mujer")
        frase = ("las personas en hogares con jefe hombre", "las personas en hogares con jefa mujer")
        sub = ("Pobreza monetaria según el sexo de quien jefatura el hogar · % de personas · "
               "solo hogares cuyo jefe o jefa es residente habitual")
        arch = f"pobreza_sexo_jefe_hogar_{anio}.png"
    else:
        d, col, etiq = df, "p207", ("Hombres", "Mujeres")
        frase = ("los hombres", "las mujeres")
        sub = "Pobreza monetaria según el sexo de la persona · % de personas"
        arch = f"pobreza_sexo_{anio}.png"
    g = grupo(d, col)
    vals = pd.Series({etiq[0]: g[1], etiq[1]: g[2]})
    dif = vals.iloc[1] - vals.iloc[0]
    if abs(dif) < 1 and sexo_de == "persona":
        titulo = (f"La pobreza apenas difiere entre hombres ({vals.iloc[0]:.1f} %) y mujeres ({vals.iloc[1]:.1f} %): "
                  f"{abs(dif):.1f} puntos porcentuales, Perú {anio}")
    elif abs(dif) < 1:
        titulo = (f"La pobreza apenas difiere según el sexo de la jefatura del hogar: {vals.iloc[0]:.1f} % con jefe hombre "
                  f"y {vals.iloc[1]:.1f} % con jefa mujer, Perú {anio}")
    else:
        k = 1 if dif > 0 else 0
        titulo = (f"La pobreza afecta más a {frase[k]} ({vals.iloc[k]:.1f} %) que a {frase[1 - k]} "
                  f"({vals.iloc[1 - k]:.1f} %): {abs(dif):.1f} puntos porcentuales, Perú {anio}")
    # n real de cada gráfico: en el de jefatura son solo los residentes de hogares con jefe/a residente.
    barras_verticales(vals, list(vals.index), titulo, sub, nota_fuente(anio, len(d)), nacional, carpeta / arch)


def nota_departamento(anio: int, n: int, g: pd.Series, referencias: Path) -> str:
    """Nota de fuente con el contraste del método oficial; las cifras salen del CSV de referencia."""
    extra = ""
    ref_csv = referencias / "pobreza_departamento_2024.csv"
    if ref_csv.exists():
        ref = pd.read_csv(ref_csv, dtype={"ccdd": str}).set_index("ccdd")["pobreza_pct"].reindex(g.index)
        menor = g.idxmin()
        dif = (g - ref).abs().drop(menor)
        mayor = dif.idxmax()
        extra = (f"Estimación con facpob07; con el método oficial del INEI (factor07 × mieperho) {nombre(menor)} es "
                 f"{ref[menor]:.1f} % {y_o_e(nombre(mayor))} {nombre(mayor)} {ref[mayor]:.1f} %. Ver salidas/validacion.txt.")
    return nota_fuente(anio, n, extra)


def grafico_departamento(df, anio, carpeta, nacional, referencias):
    g = grupo(df, "departamento").sort_values(ascending=False)
    etiquetas = [nombre(c) for c in g.index]
    titulo = (f"{etiquetas[0]} ({g.iloc[0]:.1f} %) tiene la mayor pobreza {y_o_e(etiquetas[-1])} {etiquetas[-1]} "
              f"({g.iloc[-1]:.1f} %) la menor entre los 25 departamentos, Perú {anio}")
    fig, ax = base_figura(titulo, "Pobreza monetaria por departamento · % de personas · ordenado de mayor a menor",
                          nota_departamento(anio, len(df), g, referencias), 9, 9.6, left=0.16)
    y = np.arange(len(g))
    ax.barh(y, g.values, height=0.65, color=COLOR, zorder=3)
    ax.axvline(nacional, color=GRIS, lw=1, ls="--", zorder=2)
    ax.set_xlim(0, g.max() * 1.12)
    ax.set_yticks(y, etiquetas, fontsize=10, color=TEXTO)
    ax.invert_yaxis()
    fig.canvas.draw()
    textos = [poner_valor(fig, ax, f"{v:.1f} %", v, nacional, y=yi, fontsize=9.5, bold=False) for yi, v in zip(y, g.values)]
    ax.text(nacional + 0.4, len(g) - 1, f"Total nacional: {nacional:.1f} %", fontsize=9, color=GRIS, va="center")
    ax.set_xlabel("% de personas en situación de pobreza", fontsize=10, color=GRIS)
    ax.xaxis.grid(True, color=REJILLA, zorder=0)
    ax.tick_params(axis="x", colors=GRIS, length=0)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    fig.canvas.draw()
    verificar_sin_choques(fig, ax, textos, nacional, "x")
    guardar(fig, carpeta / f"pobreza_departamento_{anio}.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grafico", choices=["area", "sexo", "departamento", "todos"], default="todos")
    ap.add_argument("--sexo-de", choices=["persona", "jefe"], default="persona")
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--base", type=Path, default=None)
    ap.add_argument("--figuras", type=Path, default=Path("figuras"))
    ap.add_argument("--referencias", type=Path, default=Path("referencias"))
    a = ap.parse_args()
    base = a.base or Path("salidas") / f"personas_{a.anio}.parquet"
    if not base.exists():
        print(f"ERROR: no existe {base}. Ejecuta primero la skill limpiando-enaho.", file=sys.stderr)
        return 1
    df = pd.read_parquet(base)
    df["departamento"] = df["departamento"].astype(str)
    nacional = tasa_ponderada(df["pobre"], df["facpob07"])
    if a.grafico in ("area", "todos"):
        grafico_area(df, a.anio, a.figuras, nacional)
    if a.grafico in ("sexo", "todos"):
        grafico_sexo(df, a.anio, a.figuras, nacional, a.sexo_de)
    if a.grafico in ("departamento", "todos"):
        grafico_departamento(df, a.anio, a.figuras, nacional, a.referencias)
    return 0


if __name__ == "__main__":
    sys.exit(main())
