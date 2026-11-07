"""Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO y valida el resultado.

Salidas (en --salidas):
    personas_AAAA.parquet  base de personas residentes habituales con pobreza y factores
    validacion.txt         verificaciones aprobadas y fallidas
    indicadores.csv        pobreza ponderada: nacional, área, sexo y departamento

Si falla una validación esencial el script escribe validacion.txt, no guarda el
parquet y termina con código 1. No se corrige nada para que coincida con la referencia.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]

# Referencias del ENUNCIADO y de la sesión 16 (solo para validar, nunca se usan como resultado).
REF_NACIONAL = 27.6
REF_URBANO, REF_RURAL = 24.8, 39.3
REF_EXTREMA = 5.5
REF_LIMA_METRO = 28.2  # dominio == 8
REF_RESIDENTES = 108_664
TOL_ESENCIAL = 0.1  # pp, solo la pobreza nacional
TOL_INFORMATIVA = 0.2  # pp, resto de referencias redondeadas a 1 decimal

DEPARTAMENTOS = {
    "01": "AMAZONAS", "02": "ANCASH", "03": "APURIMAC", "04": "AREQUIPA", "05": "AYACUCHO",
    "06": "CAJAMARCA", "07": "CALLAO", "08": "CUSCO", "09": "HUANCAVELICA", "10": "HUANUCO",
    "11": "ICA", "12": "JUNIN", "13": "LA LIBERTAD", "14": "LAMBAYEQUE", "15": "LIMA",
    "16": "LORETO", "17": "MADRE DE DIOS", "18": "MOQUEGUA", "19": "PASCO", "20": "PIURA",
    "21": "PUNO", "22": "SAN MARTIN", "23": "TACNA", "24": "TUMBES", "25": "UCAYALI",
}


def tasa_ponderada(indicador: pd.Series, peso: pd.Series) -> float:
    """Porcentaje ponderado. Único punto de cálculo: nada de promedios simples."""
    return float(np.average(indicador.astype(float), weights=peso.astype(float)) * 100)


class Validacion:
    def __init__(self) -> None:
        self.filas: list[tuple[bool, bool, str, str]] = []
        self.notas: list[str] = []

    def chequeo(self, ok: bool, nombre: str, detalle: str, esencial: bool = True) -> bool:
        self.filas.append((bool(ok), esencial, nombre, detalle))
        return bool(ok)

    def esenciales_fallidas(self) -> list[str]:
        return [n for ok, es, n, _ in self.filas if es and not ok]

    def texto(self, anio: int) -> str:
        out = [f"VALIDACIÓN ENAHO {anio} — limpiando-enaho", "=" * 60, ""]
        for ok, es, nombre, detalle in self.filas:
            marca = "APROBADO" if ok else "FALLIDO "
            tipo = "esencial" if es else "informativa"
            out.append(f"[{marca}] ({tipo}) {nombre}")
            out.append(f"           {detalle}")
        out.append("")
        out += self.notas
        fallidas = self.esenciales_fallidas()
        out += ["", "=" * 60]
        out.append(
            "RESULTADO: APROBADO (todas las validaciones esenciales pasaron)"
            if not fallidas
            else "RESULTADO: FALLIDO — validaciones esenciales fallidas: " + "; ".join(fallidas)
        )
        return "\n".join(out) + "\n"


def extraer_dta(zip_path: Path, nombre_dta: str, destino: Path) -> Path:
    """Extrae solo el .dta pedido; los zip traen además PDFs, diccionarios y otros .dta."""
    with zipfile.ZipFile(zip_path) as z:
        miembros = [m for m in z.namelist() if Path(m).name.lower() == nombre_dta.lower()]
        if len(miembros) != 1:
            raise SystemExit(f"ERROR: se esperaba exactamente un '{nombre_dta}' en {zip_path.name}, hay {len(miembros)}.")
        return Path(z.extract(miembros[0], destino))


def leer_stata(ruta: Path) -> pd.DataFrame:
    df = pd.read_stata(ruta, convert_categoricals=False)
    df.columns = [c.lower() for c in df.columns]  # 'aÑo' -> 'año'
    return df


def buscar_zip(carpeta: Path, modulo: str) -> Path:
    candidatos = sorted(carpeta.glob(f"*Modulo{modulo}*.zip"))
    if not candidatos:
        raise SystemExit(
            f"ERROR: no hay un zip del módulo {modulo} en {carpeta}/. "
            "Descárgalo del portal del INEI (código 966 = ENAHO 2024) y colócalo ahí."
        )
    return candidatos[0]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--datos", type=Path, default=Path("datos"))
    ap.add_argument("--salidas", type=Path, default=Path("salidas"))
    ap.add_argument("--referencias", type=Path, default=Path("referencias"))
    args = ap.parse_args()
    anio = args.anio
    args.salidas.mkdir(parents=True, exist_ok=True)
    v = Validacion()

    # 1. Leer ---------------------------------------------------------------
    zip34, zip02 = buscar_zip(args.datos, "34"), buscar_zip(args.datos, "02")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sumaria = leer_stata(extraer_dta(zip34, f"sumaria-{anio}.dta", tmp))
        personas = leer_stata(extraer_dta(zip02, f"enaho01-{anio}-200.dta", tmp))

    # 2. Normalizar: columnas ---------------------------------------------------
    v.chequeo(
        all(c == c.lower() for c in personas.columns) and all(c == c.lower() for c in sumaria.columns),
        "Columnas en minúscula",
        f"personas {personas.shape}, sumaria {sumaria.shape}; columna del año: 'año' presente = {'año' in personas.columns}",
    )
    requeridas_p = set(LLAVES_PERSONA) | {"año", "ubigeo", "dominio", "estrato", "p204", "p205", "p206", "p207", "facpob07"}
    requeridas_s = set(LLAVES_HOGAR) | {"pobreza", "mieperho", "factor07", "estrato", "ubigeo"}
    faltan = sorted((requeridas_p - set(personas.columns)) | (requeridas_s - set(sumaria.columns)))
    if not v.chequeo(not faltan, "Variables requeridas presentes", f"faltan: {faltan}" if faltan else "todas presentes"):
        return cerrar(v, args, anio, None)

    # Llaves como texto (ceros iniciales)
    tipos_ok = all(pd.api.types.is_string_dtype(df[k]) or df[k].dtype == object
                   for df in (personas, sumaria) for k in LLAVES_HOGAR)
    ceros = int(personas["conglome"].astype(str).str.startswith("0").sum()) if tipos_ok else 0
    largos = {k: sorted(personas[k].astype(str).str.len().unique().tolist()) for k in LLAVES_HOGAR}
    v.chequeo(
        tipos_ok and ceros > 0,
        "Llaves conglome/vivienda/hogar como texto, sin perder ceros iniciales",
        f"conglome con cero inicial en {ceros:,} filas; longitudes {largos}",
    )
    if not tipos_ok:
        return cerrar(v, args, anio, None)
    v.chequeo((pd.to_numeric(personas["año"]) == anio).all() and (pd.to_numeric(sumaria["año"]) == anio).all(),
              f"Año de la encuesta = {anio}", "personas y sumaria")

    # 3. Filtrar residentes habituales ------------------------------------------
    n_total = len(personas)
    res = ((personas.p204 == 1) & (personas.p205 == 2)) | ((personas.p204 == 2) & (personas.p206 == 1))
    personas = personas[res].copy()
    v.chequeo(len(personas) == REF_RESIDENTES, "Residentes habituales",
              f"{len(personas):,} de {n_total:,} filas del módulo 02 (referencia {REF_RESIDENTES:,})")
    dup_p = int(personas.duplicated(LLAVES_PERSONA).sum())
    v.chequeo(dup_p == 0, "Sin duplicados de persona (conglome, vivienda, hogar, codperso)", f"duplicados: {dup_p}")

    # 4. Unir personas–hogares --------------------------------------------------
    dup_s = int(sumaria.duplicated(LLAVES_HOGAR).sum())
    v.chequeo(dup_s == 0, "Llaves únicas en la sumaria", f"{len(sumaria):,} hogares, duplicados: {dup_s}")
    n_antes = len(personas)
    try:
        base = personas.merge(
            sumaria[LLAVES_HOGAR + ["pobreza", "mieperho", "factor07"]],
            on=LLAVES_HOGAR, how="left", validate="m:1",
        )
    except pd.errors.MergeError as e:
        v.chequeo(False, "Merge personas–hogares validate='m:1'", str(e))
        return cerrar(v, args, anio, None)
    sin_match = int(base["pobreza"].isna().sum())
    v.chequeo(len(base) == n_antes and sin_match == 0,
              "Merge m:1 sin pérdida ni duplicación de filas",
              f"filas antes {n_antes:,}, después {len(base):,}, sin hogar en la sumaria: {sin_match}")
    cmp = personas[LLAVES_HOGAR + ["estrato", "ubigeo"]].merge(
        sumaria[LLAVES_HOGAR + ["estrato", "ubigeo"]], on=LLAVES_HOGAR, suffixes=("", "_s"), validate="m:1")
    coincide = float(((cmp.estrato == cmp.estrato_s) & (cmp.ubigeo == cmp.ubigeo_s)).mean() * 100)
    v.chequeo(coincide > 99.9, "estrato y ubigeo de personas coinciden con la sumaria",
              f"{coincide:.2f} % de coincidencia", esencial=False)

    # 5. Construir variables ----------------------------------------------------
    base["departamento"] = base["ubigeo"].str[:2]
    base["urbano"] = base["estrato"] <= 5
    base["pobre"] = base["pobreza"] <= 2
    base["pobre_extremo"] = base["pobreza"] == 1
    sumaria["pobre"] = sumaria["pobreza"] <= 2
    sumaria["pobre_extremo"] = sumaria["pobreza"] == 1
    sumaria["urbano"] = sumaria["estrato"] <= 5

    deptos = sorted(base["departamento"].unique())
    v.chequeo(deptos == sorted(DEPARTAMENTOS), "25 códigos departamentales, Lima (15) y Callao (07) separados",
              f"{len(deptos)} códigos: {deptos[0]}…{deptos[-1]}; 07 y 15 presentes: {'07' in deptos and '15' in deptos}")
    v.chequeo(base["estrato"].notna().all() and set(base["pobreza"].unique()) <= {1, 2, 3} and base["p207"].isin([1, 2]).all(),
              "estrato sin nulos, pobreza en {1,2,3}, p207 en {1,2}",
              f"pobreza: {sorted(base['pobreza'].unique().tolist())}; estrato nulos: {int(base['estrato'].isna().sum())}")

    # 6. Ponderación ------------------------------------------------------------
    w = base["facpob07"]
    v.chequeo(w.notna().all() and (w > 0).all(), "facpob07 sin nulos y positivo",
              f"nulos {int(w.isna().sum())}, ceros o negativos {int((w <= 0).sum())}; población expandida {w.sum():,.0f}")
    nacional = tasa_ponderada(base["pobre"], w)
    simple = float(base["pobre"].mean() * 100)
    v.chequeo(abs(nacional - simple) > 0.5, "La ponderación se aplicó (ponderado ≠ promedio simple)",
              f"ponderado {nacional:.2f} % vs simple {simple:.2f} %", esencial=False)

    urb = base["urbano"]
    extrema = tasa_ponderada(base["pobre_extremo"], w)
    p_urb, p_rur = tasa_ponderada(base.loc[urb, "pobre"], w[urb]), tasa_ponderada(base.loc[~urb, "pobre"], w[~urb])
    lima = base["dominio"] == 8
    p_lima = tasa_ponderada(base.loc[lima, "pobre"], w[lima])

    # Método oficial INEI: sumaria con factor07 × mieperho
    ws = sumaria["factor07"] * sumaria["mieperho"]
    s_nac = tasa_ponderada(sumaria["pobre"], ws)
    su = sumaria["urbano"]
    s_urb, s_rur = tasa_ponderada(sumaria.loc[su, "pobre"], ws[su]), tasa_ponderada(sumaria.loc[~su, "pobre"], ws[~su])

    v.chequeo(abs(nacional - REF_NACIONAL) <= TOL_ESENCIAL, "Pobreza monetaria nacional (personas, facpob07)",
              f"{nacional:.2f} % vs referencia {REF_NACIONAL} % (tolerancia {TOL_ESENCIAL} pp)")
    v.chequeo(abs(s_nac - REF_NACIONAL) <= TOL_ESENCIAL, "Pobreza monetaria nacional (sumaria, factor07×mieperho)",
              f"{s_nac:.2f} % vs referencia {REF_NACIONAL} % (tolerancia {TOL_ESENCIAL} pp)", esencial=False)
    for nombre, val, ref in [("urbana", p_urb, REF_URBANO), ("rural", p_rur, REF_RURAL),
                             ("extrema nacional", extrema, REF_EXTREMA), ("Lima Metropolitana (dominio 8)", p_lima, REF_LIMA_METRO)]:
        v.chequeo(abs(val - ref) <= TOL_INFORMATIVA, f"Pobreza {nombre}",
                  f"{val:.2f} % vs referencia {ref} % (tolerancia {TOL_INFORMATIVA} pp)", esencial=False)

    v.notas += [
        "CONTRASTE DE MÉTODOS (pobreza monetaria, %)",
        f"  {'':10s}{'sumaria factor07×mieperho':>28s}{'personas facpob07':>20s}{'diferencia pp':>15s}",
    ]
    for nom, a, b in [("nacional", s_nac, nacional), ("urbano", s_urb, p_urb), ("rural", s_rur, p_rur)]:
        v.notas.append(f"  {nom:10s}{a:28.2f}{b:20.2f}{a - b:15.2f}")
    v.notas += [
        "  Difieren porque la sumaria cubre todos los hogares (33,691) con factor07×mieperho, mientras que",
        "  personas usa solo residentes habituales (108,664) con facpob07, un factor de persona distinto.",
        "",
    ]

    # Departamentos vs referencia de la sesión 16
    por_depto = (base.groupby("departamento")
                 .apply(lambda g: pd.Series({"pobreza_pct": tasa_ponderada(g["pobre"], g["facpob07"]), "n": len(g)}),
                        include_groups=False))
    ref_csv = args.referencias / "pobreza_departamento_2024.csv"
    if ref_csv.exists():
        ref = pd.read_csv(ref_csv, dtype={"ccdd": str}).set_index("ccdd")["pobreza_pct"]
        ref = ref.reindex(por_depto.index)
        sumaria["departamento"] = sumaria["ubigeo"].str[:2]
        s_depto = sumaria.groupby("departamento").apply(
            lambda g: tasa_ponderada(g["pobre"], ws.loc[g.index]), include_groups=False)
        dif_s, dif_p = (s_depto - ref).abs(), (por_depto["pobreza_pct"] - ref).abs()
        v.chequeo(dif_s.max() <= TOL_INFORMATIVA,
                  "Pobreza departamental (sumaria, factor07×mieperho) vs referencias/pobreza_departamento_2024.csv",
                  f"máxima diferencia {dif_s.max():.2f} pp en {dif_s.idxmax()} ({DEPARTAMENTOS[dif_s.idxmax()]}); "
                  f"{int((dif_s <= TOL_INFORMATIVA).sum())}/25 dentro de {TOL_INFORMATIVA} pp", esencial=False)
        v.notas += [
            "POBREZA DEPARTAMENTAL: la referencia de la sesión 16 se reproduce con el método de la sumaria.",
            f"  Con personas y facpob07 (indicadores.csv) la diferencia máxima es {dif_p.max():.2f} pp en "
            f"{dif_p.idxmax()} ({DEPARTAMENTOS[dif_p.idxmax()]}); {int((dif_p <= TOL_INFORMATIVA).sum())}/25 dentro de {TOL_INFORMATIVA} pp.",
            "  Es la misma diferencia de factores del contraste anterior, más marcada en muestras departamentales pequeñas.",
            "",
        ]
    else:
        v.notas.append(f"(sin {ref_csv}: no se comparó la pobreza departamental)")

    # 7. Indicadores y guardado --------------------------------------------------
    filas = [("nacional", "PE", "Perú", "pobreza", nacional, len(base)),
             ("nacional", "PE", "Perú", "pobreza_extrema", extrema, len(base)),
             ("area", "urbano", "Urbano", "pobreza", p_urb, int(urb.sum())),
             ("area", "rural", "Rural", "pobreza", p_rur, int((~urb).sum()))]
    for cod, nom in [(1, "Hombre"), (2, "Mujer")]:
        m = base["p207"] == cod
        filas.append(("sexo", str(cod), nom, "pobreza", tasa_ponderada(base.loc[m, "pobre"], w[m]), int(m.sum())))
    for cod in sorted(DEPARTAMENTOS):
        filas.append(("departamento", cod, DEPARTAMENTOS[cod], "pobreza", por_depto.loc[cod, "pobreza_pct"], int(por_depto.loc[cod, "n"])))
    indicadores = pd.DataFrame(filas, columns=["nivel", "codigo", "nombre", "indicador", "pct_ponderado", "n_personas_muestra"])
    indicadores["pct_ponderado"] = indicadores["pct_ponderado"].round(2)
    indicadores.to_csv(args.salidas / "indicadores.csv", index=False, encoding="utf-8")

    return cerrar(v, args, anio, base)


def cerrar(v: Validacion, args: argparse.Namespace, anio: int, base: pd.DataFrame | None) -> int:
    (args.salidas / "validacion.txt").write_text(v.texto(anio), encoding="utf-8")
    print(v.texto(anio))
    fallidas = v.esenciales_fallidas()
    if fallidas or base is None:
        print("ERROR: validación esencial fallida; no se guardó la base procesada.", file=sys.stderr)
        return 1
    destino = args.salidas / f"personas_{anio}.parquet"
    base.to_parquet(destino, index=False)
    print(f"Guardado: {destino} ({len(base):,} filas), {args.salidas / 'validacion.txt'}, {args.salidas / 'indicadores.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
