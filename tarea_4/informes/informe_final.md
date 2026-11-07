# Inflación en Lima (2020-2024) y pobreza monetaria al cierre del periodo

## 1. Pregunta de investigación

**¿Cómo evolucionó la inflación en Lima entre 2020 y 2024, en particular la de alimentos, y qué diferencias urbanas, rurales y departamentales presentaba la pobreza monetaria al cierre de ese periodo?**

- **Objetivo:** describir el ciclo inflacionario de Lima Metropolitana (BCRP) y, por separado, la pobreza monetaria de 2024 por área y departamento (ENAHO).
- **Delimitación:** la inflación cubre 2020-01 a 2024-12; la pobreza cubre solo 2024. El informe describe y no establece causalidad entre ambas fuentes.

## 2. Fuentes y metodología

| Fuente | Datos | Procesamiento |
|---|---|---|
| BCRP, servidor MCP `bcrp` | PN01273PM (IPC), PN09822PM (alimentos y bebidas), PN01279PM (subyacente); IPC de Lima Metropolitana, var. % a 12 meses, mensual | `buscar_series` para confirmar códigos, `serie` para los datos (descargados con `scripts/descargar_bcrp.py`, que llama a esa herramienta en memoria con `fastmcp.Client` y escribe `salidas/bcrp_inflacion_2020_2024.csv`), `resumen` y `comparar_periodos` como contraste. `scripts/grafico_bcrp.py` lee solo ese CSV y calcula todos los indicadores (`salidas/indicadores_bcrp.csv`), incluida la brecha alimentos − subyacente. |
| INEI, ENAHO 2024 (módulos 34 y 02) | Residentes habituales, n = 108,664 | Skill `limpiando-enaho` (validación en `salidas/validacion.txt`), `graficando-enaho` (barras) y `mapeando-enaho` (mapa). Porcentajes de personas ponderados con `facpob07`. |

Indicadores: promedio, máximo y mínimo de cada serie, promedio por tramo (2020-2021, 2022-2023, 2024), brecha alimentos − subyacente (pp), pobreza monetaria (% de personas) por área y departamento.

Validación ENAHO (todas las esenciales aprobadas): 108,664 residentes habituales, 25 códigos departamentales, merge m:1 sin duplicados, pobreza nacional 27.53 % (referencia 27.6 %, tolerancia 0.1 pp).

## 3. Resultados

**Hallazgo 1. La inflación de alimentos fue la más alta del ciclo 2022-2023.** El IPC general de Lima alcanzó su máximo en junio de 2022 (8.81 %), mientras que alimentos y bebidas llegó a 13.16 % en febrero de 2023 (PN09822PM). En 2022-2023 el promedio fue 10.42 % en alimentos, 7.09 % en el IPC general y 5.74 % en la subyacente; la brecha alimentos − subyacente promedió 4.67 pp, con un máximo de 6.76 pp en abril de 2022.

**Hallazgo 2. En 2024 la inflación se normalizó y la de alimentos terminó por debajo de la subyacente.** El promedio de 2024 fue 2.35 % en el IPC general, 2.01 % en alimentos y 3.27 % en la subyacente. En diciembre de 2024 las tasas fueron 1.97 %, 1.25 % y 2.57 %, y la brecha alimentos − subyacente fue −1.33 pp. La inflación de alimentos estuvo por debajo del 1 % en mayo, agosto y septiembre de 2024 (mínimo 0.69 % en septiembre). El IPC general estuvo sobre el 3 % en 34 de los 60 meses del periodo.

**Hallazgo 3. En 2024 la pobreza rural superó a la urbana en 14.7 pp y los departamentos se dispersan entre 5.9 % y 45.0 %.** La pobreza rural fue 39.44 % y la urbana 24.74 % (nacional 27.53 %). Por departamento, Ica tuvo el valor más bajo (5.91 %) y Cajamarca el más alto (44.99 %); 10 de los 25 departamentos superaron el total nacional. Entre los más altos están Loreto (42.61 %), Puno (40.42 %), Huánuco (39.47 %) y Pasco (39.28 %).

**Dato complementario sobre Lima.** Con la ENAHO, la pobreza de Lima Metropolitana (dominio 8) fue 28.03 %; el departamento de Lima registró 26.89 % y el Callao 33.77 % (estimaciones de personas con `facpob07`).

## 4. Visualizaciones

- BCRP: `figuras/inflacion_lima_2020_2024.png`
- ENAHO, urbano vs rural: `figuras/pobreza_urbano_rural_2024.png` (también `pobreza_sexo_2024.png` y `pobreza_departamento_2024.png`)
- Mapa departamental (25 unidades, Lima y Callao separados): `mapas/pobreza_departamento_2024.png`

![Inflación de Lima 2020-2024](../figuras/inflacion_lima_2020_2024.png)
![Pobreza urbana y rural 2024](../figuras/pobreza_urbano_rural_2024.png)
![Mapa de pobreza por departamento 2024](../mapas/pobreza_departamento_2024.png)

## 5. Interpretación

- El ciclo 2021-2023 fue una subida generalizada de precios, pero más intensa en alimentos que en el resto de la canasta: la brecha con la subyacente se ensanchó de 1.20 pp (promedio 2020-2021) a 4.67 pp (2022-2023). Hacia 2024 la brecha se invirtió (−1.25 pp en promedio).
- Que los alimentos subieran más que el resto es relevante para el bienestar de los hogares de menores ingresos, pero **este informe no lo demuestra**: la ENAHO usada aquí es de un solo año y no mide el gasto en alimentos por hogar. Es una hipótesis para una investigación posterior.
- La pobreza de 2024 se concentra fuera de las áreas urbanas: la brecha rural − urbana (14.7 pp) y la dispersión departamental (5.9 % a 45.0 %) muestran que el promedio nacional (27.5 %) oculta situaciones muy distintas.

## 6. Limitaciones

- **Distinta cobertura geográfica:** la inflación del BCRP es de Lima Metropolitana; la pobreza de la ENAHO es nacional, urbana/rural y departamental. No se debe inferir que la inflación de Lima explique la pobreza de otros departamentos.
- **Distinta cobertura temporal:** la ENAHO procesada es solo 2024, así que no hay trayectoria de la pobreza 2020-2024 que contrastar con la inflación. Solo se compara un punto de pobreza con una serie de inflación.
- **Sin causalidad:** todas las diferencias son descriptivas.
- **Ranking departamental no estricto:** el INEI publica la pobreza departamental en grupos con niveles estadísticamente similares, por el error de muestreo. Diferencias pequeñas entre departamentos (por ejemplo, Huánuco 39.5 % y Pasco 39.3 %) no deben leerse como un ranking estricto.
- **Método de ponderación:** las cifras usan `facpob07` sobre residentes habituales. La referencia de la sesión 16 usa la sumaria (`factor07 × mieperho`); las diferencias llegan a 0.52 pp en Puno (16 de 25 departamentos dentro de 0.2 pp). Ver `salidas/validacion.txt`.
- **Alcance del gráfico del BCRP:** muestra tasas a 12 meses. Un valor bajo en 2024 no implica que los precios hayan bajado, solo que subieron menos que un año antes.

## 7. Reproducibilidad

| Elemento | Archivo |
|---|---|
| Series BCRP (salida de la herramienta `serie`) | `scripts/descargar_bcrp.py` → `salidas/bcrp_inflacion_2020_2024.csv` |
| Gráfico e indicadores BCRP | `scripts/grafico_bcrp.py` → `figuras/inflacion_lima_2020_2024.png`, `salidas/indicadores_bcrp.csv` |
| Limpieza ENAHO | `.claude/skills/limpiando-enaho/scripts/limpiar.py` → `salidas/personas_2024.parquet`, `salidas/validacion.txt`, `salidas/indicadores.csv` |
| Gráficos ENAHO | `.claude/skills/graficando-enaho/scripts/graficar.py` → `figuras/` |
| Mapa | `.claude/skills/mapeando-enaho/scripts/mapear.py` → `mapas/`, `salidas/comparacion_mapa.csv` |
| Verificación manual | `informes/verificacion.md` |

Comandos (desde `tarea_4/`):

```bash
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run .claude/skills/graficando-enaho/scripts/graficar.py
uv run .claude/skills/mapeando-enaho/scripts/mapear.py
uv run scripts/descargar_bcrp.py
uv run scripts/grafico_bcrp.py
```

Series: PN01273PM, PN09822PM, PN01279PM (BCRP, API `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/<codigo>/json/2020-1/2024-12`).
