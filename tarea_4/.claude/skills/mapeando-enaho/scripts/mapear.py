"""Mapa coroplético de pobreza monetaria departamental (ENAHO) desde salidas/personas_AAAA.parquet.

    uv run mapear.py [--anio 2024]

Une indicadores y geometrías por código (ubigeo[:2] = FIRST_IDDP), nunca por nombre. Falla si no hay
exactamente 25 departamentos con dato o si Lima (15) y Callao (07) no están separados.
Salidas: mapas/pobreza_departamento_AAAA.png y salidas/comparacion_mapa.csv.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import cm, colors  # noqa: E402

# Reutiliza el estilo y los helpers de graficando-enaho (que a su vez usa limpiando-enaho).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "graficando-enaho" / "scripts"))
from graficar import GRIS, TEXTO, base_figura, guardar, nombre, nota_fuente, y_o_e  # noqa: E402
from limpiar import DEPARTAMENTOS, tasa_ponderada  # noqa: E402

CMAP = "Blues"           # un solo color, de claro a oscuro
TOL_FALLA_PP = 1.0       # diferencia contra la referencia que ya no se explica por el método
CALLAO, LIMA = "07", "15"


def fallar(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def cargar_geo(ruta: Path) -> gpd.GeoDataFrame:
    if not ruta.exists():
        fallar(f"no existe {ruta}. Descárgalo con curl en referencias/ (ver SKILL.md).")
    geo = gpd.read_file(ruta)
    if "FIRST_IDDP" not in geo.columns:
        fallar(f"{ruta.name} no tiene la columna FIRST_IDDP; columnas: {list(geo.columns)}")
    geo["FIRST_IDDP"] = geo["FIRST_IDDP"].astype(str)
    return geo


def indicadores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(ccdd=df["ubigeo"].str[:2])  # llave de unión: ubigeo[:2]
    por = df.groupby("ccdd").apply(
        lambda g: pd.Series({"pobreza_pct": tasa_ponderada(g["pobre"], g["facpob07"]), "n_personas_muestra": len(g)}),
        include_groups=False)
    return por.reset_index()


def unir(geo: gpd.GeoDataFrame, ind: pd.DataFrame) -> gpd.GeoDataFrame:
    """Une por código y exige 25 unidades con dato; falla si falta alguna."""
    esperados = set(DEPARTAMENTOS)
    for etiqueta, codigos in (("GeoJSON (FIRST_IDDP)", set(geo["FIRST_IDDP"])), ("ENAHO (ubigeo[:2])", set(ind["ccdd"]))):
        if codigos != esperados:
            fallar(f"{etiqueta}: faltan {sorted(esperados - codigos)} / sobran {sorted(codigos - esperados)}")
    if geo["FIRST_IDDP"].duplicated().any():
        fallar("FIRST_IDDP duplicado en el GeoJSON")
    m = geo.merge(ind, left_on="FIRST_IDDP", right_on="ccdd", how="left", validate="1:1")
    if len(m) != 25 or m["pobreza_pct"].isna().any():
        fallar(f"se esperaban 25 departamentos con dato; sin dato: {m.loc[m['pobreza_pct'].isna(), 'FIRST_IDDP'].tolist()}")
    # Lima y Callao separados: dos geometrías y dos filas de datos distintas.
    fila = m.set_index("FIRST_IDDP")
    if fila.loc[LIMA, "geometry"].equals(fila.loc[CALLAO, "geometry"]) or fila.loc[LIMA, "pobreza_pct"] == fila.loc[CALLAO, "pobreza_pct"]:
        fallar("Lima (15) y Callao (07) no están separados")
    print("Unión por código: 25/25 departamentos con dato; Lima (15) y Callao (07) separados.")
    return m


def comparar(m: gpd.GeoDataFrame, ref_csv: Path, salida: Path) -> pd.DataFrame:
    """Compara con la referencia de la sesión 16 y guarda salidas/comparacion_mapa.csv."""
    if not ref_csv.exists():
        fallar(f"no existe {ref_csv}")
    ref = pd.read_csv(ref_csv, dtype={"ccdd": str}).set_index("ccdd")["pobreza_pct"]
    c = m[["FIRST_IDDP", "pobreza_pct", "n_personas_muestra"]].rename(columns={"FIRST_IDDP": "ccdd"}).copy()
    c["n_personas_muestra"] = c["n_personas_muestra"].astype(int)
    c["departamento"] = c["ccdd"].map(nombre)
    c["pobreza_facpob07"] = c["pobreza_pct"].round(2)
    c["pobreza_referencia"] = c["ccdd"].map(ref)
    c["diferencia_pp"] = (c["pobreza_pct"] - c["pobreza_referencia"]).round(2)
    c["abs_pp"] = c["diferencia_pp"].abs()
    c = c[["ccdd", "departamento", "pobreza_facpob07", "pobreza_referencia", "diferencia_pp", "abs_pp",
           "n_personas_muestra"]].sort_values("ccdd")
    salida.parent.mkdir(parents=True, exist_ok=True)
    c.to_csv(salida, index=False, encoding="utf-8")
    peor = c.loc[c["abs_pp"].idxmax()]
    print(f"Comparación con referencia: diferencia máxima {peor['abs_pp']:.2f} pp ({peor['departamento']}); "
          f"{int((c['abs_pp'] <= 0.2).sum())}/25 dentro de 0.2 pp. Guardado: {salida}")
    print("  Las diferencias vienen del método: este mapa pondera personas con facpob07; la referencia usa la "
          "sumaria con factor07 × mieperho.")
    if peor["abs_pp"] > TOL_FALLA_PP:
        fallar(f"{peor['departamento']} difiere {peor['abs_pp']:.2f} pp de la referencia (> {TOL_FALLA_PP} pp): "
               "no se explica solo por el método de ponderación; revisa la base procesada.")
    return c


def color_texto(rgba) -> str:
    lum = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
    return TEXTO if lum > 0.5 else "white"


def dibujar(m: gpd.GeoDataFrame, anio: int, n: int, nacional: float, dif_max: float, ruta: Path) -> None:
    vmax = float(np.ceil(m["pobreza_pct"].max() / 10) * 10)
    norm = colors.Normalize(vmin=0, vmax=vmax)          # escala desde 0
    cmap = matplotlib.colormaps[CMAP]
    sup, inf = m.loc[m["pobreza_pct"].idxmax()], m.loc[m["pobreza_pct"].idxmin()]
    s_nom, i_nom = nombre(sup["FIRST_IDDP"]), nombre(inf["FIRST_IDDP"])
    sobre = int((m["pobreza_pct"] > nacional).sum())
    titulo = (f"La pobreza va de {inf['pobreza_pct']:.1f} % en {i_nom} a {sup['pobreza_pct']:.1f} % en {s_nom}; "
              f"{sobre} de 25 departamentos superan el total nacional ({nacional:.1f} %), Perú {anio}")
    nota = nota_fuente(anio, n, f"La referencia de la sesión 16 usa factor07 × mieperho "
                                f"(diferencia máxima {dif_max:.1f} pp, ver salidas/comparacion_mapa.csv).")
    fig, ax = base_figura(titulo, "Pobreza monetaria por departamento · % de personas · escala de un color desde 0 %",
                          nota, 7.5, 10.2, left=0.05)
    m.plot(ax=ax, column="pobreza_pct", cmap=cmap, norm=norm, edgecolor="white", linewidth=0.6)
    ax.set_aspect("equal")
    ax.set_axis_off()

    # Valor en cada departamento; Callao es diminuto: se rotula fuera, en el mar, con una línea.
    for _, f in m.iterrows():
        cod, val = f["FIRST_IDDP"], f["pobreza_pct"]
        p = f.geometry.representative_point()
        if cod == CALLAO:
            ax.annotate(f"Callao {val:.1f}", xy=(p.x, p.y), xytext=(p.x - 2.9, p.y - 0.9), fontsize=7.5, color=TEXTO,
                        ha="right", va="center", arrowprops=dict(arrowstyle="-", color=GRIS, lw=0.7))
            continue
        ax.text(p.x, p.y, f"{val:.1f}", fontsize=7, ha="center", va="center",
                color=color_texto(cmap(norm(val))), fontweight="bold")

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.035, pad=0.02, shrink=0.7)
    cb.set_ticks(np.arange(0, vmax + 1, 10))
    cb.set_ticklabels([f"{t:.0f} %" for t in np.arange(0, vmax + 1, 10)])
    cb.set_label("% de personas en situación de pobreza monetaria", fontsize=9.5, color=GRIS)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=9, colors=GRIS, length=0)
    guardar(fig, ruta)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--base", type=Path, default=None)
    ap.add_argument("--geojson", type=Path, default=Path("referencias/peru_departamental_simple.geojson"))
    ap.add_argument("--referencias", type=Path, default=Path("referencias"))
    ap.add_argument("--mapas", type=Path, default=Path("mapas"))
    ap.add_argument("--salidas", type=Path, default=Path("salidas"))
    a = ap.parse_args()
    base = a.base or a.salidas / f"personas_{a.anio}.parquet"
    if not base.exists():
        fallar(f"no existe {base}. Ejecuta primero la skill limpiando-enaho.")
    df = pd.read_parquet(base)
    geo = cargar_geo(a.geojson)
    ind = indicadores(df)
    m = unir(geo, ind)
    comp = comparar(m, a.referencias / "pobreza_departamento_2024.csv", a.salidas / "comparacion_mapa.csv")
    nacional = tasa_ponderada(df["pobre"], df["facpob07"])
    dibujar(m, a.anio, len(df), nacional, float(comp["abs_pp"].max()), a.mapas / f"pobreza_departamento_{a.anio}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
