# 🗞️ Noticias peruanas: del titular al clasificador

> Tarea 1 · Python Intermedio · Diplomatura QLAB – PUCP
> Estudiante: **Valeria Murga** (@ValMur123)

## 1. Pregunta del proyecto
**¿Podemos convertir titulares peruanos en un clasificador de noticias?** Es decir, ¿un modelo pequeño, entrenado con
etiquetas generadas por un LLM, puede asignar un titular nuevo a *política*, *economía*, *deportes* o *ciencia y
tecnología* con buena precisión y en tiempo real?

**Respuesta corta:** sí. El modelo BETO ajustado alcanzó un **F1 macro de 0.88** en un test que nunca vio, frente a
**0.54** de un modelo sin entrenamiento (zero-shot), y clasifica un titular en ~0.06 s sin internet.

## 2. Medios y fechas de extracción
| Medio | Canal usado | Noticias finales | Periodo de publicación |
|---|---|---|---|
| El Comercio (`elcomercio.pe`) | RSS por sección + sitemap de noticias (`/sitemap/news/<sección>/`) | **382** | octubre de 2026 |
| La República (`larepublica.pe`) | RSS y sitemaps por sección + sitemap general de noticias (declarados en `robots.txt`) | **51** | octubre de 2026 |

- **Opción C – Comparada.** Fecha de descarga: **17/10/2026** (la hora UTC exacta se registra en el notebook).
- 431 de las 433 noticias son de octubre de 2026; 2 son anteriores (febrero y abril), porque los sitemaps también listan
  notas antiguas actualizadas.
- Se respetó `robots.txt`, con User-Agent identificado, pausa de 1.5 s y como máximo 1 reintento. Solo se usaron canales
  oficiales; el HTML de cada nota se visitó únicamente para completar bajadas faltantes.
- De **604 URLs únicas** se descartaron **171** (169 de secciones fuera de las 4 categorías y 2 titulares de menos de
  4 palabras) → **433 noticias** en `datos/noticias.csv`. El detalle está en `datos/raw/descartadas.csv`.

## 3. Metodología resumida
1. **Recolección y limpieza** (`01_recoleccion.ipynb`): RSS y sitemaps → `seccion_original` desde la URL → tabla de
   equivalencias a 4 categorías → limpieza con reporte de descartes → bajadas faltantes → EDA (3 gráficos Plotly)
   → validación de extremos → exportación.
2. **Clasificación** (`02_clasificacion.ipynb`): partición 70/15/15 estratificada (`random_state=42`, 303/65/65);
   zero-shot con `Recognai/bert-base-spanish-wwm-cased-xnli`; etiquetado débil con **Gemini** (`gemini-flash-latest`)
   y auditoría humana de 20 casos; *fine-tuning* con `Trainer` (3 épocas, batch 16, F1 macro) de **BETO** y
   **ModernBERT** (el modelo de la clase 2), eligiendo el mejor en validación y evaluándolo una sola vez en test.
3. **Dashboard** (`app.py`): filtros, indicadores, gráfico, tabla descargable, resultados del modelo y probador en vivo.

| Enfoque | F1 macro (test) | Latencia por titular | Requiere internet |
|---|---|---|---|
| Zero-shot (BERT español XNLI) | 0.54 | 0.49 s | No |
| LLM débil (Gemini) | 0.90 | 3.6 s* | Sí |
| **BETO fine-tuned (ganador)** | **0.88** | **0.06 s** | No |

\* Incluye pausas y reintentos por los límites de la cuota gratuita.

Comparación en validación: **BETO 0.954** vs ModernBERT 0.733. Acuerdo LLM–humano en la auditoría: **19/20**.

## 4. Hallazgos analíticos
1. **El idioma del modelo base importa más que su modernidad.** BETO (español) superó a ModernBERT (inglés) por más de
   20 puntos de F1 en validación. Con el mismo titular, BETO usa 13 tokens y ModernBERT 22, con las tildes partidas
   en bytes; en ModernBERT la pérdida de validación además sube mientras la de entrenamiento baja (memoriza sin generalizar).
2. **Economía es la categoría más difícil (F1 0.82) y política la más fácil (F1 0.94).** Economía atrae titulares con
   vocabulario de marcas, ventas o logística ("ASICS Golden Run: desvío vehicular", "Ventas de smartphones caen 20 %")
   y fenómenos con impacto económico ("El Niño alcanza niveles récord"). Varios de esos "errores" son etiquetas
   discutibles de la sección del diario.

## 5. Limitaciones técnicas
1. **Ruido en las etiquetas.** El modelo aprende de etiquetas del LLM (19/20 con la revisión humana) y se evalúa contra
   la sección del diario, que coincide con el LLM solo en el 93.5 %. Por eso el F1 baja de 0.95 (validación) a 0.88
   (test). Además, el test tiene solo 65 titulares: cada error mueve el F1 cerca de 1.5 puntos.
2. **Muestra pequeña, de pocos días y desbalanceada entre medios.** Son 433 titulares, casi todos de octubre de 2026, y
   La República aporta solo 51 (sus feeds exponen entre 9 y 20 notas por sección). El modelo refleja sobre todo el
   estilo de El Comercio y puede depender de temas coyunturales.

## 6. Cómo ejecutar en local
```bash
git clone https://github.com/ValMur123/python_intermedio.git
cd python_intermedio/tarea_1
python -m venv .venv
# Windows: .venv\Scripts\activate    |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Se abre en `http://localhost:8501`; se detiene con `Ctrl + C`.

Para regenerar los datos y el modelo: ejecutar `01_recoleccion.ipynb`, crear un archivo `.env` con
`GEMINI_API_KEY=tu_clave` y ejecutar `02_clasificacion.ipynb`. Los pesos del modelo (`modelo/model.safetensors`,
~440 MB) **no están en GitHub** porque superan el límite de 100 MB; el probador en vivo los necesita, así que hay que
ejecutar el notebook 02 primero. El resto del dashboard funciona sin ellos.

**Despliegue:** ejecución local comprobada (Streamlit Community Cloud no se usó porque los pesos del modelo no se suben
al repositorio).
