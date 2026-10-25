# Tarea 2 · Voces y documentos peruanos: del archivo escaneado al texto buscable


**Pregunta:** ¿Pueden convertirse documentos escaneados y entrevistas en audio en un archivo de texto estructurado y buscable?

**Dashboard público:** https://pythonintermedio-hs4c7qdetk3x7ydcjgu7ud.streamlit.app

Pipeline: imágenes → **PaddleOCR** · audio → **faster-whisper** (VAD + diarización con `voz.py` de la Sesión 13) → seudonimización →
extracción JSON con **LLM local (Qwen2.5 3B vía Ollama)** → evaluación **CER/WER** sobre 10 documentos y 10 clips transcritos a mano → dashboard en **Streamlit**.

## Corpus y fuentes

| Corpus | Contenido | Fuente | Licencia | Fecha de extracción |
|---|---|---|---|---|
| Documentos impresos (8) | *El Peruano* 1844, billete de 20 soles 1879, *Mercurio Peruano* 1791, *El Comercio* 1839 / c. 1842 / 1945, *La Mesa Peruana* 1867, Constitución de 1823 | Wikimedia Commons, Repositorio PUCP | Dominio público / CC0 | 23/10/2026 |
| Fotos (8) | Carteles, menús, placa y avisos con sombra, inclinación o poca luz (Jesús María, Lima) | Fotografías propias | CC BY 4.0 | 23/10/2026 |
| Manuscritos (9) | Pizarras de menú (tiza y plumón), apuntes y una nota en papel | Fotografías propias | CC BY 4.0 | 23/10/2026 |
| Audio (32 min, 24 clips) | Español peruano leído (OpenSLR 73) + entrevistas en la calle en El Agustino y a una dirigente de Fenmucarinap | [OpenSLR 73](https://www.openslr.org/73/), [Wikimedia Commons](https://commons.wikimedia.org) | CC BY-SA 4.0 | 24/10/2026 |

URL, autor, licencia y forma de recuperar cada archivo: [`datos/fuentes.csv`](datos/fuentes.csv).
Los originales (imágenes y audio) **no se versionan** (`datos/raw/` está en `.gitignore`); en `datos/ejemplos/` hay una muestra liviana y publicable.

**Datos personales:** el nombre y los teléfonos de un particular (cartel de remate, `doc_014`) se reemplazaron por `[PERSONA_1]` y `[TELEFONO]`.
La revisión humana detectó que el OCR había deformado el nombre y la seudonimización automática no lo atrapó; se corrigió agregando la variante a una lista privada no versionada.
Las imágenes con personas o datos de particulares (`doc_012`, `doc_014`) no se publican: en el dashboard solo se muestra su texto.

## Estructura

```
tarea_2/
├── 01_extraccion.ipynb     # OCR, ASR, diarización, seudonimización, limpieza, EDA
├── 02_evaluacion.ipynb     # CER/WER, comparación de modelos, LLM y auditoría
├── app.py                  # dashboard Streamlit (solo lee CSV)
├── voz.py                  # Sesión 13 del curso (d2cml-ai/Data-Science-Python, licencia MIT)
├── datos/
│   ├── documentos.csv · transcripciones.csv · fuentes.csv
│   ├── extraccion_llm.csv · auditoria_llm.csv · metricas.csv · comparacion_modelos.csv
│   └── ejemplos/           # imágenes y audios publicables
├── modelos/config_evaluacion.json   # muestra de evaluación fijada antes de medir
└── evidencias_ia/          # capturas de la conversación con la IA
```

## Resultados (muestra de 10 documentos y 10 clips)

| Modalidad | Modelo | Error | Latencia |
|---|---|---|---|
| Documentos | **PaddleOCR 3.7 (base)** ✔ | **CER 13.9 %** | __ s/doc |
| Documentos | Tesseract 5 (spa) | CER __ % | __ s/doc |
| Audio | faster-whisper small (base) | WER ≈ 9.5 % | RTF ≈ 0.55 |
| Audio | **faster-whisper large-v3-turbo** ✔ | **WER 6.1 %** | RTF ≈ 0.6 |
| Audio | Qwen3-ASR 0.6B | WER ≈ 8 % | RTF ≈ 1.0 |
| LLM | Qwen2.5 3B (Ollama, local) | Acuerdo con auditoría humana: **5/20 (25 %)** | — |

## Hallazgos

1. **PaddleOCR es ≈3.5 veces más preciso que Tesseract**, aunque mucho más lento en CPU. Tesseract falla sobre todo en fotos (relieve, sombras, perspectiva: CER 100 % en el billete de 1879 y la placa del parque); PaddleOCR, en manuscritos de pizarra.
2. **El ruido importa más que el modelo:** en voz leída los tres modelos de ASR casi no se equivocan, pero en la entrevista callejera de El Agustino (`clip_002`) el WER sube a 56–72 %. Turbo es el más robusto y el más rápido que tiempo real.
3. **El LLM pequeño omite más de lo que inventa:** casi no fabricó emisores, fechas ni montos, pero dejó vacíos datos presentes y malinterpretó las frases leídas de OpenSLR como conversaciones. Necesita revisión humana.

## Limitaciones

1. **Todo corrió en CPU (Windows).** PaddlePaddle 3.3 falla con la aceleración oneDNN en Windows, así que se desactivó (`enable_mkldnn=False`): el OCR de un periódico completo tardó hasta 7 minutos. Faster-whisper turbo transcribió a ~0,7× tiempo real.
3. **El LLM terminó siendo local.** Las claves nuevas de Gemini (formato `AQ.`) devolvían `API key not valid`, así que se usó Qwen2.5 3B con Ollama: más privado y gratuito, pero menos capaz (5/20). Una clave de prueba de Gemini quedó en el historial de un commit; fue revocada antes de publicar.
2. **La mayor parte del audio es voz leída** (OpenSLR 73, ~70 %): es más limpia que una entrevista real, así que el WER global subestima la dificultad de entrevistas de campo. Solo hay ~10 min de entrevistas reales con licencia libre.

## Cómo ejecutar

**Dashboard (local):**
```
pip install -r requirements.txt
streamlit run app.py
```

**Notebooks (Python 3.12, Windows):**
```
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install "paddlepaddle>=3.2.1" "paddleocr==3.7.0" faster-whisper jiwer rapidfuzz "pyannote.audio>=4.0.7" soundfile scipy pandas requests plotly kaleido nbformat ipykernel pytesseract "transformers>=5.16" accelerate pydantic
```
En `01_extraccion.ipynb` se importa `torch` antes que `paddle` (en Windows, al revés falla una DLL). Para Tesseract: `winget install UB-Mannheim.TesseractOCR`. Para el LLM: instalar Ollama (`winget install Ollama.Ollama`) y `ollama pull qwen2.5:3b`.

## Uso de IA

El desarrollo se apoyó en un asistente de IA (Claude). Las capturas completas de la conversación están en [`evidencias_ia/`](evidencias_ia/).
La recolección y selección de documentos, las fotografías, las transcripciones manuales de referencia y la auditoría del LLM las hice yo.
