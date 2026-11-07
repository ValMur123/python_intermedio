"""Gráfico e indicadores de inflación de Lima Metropolitana 2020-2024 a partir del CSV del MCP.

    uv run scripts/grafico_bcrp.py

Lee SOLO salidas/bcrp_inflacion_2020_2024.csv (salida de la herramienta `serie` del MCP bcrp).
Escribe figuras/inflacion_lima_2020_2024.png y salidas/indicadores_bcrp.csv.
Toda resta, promedio y extremo se calcula aquí, en Python; no hay cifras escritas a mano.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "salidas" / "bcrp_inflacion_2020_2024.csv"
FIGURA = RAIZ / "figuras" / "inflacion_lima_2020_2024.png"
INDICADORES = RAIZ / "salidas" / "indicadores_bcrp.csv"

SERIES = {
    "PN01273PM": ("IPC general", "#1F5F8B"),
    "PN09822PM": ("Alimentos y bebidas", "#C8561E"),
    "PN01279PM": ("Subyacente", "#5B8E3E"),
}
META_MIN, META_MAX = 1.0, 3.0  # rango meta de inflación del BCRP (%)
TRAMOS = {
    "2020-2021": ("2020-01", "2021-12"),
    "2022-2023": ("2022-01", "2023-12"),
    "2024": ("2024-01", "2024-12"),
}


def cargar() -> pd.DataFrame:
    df = pd.read_csv(ENTRADA, dtype={"codigo": str, "periodo": str})
    esperadas = set(SERIES)
    if set(df["codigo"]) != esperadas:
        raise SystemExit(f"Series inesperadas en el CSV: {sorted(set(df['codigo']))}")
    ancho = df.pivot(index="periodo", columns="codigo", values="valor").sort_index()
    if ancho.shape[0] != 60 or ancho.isna().any().any():
        raise SystemExit("Se esperaban 60 meses completos (2020-01 a 2024-12) por serie.")
    ancho["brecha"] = ancho["PN09822PM"] - ancho["PN01279PM"]  # alimentos − subyacente, pp
    return ancho


def indicadores(ancho: pd.DataFrame) -> pd.DataFrame:
    filas = []

    def agrega(serie: str, indicador: str, valor, periodo: str = "", unidad: str = "% / pp") -> None:
        filas.append({"serie": serie, "indicador": indicador, "periodo": periodo,
                      "valor": round(float(valor), 2), "unidad": unidad})

    for cod, (nombre, _) in SERIES.items():
        s = ancho[cod]
        agrega(cod, "promedio 2020-2024", s.mean(), "2020-01/2024-12")
        agrega(cod, "máximo", s.max(), s.idxmax())
        agrega(cod, "mínimo", s.min(), s.idxmin())
        for tramo, (a, b) in TRAMOS.items():
            agrega(cod, f"promedio {tramo}", s.loc[a:b].mean(), f"{a}/{b}")
        agrega(cod, "valor dic-2024", s["2024-12"], "2024-12")
        agrega(cod, "meses sobre 3 % (rango meta)", (s > META_MAX).sum(), "2020-01/2024-12", "meses")
    b = ancho["brecha"]
    agrega("PN09822PM-PN01279PM", "brecha promedio alimentos − subyacente", b.mean(), "2020-01/2024-12")
    agrega("PN09822PM-PN01279PM", "brecha máxima", b.max(), b.idxmax())
    agrega("PN09822PM-PN01279PM", "brecha mínima", b.min(), b.idxmin())
    agrega("PN09822PM-PN01279PM", "brecha dic-2024", b["2024-12"], "2024-12")
    for tramo, (x, y) in TRAMOS.items():
        agrega("PN09822PM-PN01279PM", f"brecha promedio {tramo}", b.loc[x:y].mean(), f"{x}/{y}")
    out = pd.DataFrame(filas)
    out.to_csv(INDICADORES, index=False, encoding="utf-8")
    return out


def grafico(ancho: pd.DataFrame, ind: pd.DataFrame) -> None:
    fechas = pd.to_datetime(ancho.index + "-01")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axhspan(META_MIN, META_MAX, color="#BBBBBB", alpha=0.35, zorder=0,
               label="Rango meta del BCRP (1 %–3 %)")
    for cod, (nombre, color) in SERIES.items():
        ax.plot(fechas, ancho[cod], color=color, lw=2.2, label=f"{nombre} ({cod})")

    pico = ancho["PN09822PM"].idxmax()
    ax.annotate(f"Alimentos: máx. {ancho['PN09822PM'].max():.1f} %\n({pico})",
                xy=(pd.to_datetime(pico + "-01"), ancho["PN09822PM"].max()),
                xytext=(-120, -4), textcoords="offset points", fontsize=9, color="#C8561E",
                arrowprops=dict(arrowstyle="-", color="#C8561E"))
    ult = ancho.iloc[-1]
    ax.annotate(f"Dic-2024: general {ult['PN01273PM']:.1f} %,\nalimentos {ult['PN09822PM']:.1f} %,\n"
                f"subyacente {ult['PN01279PM']:.1f} %",
                xy=(fechas[-1], ult["PN01273PM"]), xytext=(-75, 95), textcoords="offset points",
                fontsize=9, ha="left", arrowprops=dict(arrowstyle="-", color="#555555"))

    ax.set_ylim(0, ancho[list(SERIES)].max().max() * 1.12)
    ax.set_ylabel("Variación % a 12 meses")
    ax.grid(axis="y", alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_title("En Lima, la inflación de alimentos lideró el pico de 2022-2023 (máx. 13.2 %) y cerró 2024 bajo la subyacente",
                 fontsize=12.5, loc="left", pad=12, wrap=True)
    fig.text(0.01, 0.01,
             "Fuente: BCRP, IPC de Lima Metropolitana, var. % a 12 meses, mensual, ene-2020 a dic-2024. "
             "Series PN01273PM (general), PN09822PM (alimentos y bebidas), PN01279PM (subyacente).",
             fontsize=8, color="#444444", wrap=True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    FIGURA.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURA, dpi=200)
    plt.close(fig)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows usa cp1252
    ancho = cargar()
    ind = indicadores(ancho)
    grafico(ancho, ind)
    print(ind.to_string(index=False))
    print(f"\nGuardado: {FIGURA.relative_to(RAIZ)}, {INDICADORES.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
