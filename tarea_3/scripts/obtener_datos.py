"""Paso 1 · Obtener los datos.

1. Rasters y shapefile del curso (Hugging Face, sesión 07-raster):
   luces nocturnas VIIRS 2021, áreas mineras (Maus et al. 2022),
   precipitación y límites distritales.
2. PBI por departamentos 2007-2023 (INEI, vía API del BCRP).

Uso:  python scripts/obtener_datos.py
"""
import json

import pandas as pd
import requests

from comun import CODIGOS_PBI, HF_ARCHIVOS, ORIGINALES, traer, traer_shapefile


def descargar_rasters() -> dict:
    rutas = {}
    for clave, ruta in HF_ARCHIVOS.items():
        print(f"  · {clave:9s} <- {ruta}")
        rutas[clave] = traer_shapefile(ruta) if clave == "distritos" else traer(ruta)
    # Guardamos dónde quedaron en el caché para que el resto de scripts los encuentre
    (ORIGINALES / "rutas_rasters.json").write_text(json.dumps(rutas, indent=2))
    return rutas


def descargar_pbi(desde: int = 2007, hasta: int = 2023) -> pd.DataFrame:
    filas = []
    for codigo, depto in CODIGOS_PBI.items():
        url = (f"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
               f"{codigo}/json/{desde}/{hasta}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        datos = json.loads(r.content.decode("utf-8-sig"))
        nombre = datos["config"]["series"][0]["name"]
        for p in datos["periods"]:
            valor = p["values"][0]
            filas.append({
                "codigo_bcrp": codigo,
                "departamento": depto,
                "nombre_serie": nombre,
                "anio": int(p["name"]),
                "pbi_millones_s2007": pd.to_numeric(valor, errors="coerce"),
            })
        print(f"  · {codigo}  {depto:14s} ({nombre[:60]})")
    df = pd.DataFrame(filas)
    df.to_csv(ORIGINALES / "pbi_departamental_bcrp.csv", index=False)
    return df


if __name__ == "__main__":
    print("1/2  Rasters y shapefile (Hugging Face; puede tardar la primera vez)")
    descargar_rasters()
    print("\n2/2  PBI departamental (API BCRP)")
    pbi = descargar_pbi()
    print(f"\nListo: {len(pbi)} filas de PBI · archivos en {ORIGINALES}")