"""Paso 3 · Procesar: de píxeles a una tabla por distrito.

Aplica zonal statistics (mismo método de la sesión 07-raster) y construye:
  datos/procesados/panel_distritos.csv      una fila por distrito
  datos/procesados/panel_departamentos.csv  luz agregada + PBI INEI 2021
  web/data/distritos.geojson                geometrías simplificadas para el mapa
"""
import json
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterstats import zonal_stats

from comun import ANIO, ORIGINALES, PROCESADOS, WEB_DATA, normalizar

warnings.filterwarnings("ignore")

# Umbrales de intensidad minera (km² de superficie intervenida en el distrito)
CORTES = [0, 1, 10, np.inf]
ETIQUETAS = ["Pequeña (<1 km²)", "Media (1-10 km²)", "Grande (≥10 km²)"]


def cargar_rutas() -> dict:
    archivo = ORIGINALES / "rutas_rasters.json"
    if not archivo.exists():
        raise SystemExit("Primero corre: python scripts/obtener_datos.py")
    return json.loads(archivo.read_text())


def panel_distrital(rutas: dict) -> gpd.GeoDataFrame:
    distritos = gpd.read_file(rutas["distritos"])
    print(f"  {len(distritos):,} distritos · columnas: {list(distritos.columns)}")

    with rasterio.open(rutas["luces"]) as src:
        assert distritos.crs.to_epsg() == src.crs.to_epsg(), "CRS distintos"
    with rasterio.open(rutas["minas"]) as src:
        nodata_minas = src.nodata
    with rasterio.open(rutas["precip"]) as src:
        nodata_precip = src.nodata

    print("  zonal stats · luces")
    luz = pd.DataFrame(zonal_stats(distritos, rutas["luces"],
                                   stats=["mean", "sum", "max", "count"],
                                   nodata=np.nan, all_touched=True))
    print("  zonal stats · minas")
    minas = pd.DataFrame(zonal_stats(distritos, rutas["minas"], stats=["sum"],
                                     nodata=nodata_minas, all_touched=True))
    print("  zonal stats · precipitación")
    prec = pd.DataFrame(zonal_stats(distritos, rutas["precip"], stats=["mean"],
                                    band=1, nodata=nodata_precip, all_touched=True))

    panel = distritos[["DEPARTAMEN", "PROVINCIA", "DISTRITO", "geometry"]].copy()
    panel.insert(0, "id", range(len(panel)))
    for col in ("DEPARTAMEN", "PROVINCIA", "DISTRITO"):
        panel[col] = panel[col].map(normalizar)

    # Los negativos de VIIRS son resta de fondo: se recortan a 0
    panel["luz_total"] = luz["sum"].clip(lower=0).values
    panel["luz_media"] = luz["mean"].clip(lower=0).values
    panel["luz_max"] = luz["max"].values
    panel["n_pixeles"] = luz["count"].values
    panel["mina_km2"] = minas["sum"].fillna(0).clip(lower=0).values
    panel["precip_mm"] = prec["mean"].values
    panel["area_km2"] = panel.to_crs(epsg=24891).geometry.area.values / 1e6

    panel["es_minero"] = (panel["mina_km2"] > 0).astype(int)
    panel["intensidad_minera"] = pd.cut(panel["mina_km2"], CORTES, labels=ETIQUETAS,
                                        right=False).astype(str)
    panel.loc[panel["es_minero"] == 0, "intensidad_minera"] = "Sin minería"
    panel["log_luz"] = np.log1p(panel["luz_total"])
    return panel


def panel_departamental(panel: gpd.GeoDataFrame) -> pd.DataFrame:
    pbi = pd.read_csv(ORIGINALES / "pbi_departamental_bcrp.csv")
    pbi = pbi[pbi["anio"] == ANIO][["departamento", "pbi_millones_s2007"]]

    tabla = panel.drop(columns="geometry").copy()
    # El PBI del INEI incluye al Callao dentro de Lima
    tabla["departamento"] = tabla["DEPARTAMEN"].replace({"CALLAO": "LIMA"})
    tabla["luz_minera"] = tabla["luz_total"] * tabla["es_minero"]

    dep = (tabla.groupby("departamento")
           .agg(n_distritos=("id", "size"),
                n_mineros=("es_minero", "sum"),
                mina_km2=("mina_km2", "sum"),
                luz_total=("luz_total", "sum"),
                luz_minera=("luz_minera", "sum"),
                area_km2=("area_km2", "sum"))
           .reset_index())
    dep["pct_luz_minera"] = 100 * dep["luz_minera"] / dep["luz_total"]
    dep = dep.merge(pbi, on="departamento", how="left")
    faltan = dep[dep["pbi_millones_s2007"].isna()]["departamento"].tolist()
    if faltan:
        print(f"  AVISO: sin PBI para {faltan} — revisar nombres")
    return dep


def exportar_geojson(panel: gpd.GeoDataFrame) -> None:
    web = panel[["id", "geometry"]].copy()
    web["geometry"] = web.geometry.simplify(0.004, preserve_topology=True)
    destino = WEB_DATA / "distritos.geojson"
    web.to_file(destino, driver="GeoJSON", layer_options={"COORDINATE_PRECISION": 4})
    print(f"  geojson: {destino.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    rutas = cargar_rutas()
    print("1/3  Panel distrital")
    panel = panel_distrital(rutas)
    panel.drop(columns="geometry").to_csv(PROCESADOS / "panel_distritos.csv", index=False)
    print(f"  {panel.es_minero.sum()} distritos con minería de {len(panel)}")

    print("2/3  Panel departamental + PBI")
    dep = panel_departamental(panel)
    dep.to_csv(PROCESADOS / "panel_departamentos.csv", index=False)

    print("3/3  GeoJSON para el dashboard")
    exportar_geojson(panel)
    print("\nListo.")