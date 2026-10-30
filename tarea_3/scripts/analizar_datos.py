"""Paso 4 · Analizar: indicadores, comparaciones y hallazgos.

Genera:
  datos/procesados/resumen.json   KPIs y resultados (dashboard y reel)
  web/data/distritos.csv          atributos por distrito (se une al GeoJSON por 'id')
  web/data/departamentos.csv      luz, minería y PBI por departamento
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from comun import ANIO, PROCESADOS, WEB_DATA

panel = pd.read_csv(PROCESADOS / "panel_distritos.csv")
dep = pd.read_csv(PROCESADOS / "panel_departamentos.csv")

# ------------------------------------------------ comparación simple
grupos = panel.groupby("es_minero")["luz_total"].agg(["median", "mean", "count"])
mediana_min, mediana_no = grupos.loc[1, "median"], grupos.loc[0, "median"]

# ------------------------------------------------ regresiones (sesión 07)
reg = panel.dropna(subset=["precip_mm"]).copy()
reg["log_area"] = np.log(reg["area_km2"])
modelos = {
    "simple": "log_luz ~ es_minero",
    "area": "log_luz ~ es_minero + log_area",
    "completo": "log_luz ~ es_minero + log_area + precip_mm + C(DEPARTAMEN)",
}
res_modelos = {}
for nombre, formula in modelos.items():
    m = smf.ols(formula, data=reg).fit(cov_type="HC1")
    res_modelos[nombre] = {
        "coef": m.params["es_minero"], "se": m.bse["es_minero"],
        "t": m.tvalues["es_minero"], "r2": m.rsquared, "n": int(m.nobs),
        "veces_mas_luz": float(np.exp(m.params["es_minero"])),
    }

# Robustez: ¿el resultado depende de cómo definimos "minero"?
umbrales = []
for u in [0, 1, 5, 10]:
    reg["minero_u"] = (reg["mina_km2"] > u).astype(int)
    m = smf.ols("log_luz ~ minero_u + log_area + precip_mm + C(DEPARTAMEN)",
                data=reg).fit(cov_type="HC1")
    umbrales.append({"umbral_km2": u, "n_mineros": int(reg["minero_u"].sum()),
                     "coef": m.params["minero_u"], "t": m.tvalues["minero_u"],
                     "veces_mas_luz": float(np.exp(m.params["minero_u"]))})

# ------------------------------------------------ departamentos
d = dep.dropna(subset=["pbi_millones_s2007"]).copy()
corr = np.corrcoef(np.log(d["luz_total"]), np.log(d["pbi_millones_s2007"]))[0, 1]
sin_lima = d[d.departamento != "LIMA"]
corr_sin_lima = np.corrcoef(np.log(sin_lima["luz_total"]),
                            np.log(sin_lima["pbi_millones_s2007"]))[0, 1]
dep_top = dep.sort_values("pct_luz_minera", ascending=False).iloc[0]

# ------------------------------------------------ resumen
top_minas = (panel.nlargest(10, "mina_km2")
             [["DISTRITO", "PROVINCIA", "DEPARTAMEN", "mina_km2", "luz_total"]]
             .round(2).to_dict("records"))

resumen = {
    "anio": ANIO,
    "n_distritos": int(len(panel)),
    "n_mineros": int(panel["es_minero"].sum()),
    "pct_mineros": float(100 * panel["es_minero"].mean()),
    "area_minera_km2": float(panel["mina_km2"].sum()),
    "mediana_luz_minero": float(mediana_min),
    "mediana_luz_no_minero": float(mediana_no),
    "ratio_medianas": float(mediana_min / mediana_no) if mediana_no > 0 else None,
    "luz_media_km2_minero": float(panel.loc[panel.es_minero == 1, "luz_media"].mean()),
    "luz_media_km2_no_minero": float(panel.loc[panel.es_minero == 0, "luz_media"].mean()),
    "area_mediana_minero": float(panel.loc[panel.es_minero == 1, "area_km2"].median()),
    "area_mediana_no_minero": float(panel.loc[panel.es_minero == 0, "area_km2"].median()),
    "modelos": res_modelos,
    "robustez_umbral": umbrales,
    "corr_luz_pbi_dep": float(corr),
    "corr_luz_pbi_dep_sin_lima": float(corr_sin_lima),
    "dep_mayor_pct_luz_minera": {"departamento": dep_top["departamento"],
                                 "pct": float(dep_top["pct_luz_minera"])},
    "top_distritos_mineros": top_minas,
}
(PROCESADOS / "resumen.json").write_text(
    json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

# ------------------------------------------------ datos para la web
cols = ["id", "DEPARTAMEN", "PROVINCIA", "DISTRITO", "luz_total", "luz_media",
        "mina_km2", "area_km2", "precip_mm", "es_minero", "intensidad_minera"]
panel[cols].round(3).to_csv(WEB_DATA / "distritos.csv", index=False)
dep.round(3).to_csv(WEB_DATA / "departamentos.csv", index=False)
(WEB_DATA / "resumen.json").write_text(
    json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

# ------------------------------------------------ impresión
c = res_modelos["completo"]
print(f"""
HALLAZGOS ({ANIO})
1. {resumen['n_mineros']} de {resumen['n_distritos']} distritos ({resumen['pct_mineros']:.1f} %) tienen minería.
2. Luz total mediana: mineros {mediana_min:.1f} vs no mineros {mediana_no:.1f}.
   Controlando área, lluvia y departamento: {c['veces_mas_luz']:.1f} veces más luz
   (coef = {c['coef']:.2f}, t = {c['t']:.1f}, N = {c['n']}).
3. Luz por km²: mineros {resumen['luz_media_km2_minero']:.2f} vs no mineros {resumen['luz_media_km2_no_minero']:.2f}.
   Área mediana: mineros {resumen['area_mediana_minero']:.0f} km² vs {resumen['area_mediana_no_minero']:.0f} km².
4. Correlación luz–PBI departamental (logs): {corr:.2f}  (sin Lima: {corr_sin_lima:.2f}).
5. Donde más pesa la luz minera: {dep_top['departamento']} ({dep_top['pct_luz_minera']:.1f} %).

Robustez por umbral de área minera:""")
for u in umbrales:
    print(f"   > {u['umbral_km2']:>2} km²: {u['n_mineros']:>4} distritos · "
          f"{u['veces_mas_luz']:.2f} veces · t = {u['t']:.1f}")
print("\nTop distritos por área minera:")
print(pd.DataFrame(top_minas).to_string(index=False))