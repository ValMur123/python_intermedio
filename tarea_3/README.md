# La luz de las minas: minería y actividad económica en el Perú

## 1. Definición del problema

**Tema:** minería y actividad económica en los distritos del Perú.

**Contexto:** el INEI publica el PBI solo a nivel departamental; no existe PBI por
distrito. La literatura usa la luminosidad nocturna satelital como aproximación de la
actividad económica (Henderson, Storeygard y Weil, 2012; para el Perú, Seminario y
Palomino, 2022). Esto permite estudiar territorios pequeños, como los distritos mineros.

**Pregunta de investigación:** ¿los distritos con actividad minera tienen más actividad
económica, medida con luces nocturnas satelitales, que los distritos sin minería?

**Cobertura:**
- Geográfica: todos los distritos del Perú (unidad de análisis: distrito).
- Temporal: año 2021 (luces nocturnas VIIRS). Para validar la luz como proxy, se compara
  con el PBI departamental del INEI del mismo año.

  ## 2. Datos y fuentes

| Dato | Fuente | Cobertura | Cómo se obtiene |
|---|---|---|---|
| Luces nocturnas (radiancia) | NASA/NOAA VIIRS, compuesto anual | Perú, 2021, ~1 km por píxel | Dataset del curso en Hugging Face (`aquiro1994/ds-python-up`) |
| Áreas mineras (km² intervenidos) | Maus et al. (2022), *Scientific Data* | Mundial, ~1 km por píxel | Dataset del curso |
| Precipitación | Dataset del curso (laboratorio 7) | Perú | Dataset del curso |
| Límites distritales | Shapefile del curso (sesión 07-raster) | Perú, todos los distritos | Dataset del curso |
| PBI por departamentos (millones de S/ de 2007) | INEI, publicado por el BCRP (series RD17000DA–RD17023DA) | 24 departamentos, 2007-2023 | API del BCRP |

**Fecha de descarga:** 29/10/2026.

Todos los datos se descargan con `python scripts/obtener_datos.py`. Los rasters no se
suben al repositorio por su tamaño; quedan en el caché local de Hugging Face. El PBI se
guarda en `datos/originales/pbi_departamental_bcrp.csv`.

## 3. Procesamiento

`scripts/procesar_datos.py` pasa de píxeles a una tabla con una fila por distrito
(*zonal statistics*, como en la sesión 07-raster):

- **Limpieza:** valores negativos de VIIRS (resta de fondo del sensor) recortados a 0;
  `nodata` declarado en cada raster; nombres normalizados (sin tildes, en mayúsculas).
- **Transformación:** área de cada distrito calculada en un CRS métrico (EPSG:24891);
  Callao sumado a Lima para coincidir con el PBI del INEI.
- **Indicadores:** luz total, luz por km², km² de área minera, distrito minero (sí/no),
  intensidad minera (pequeña <1 km², media 1-10 km², grande ≥10 km²) y % de la luz de
  cada departamento que proviene de distritos mineros.

Resultado: 1 873 distritos, de los cuales 129 tienen actividad minera detectada.