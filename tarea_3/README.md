# La luz de las minas: minería y actividad económica en el Perú

Tarea 3 · Python Intermedio · Diplomado PUCP 2026 · Alessandra Murga

🔗 **Dashboard público:** https://valmur123.github.io/python_intermedio/tarea_3/web/
🎬 **Reel:** [`reel/reel.mp4`](reel/reel.mp4)
💼 **Publicación de LinkedIn:** LINK_LINKEDIN

## 1. Tema y pregunta de investigación

**Tema:** minería y actividad económica en los distritos del Perú.

**Pregunta:** ¿los distritos con actividad minera tienen más actividad económica, medida con
luces nocturnas satelitales, que los distritos sin minería?

**Cobertura:** los 1 873 distritos del Perú, año 2021.

## 2. Descripción del proyecto

El INEI publica el PBI solo por departamento; no existe PBI por distrito. La literatura usa la
luminosidad nocturna satelital como aproximación de la actividad económica (Henderson, Storeygard
y Weil, 2012; para el Perú, Seminario y Palomino, 2022). Este proyecto mide la luz de cada
distrito con imágenes satelitales, la cruza con la superficie minera detectada por satélite y
compara distritos mineros y no mineros. Los resultados se presentan en un dashboard interactivo
y en un reel de divulgación.

## 3. Datos, fuentes y metodología

| Dato | Fuente | Cobertura | Cómo se obtiene |
|---|---|---|---|
| Luces nocturnas (radiancia) | NASA/NOAA VIIRS, compuesto anual | Perú, 2021, ~1 km por píxel | Dataset del curso en Hugging Face (`aquiro1994/ds-python-up`) |
| Áreas mineras (km² intervenidos) | Maus et al. (2022), *Scientific Data* | Mundial, ~1 km por píxel | Dataset del curso |
| Precipitación | Dataset del curso (laboratorio 7) | Perú | Dataset del curso |
| Límites distritales | Shapefile del curso (sesión 07-raster) | 1 873 distritos | Dataset del curso |
| PBI por departamentos (millones de S/ de 2007) | INEI, publicado por el BCRP (series RD17000DA–RD17023DA) | 24 departamentos, 2007-2023 | API del BCRP |

**Fecha de descarga:** 29/10/2026. Los rasters no se suben al repositorio por su tamaño; se
descargan con `scripts/obtener_datos.py`.

**Metodología:**

1. **Obtención** (`scripts/obtener_datos.py`): descarga los rasters del curso y el PBI departamental.
2. **Procesamiento** (`scripts/procesar_datos.py`): *zonal statistics* para pasar de píxeles a una
   fila por distrito (`all_touched=True`, `nodata` declarado, negativos de VIIRS recortados a 0);
   área calculada en un CRS métrico (EPSG:24891); nombres normalizados; Callao sumado a Lima para
   coincidir con el PBI del INEI. Indicadores: luz total, luz por km², km² de área minera, distrito
   minero (sí/no), intensidad minera (<1, 1-10, ≥10 km²) y % de la luz de cada departamento que
   viene de distritos mineros.
3. **Análisis** (`scripts/analizar_datos.py`): medianas por grupo y regresión del log de la luz
   total sobre ser minero, controlando log del área, precipitación y efectos fijos por
   departamento (errores robustos). Robustez con umbrales de 0, 1, 5 y 10 km² de área minera.
   Validación externa: correlación entre luz y PBI por departamento.

## 4. Tres hallazgos

1. **Los distritos mineros tienen más luz.** Luz total mediana: 29,1 (mineros) vs. 4,1 (no
   mineros). Comparando distritos de igual tamaño, lluvia y departamento, los mineros tienen
   3,6 veces más luz (coef. = 1,29; t = 7,6; N = 1 873).
2. **A mayor mina, mayor brecha, pero la luz se concentra en un punto.** Si se exige más de 1, 5
   o 10 km² de área minera, la diferencia sube a 7, 15 y 23 veces. Por km², en cambio, los
   distritos mineros brillan menos (0,32 vs. 1,54): son el doble de grandes (377 vs. 195 km² de
   mediana) y su luz se concentra en las operaciones.
3. **La luz satelital sigue al PBI oficial.** La correlación entre luz y PBI por departamento es
   0,93 (0,88 sin Lima). En Pasco, el 84 % de la luz proviene de distritos mineros (incluida la
   ciudad de Cerro de Pasco).

**Validación:** el ranking de área minera recupera las grandes operaciones del país: Antapaccay
(Espinar), Toquepala (Ilabaya), Cuajone (Torata), Cerro Verde (Yarabamba), Antamina (San Marcos),
Yanacocha (Cajamarca) y Las Bambas (Challhuahuacho).

## 5. Limitaciones

- La luz es una aproximación de la actividad económica, no el PBI: las minas iluminan sus
  instalaciones aunque eso no se traduzca en ingresos para la población local.
- Es una correlación, no un efecto causal: las minas se ubican donde hay mineral, y eso puede
  coincidir con vías, ciudades o altitud.
- Se usa 2021 porque es el último año con luces nacionales en el dataset del curso y con PBI
  departamental disponible para validar; el raster minero refleja minas de alrededor de 2019.
- Resolución de ~1 km: los distritos urbanos pequeños quedan representados por pocos píxeles.
  El raster minero mide superficie intervenida, no producción.

## 6. Dashboard

Construido con HTML, CSS y D3.js (`web/`). Incluye 4 KPIs, 6 visualizaciones (mapa distrital,
ranking, distribución por intensidad minera, luz vs. área, luz vs. PBI y peso minero por
departamento) y 4 controles: departamento, grupo de distritos, indicador y buscador de distritos,
además de descarga del CSV filtrado.

## 7. Reel

Video vertical 1080×1920 de 67 segundos, 7 escenas (`reel/guion.json`), con:

- Narración generada con **Qwen3-TTS** (Qwen3-TTS-12Hz-0.6B-Base) a partir de una grabación de mi
  propia voz de ~21 s. La grabación no se publica en el repositorio.
- Subtítulos sincronizados con **Whisper** large-v3-turbo (`reel/subtitulos.srt`); control de
  calidad con WER ≤ 0,05 en todas las escenas.
- Capturas del dashboard y gráficos propios (`reel/recursos/`, `reel/graficos_reel.py`).
- Música: *Cinematic Documentary*, de leberch (Pixabay, licencia de Pixabay). No se incluye el
  archivo en el repositorio.
- Aviso visible de voz generada con IA, fuente de los datos y créditos.

`reel/reel.py` proviene de la sesión 15 del curso; `reel/montaje.py` lo extiende con una imagen
por escena y música de fondo.

## 8. Cómo reproducir el proyecto

```
cd tarea_3
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/obtener_datos.py
python scripts/procesar_datos.py
python scripts/analizar_datos.py
```

Dashboard en local:

```
cd web
python -m http.server 8000
```

y abrir http://localhost:8000

Reel (entorno aparte, como en la sesión 15):

```
cd reel
python -m venv .venv-reel
.venv-reel\Scripts\python.exe -m pip install qwen-tts faster-whisper pillow imageio-ffmpeg soundfile jiwer num2words
.venv-reel\Scripts\python.exe montaje.py --voz recursos/mi_voz.wav --autor "Nombre Apellido" --credito-musica "Canción · Autor"
```

## 9. Uso de inteligencia artificial

Usé Claude (Anthropic) como asistente durante el proyecto: para elegir el enfoque,
escribir y depurar los scripts de Python, construir el dashboard, redactar el guion del reel y
preparar el montaje del video. La narración se generó con Qwen3-TTS a partir de mi voz y los
subtítulos con Whisper. Ejecuté todo el código en mi computadora y verifiqué los resultados: el
número de distritos mineros y el coeficiente coinciden con la sesión 07, el ranking minero
recupera las minas conocidas y las cifras del dashboard y del reel coinciden con la salida de
`analizar_datos.py`.

## Referencias

- Henderson, J. V., Storeygard, A. y Weil, D. N. (2012). Measuring Economic Growth from Outer Space. *American Economic Review*, 102(2).
- Maus, V. et al. (2022). An update on global mining land use. *Scientific Data*, 9.
- Seminario, B. y Palomino, L. (2022). *Estimación del PIB a nivel subnacional utilizando datos satelitales de luminosidad: Perú, 1993-2018*. Universidad del Pacífico.