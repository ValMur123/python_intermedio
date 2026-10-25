# Bitácora · Tarea 2: Voces y documentos peruanos

Registro de avances con el commit correspondiente. Cada parte se siguió en su propio issue del repositorio.

| Parte | Issue | Contenido |
|---|---|---|
| 1 | #4 | Extracción: OCR, ASR, seudonimización, limpieza y EDA |
| 2 | #5 | Evaluación: CER/WER, comparación de modelos, LLM y auditoría |
| 3 | #6 | Dashboard en Streamlit y README |

---

## Parte 1 · Extracción (#4)

| Commit | Avance |
|---|---|
| `0b23c96` | Estructura de la carpeta `tarea_2` y corpus de 25 documentos (8 impresos de dominio público, 8 fotos propias y 9 manuscritos propios). Fuentes y licencias registradas en `fuentes.csv`. |
| `b6b786e` | Configuración del entorno en VS Code (Python 3.12, venv) y OCR con PaddleOCR sobre los 25 documentos. |
| `bad4173` | ASR con faster-whisper large-v3-turbo + VAD y diarización con `voz.py` de la Sesión 13 (licencia MIT). 24 clips, 32 min de audio (OpenSLR 73 + entrevistas de Wikimedia Commons). |
| `5def266` | Seudonimización de nombres, DNI y teléfonos. |
| `af82425` | Limpieza: duplicados y textos vacíos. |
| `13b9091` | Análisis exploratorio con 3 gráficos: documentos por tipo, duración de clips y longitud de textos. |
| `ae99b00` | Validación final, exportación de `documentos.csv` y `transcripciones.csv`, y ejemplos publicables en `datos/ejemplos/`. |

**Problemas y cómo se resolvieron**
- PaddlePaddle no tiene versión para Python 3.14 → se creó el venv con Python 3.12.
- Error de DLL de `torch` en Windows (`shm.dll`) → se instaló torch para CPU y se importa antes que `paddle`.
- PaddleOCR falla con oneDNN en Windows → `enable_mkldnn=False`.
- Wikimedia Commons bloqueaba descargas seguidas (error 429) → descarga con reintentos y espera.
- La revisión manual detectó un nombre que el OCR había deformado y la seudonimización no había reemplazado → se agregó la variante a una lista privada no versionada.

---

## Parte 2 · Evaluación (#5)

| Commit | Avance |
|---|---|
| `79f805f` | Muestra de evaluación fijada antes de medir (semilla 2026): 10 documentos y 10 clips en `modelos/config_evaluacion.json`. |
| `0cb8a10` | 20 referencias transcritas a mano (10 documentos y 10 clips). |
| `132bb31` | Evaluación de los modelos base: CER de PaddleOCR vs. Tesseract, y WER de faster-whisper small vs. large-v3-turbo vs. Qwen3-ASR 0.6B, con RTF como latencia. |
| `a7c1481` | Extracción estructurada en JSON con LLM (49 registros). |
| `ee61095` | Auditoría humana de 20 extracciones: acuerdo LLM-humano 5/20 (25 %). |
| `d91a5d0` | Tabla comparativa, gráficos, casos difíciles con sus causas y decisión final. |

**Problemas y cómo se resolvieron**
- Tesseract no estaba instalado → `winget install UB-Mannheim.TesseractOCR` y variable `TESSDATA_PREFIX`.
- Las claves nuevas de Gemini (formato `AQ.`) devolvían `API key not valid` → se cambió a **Qwen2.5 3B local con Ollama** (salida validada con pydantic, temperatura 0).
- Una clave de Gemini quedó en el historial del commit `a7c1481`. GitHub bloqueó el push; la clave se **revocó** antes de publicar.

**Resultados**
- OCR: **PaddleOCR** (CER 13.9 %), ≈3.5 veces más preciso que Tesseract.
- ASR: **faster-whisper large-v3-turbo** (WER 6.1 %), el más preciso y más rápido que tiempo real.
- LLM: omite más datos de los que inventa; necesita revisión humana.

---

## Parte 3 · Dashboard (#6)

| Commit | Avance |
|---|---|
| `1ff8216` | Dashboard en Streamlit (`app.py`), que solo lee los CSV. Lee archivos separados por `,` o `;`. |
| `5762bea` | Dashboard terminado y probado en local: filtros, métricas, gráficos y explorador de documentos y audios. Las imágenes con datos personales no se muestran. |
| `_______` | README con resultados, hallazgos, limitaciones y enlace a la app. Bitácora. |

**App publicada:** https://pythonintermedio-hs4c7qdetk3x7ydcjgu7ud.streamlit.app
