"""Participación del gasto en alimentos en el gasto total del hogar, ENAHO 2024 (sumaria).

    uv run scripts/gasto_alimentos.py

Lee los .dta directamente del zip datos/966-Modulo34.zip (no se extrae nada) y escribe
salidas/gasto_alimentos_2024.csv.

Denominador: gashog2d (gasto total bruto, el gasto de la medición oficial de pobreza).
Ponderación: factor07 × mieperho (personas), igual que el método oficial de la sumaria.

Definiciones de alimentos (columna `definicion`):
  inei      PRINCIPAL. Alimentos según el do-file oficial del INEI (ConstVarGasto, sumaria-2024.dta), 26
            variables: grupo 1 alimentos (gru11hd, gru12hd1/2, gru13hd1..3), alimentos fuera del hogar (g05hd*,
            ig06hd), instituciones benéficas (sg23, sig24) y otros (gru14hd*, sg25..sig28). Con las partidas de
            los demás grupos (que incluyen sg42*, g07hd, ig08hd) suma exactamente gashog2d.
  sensibilidad_12g  Definición inicial de la estudiante, con sumaria-2024-12g.dta: grupo 1 (alimentos dentro
            del hogar, 6 formas: gru11hd..gru16hd), grupo 11 alimentos fuera del hogar (gru111hd..gru116hd) y
            alimentos preparados ambulantes (gru111hd2..gru116hd2). Omite g05hd*, ig06hd y sg23..sig28, por lo
            que subestima el gasto en alimentos; se conserva como sensibilidad.

Cifra principal: cociente de totales ponderados, sum(alim·w) / sum(gashog2d·w).
Complemento: promedio ponderado de la participación de cada hogar, sum(w·alim/gasto) / sum(w).
Las diferencias entre grupos (pobre − no pobre, rural − urbano) se calculan aquí, con valores sin redondear,
y se guardan en el CSV con nivel `diferencia_pp`.
"""
from __future__ import annotations

import sys
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ZIP = RAIZ / "datos" / "966-Modulo34.zip"
SALIDA = RAIZ / "salidas" / "gasto_alimentos_2024.csv"
LLAVES = ["conglome", "vivienda", "hogar"]

VALIDADA = (
    [f"gru1{i}hd" for i in range(1, 7)]
    + [f"gru11{i}hd" for i in range(1, 7)]
    + [f"gru11{i}hd2" for i in range(1, 7)]
)
INEI_ALIMENTOS = (
    ["gru11hd", "gru12hd1", "gru12hd2", "gru13hd1", "gru13hd2", "gru13hd3"]
    + ["g05hd", "g05hd1", "g05hd2", "g05hd3", "g05hd4", "g05hd5", "g05hd6", "ig06hd"]
    + ["sg23", "sig24"]
    + ["gru14hd", "gru14hd1", "gru14hd2", "gru14hd3", "gru14hd4", "gru14hd5", "sg25", "sig26", "sg27", "sig28"]
)
# Resto de partidas del do-file del INEI (grupos 2 a 8); solo para comprobar que todo suma gashog2d.
INEI_RESTO = [
    "gru21hd", "gru22hd1", "gru22hd2", "gru23hd1", "gru23hd2", "gru23hd3", "gru24hd",
    "gru31hd", "gru32hd1", "gru32hd2", "gru33hd1", "gru33hd2", "gru33hd3", "gru34hd",
    "gru41hd", "gru42hd1", "gru42hd2", "gru43hd1", "gru43hd2", "gru43hd3", "gru44hd", "sg421", "sg42d1", "sg423", "sg42d3",
    "gru51hd", "gru52hd1", "gru53hd1", "gru53hd2", "gru53hd3", "gru54hd",
    "gru61hd", "gru62hd1", "gru62hd2", "gru63hd1", "gru63hd2", "gru63hd3", "gru64hd", "g07hd", "ig08hd", "sg422", "sg42d2",
    "gru71hd", "gru72hd1", "gru72hd2", "gru73hd1", "gru73hd2", "gru73hd3", "gru74hd", "sg42", "sg42d",
    "gru81hd", "gru82hd1", "gru82hd2", "gru83hd1", "gru83hd2", "gru83hd3", "gru84hd",
]  # gru52hd2 no existe en el archivo 2024 (se omite)


def leer(miembro: str) -> pd.DataFrame:
    with zipfile.ZipFile(ZIP) as z:
        with z.open(f"966-Modulo34/{miembro}") as f:
            df = pd.read_stata(BytesIO(f.read()), convert_categoricals=False)
    df.columns = [c.lower() for c in df.columns]
    for k in LLAVES:
        df[k] = df[k].astype(str)
    return df


def suma(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    faltan = [c for c in cols if c not in df]
    if faltan:
        raise SystemExit(f"Faltan variables en la sumaria: {faltan}")
    return df[cols].fillna(0).sum(axis=1)


def cargar() -> pd.DataFrame:
    s8 = leer("sumaria-2024.dta")
    s12 = leer("sumaria-2024-12g.dta")
    if s8[LLAVES].duplicated().any() or s12[LLAVES].duplicated().any():
        raise SystemExit("Hogares duplicados en la sumaria.")
    df = s12[LLAVES + ["gashog2d", "factor07", "mieperho", "pobreza", "estrato"]].copy()
    df["alim_validada"] = suma(s12, VALIDADA).to_numpy()
    s8 = s8.assign(alim_inei=suma(s8, INEI_ALIMENTOS), resto_inei=suma(s8, INEI_RESTO))
    df = df.merge(s8[LLAVES + ["gashog2d", "alim_inei", "resto_inei"]], on=LLAVES, how="inner",
                  suffixes=("", "_8g"), validate="1:1")
    # Validaciones
    assert len(df) == len(s12) == 33691, f"Se esperaban 33,691 hogares y hay {len(df)}"
    assert (df.gashog2d - df.gashog2d_8g).abs().max() < 0.05, "gashog2d difiere entre sumaria-2024 y 12g"
    cuadre = (df.alim_inei + df.resto_inei - df.gashog2d).abs().max()
    assert cuadre < 0.05, f"El do-file del INEI no reconstruye gashog2d (dif. máx. {cuadre:.3f})"
    assert df[["gashog2d", "factor07", "mieperho"]].notna().all().all() and (df.gashog2d > 0).all()
    assert (df.alim_validada <= df.gashog2d + 1e-6).all() and (df.alim_inei <= df.gashog2d + 1e-6).all()
    # El numerador del INEI no debe contener partidas de otros grupos (equipamiento, otros gastos).
    assert not set(INEI_ALIMENTOS) & set(INEI_RESTO)
    assert not [c for c in INEI_ALIMENTOS if c.startswith(("sg42", "g07", "ig08"))]
    df["w"] = df.factor07 * df.mieperho
    df["pobre"] = df.pobreza <= 2
    df["urbano"] = df.estrato <= 5
    print(f"Hogares: {len(df):,}. Reconstrucción INEI vs gashog2d: dif. máx. {cuadre:.3f} soles. "
          f"Personas expandidas: {df.w.sum():,.0f}")
    return df


def filas(df: pd.DataFrame) -> pd.DataFrame:
    cortes = {
        ("total", "todos hogares"): df.index == df.index,
        ("pobreza", "pobre"): df.pobre,
        ("pobreza", "no pobre"): ~df.pobre,
        ("area", "urbano"): df.urbano,
        ("area", "rural"): ~df.urbano,
        ("pobreza_area", "pobre urbano"): df.pobre & df.urbano,
        ("pobreza_area", "no pobre urbano"): ~df.pobre & df.urbano,
        ("pobreza_area", "pobre rural"): df.pobre & ~df.urbano,
        ("pobreza_area", "no pobre rural"): ~df.pobre & ~df.urbano,
    }
    out = []
    for definicion, col in (("inei", "alim_inei"), ("sensibilidad_12g", "alim_validada")):
        alim = df[col]
        exacto = {}  # valores sin redondear, para las diferencias
        for (nivel, grupo), m in cortes.items():
            d, a = df[m], alim[m]
            w = d.w
            cociente = 100 * (a * w).sum() / (d.gashog2d * w).sum()
            promedio = 100 * np.average(a / d.gashog2d, weights=w)
            exacto[grupo] = (cociente, promedio)
            out.append({
                "definicion": definicion, "nivel": nivel, "grupo": grupo, "unidad": "% del gasto total",
                "n_hogares": len(d),
                "hogares_participacion_cero": int((a == 0).sum()),
                "pct_cociente_totales": round(cociente, 2),
                "pct_promedio_hogares": round(promedio, 2),
            })
        for grupo, (x, y) in {"pobre − no pobre": ("pobre", "no pobre"),
                              "rural − urbano": ("rural", "urbano")}.items():
            out.append({
                "definicion": definicion, "nivel": "diferencia_pp", "grupo": grupo, "unidad": "pp",
                "n_hogares": "", "hogares_participacion_cero": "",
                "pct_cociente_totales": round(exacto[x][0] - exacto[y][0], 2),
                "pct_promedio_hogares": round(exacto[x][1] - exacto[y][1], 2),
            })
    return pd.DataFrame(out)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    df = cargar()
    t = filas(df)
    SALIDA.parent.mkdir(exist_ok=True)
    t.to_csv(SALIDA, index=False, encoding="utf-8")
    for nombre, col in (("INEI (principal)", "alim_inei"), ("sensibilidad 12g", "alim_validada")):
        cero = df[col] == 0
        print(f"Hogares con participación 0 % ({nombre}): {int(cero.sum())} "
              f"({100 * cero.mean():.2f} % de hogares; {100 * df.w[cero].sum() / df.w.sum():.2f} % de personas); "
              f"pobres: {int((cero & df.pobre).sum())}")
    cero12 = df.alim_validada == 0
    print(f"  de los {int(cero12.sum())} de la sensibilidad 12g, con alimentos > 0 según el INEI: "
          f"{int(((df.alim_inei > 0) & cero12).sum())}")
    print(f"Gasto anual en alimentos por hogar (promedio sin ponderar, soles): INEI "
          f"{df.alim_inei.mean():,.0f}; sensibilidad 12g {df.alim_validada.mean():,.0f}; "
          f"gasto total {df.gashog2d.mean():,.0f}")
    print(t.to_string(index=False))
    print(f"\nGuardado: {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
