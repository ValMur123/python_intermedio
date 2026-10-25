"""Dashboard de la Tarea 2: documentos (OCR) y audios (ASR) peruanos convertidos en texto buscable.

Solo lee los CSV generados en 01_extraccion.ipynb y 02_evaluacion.ipynb: no ejecuta OCR, ASR ni LLM.
Ejecutar en local:  streamlit run app.py
"""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).resolve().parent
DATOS = BASE / "datos"
EJEMPLOS = DATOS / "ejemplos"


st.set_page_config(page_title="Voces y documentos peruanos", page_icon="📜", layout="wide")


# ───────────────────────────────────────────── datos
@st.cache_data
def leer(nombre):
    ruta = DATOS / nombre
    if not ruta.exists():
        return pd.DataFrame()
    # sep=None detecta solo si el archivo usa "," o ";" (auditoria_llm.csv se guardó con ";" para Excel)
    return pd.read_csv(ruta, dtype={"id": str}, encoding="utf-8-sig", sep=None, engine="python")


docs = leer("documentos.csv").fillna({"texto_ocr": "", "texto_referencia": ""})
audios = leer("transcripciones.csv").fillna({"texto_asr": "", "texto_referencia": ""})
llm = leer("extraccion_llm.csv")
metricas = leer("metricas.csv")
comparacion = leer("comparacion_modelos.csv")
auditoria = leer("auditoria_llm.csv").fillna("")

campos = {r.id: json.loads(r.campos_json) for r in llm.itertuples()} if len(llm) else {}
if len(audios):
    audios["minutos"] = audios["duracion_seg"] / 60
    audios["fuente"] = audios.get("fuente", pd.Series("—", index=audios.index)).fillna("—")


def metrica(modalidad, modelo_contiene=None):
    m = metricas[metricas.modalidad == modalidad] if len(metricas) else metricas
    if modelo_contiene is not None and len(m):
        m = m[m.modelo.str.contains(modelo_contiene, case=False, regex=False)]
    return m


def imagen_publicable(doc_id):
    p = EJEMPLOS / "img" / f"{doc_id}.jpg"
    fila = docs[docs.id == doc_id]
    ok = len(fila) and str(fila.iloc[0].get("publicar_imagen", "")).strip().lower() == "si"
    return p if ok and p.exists() else None


def audio_publicable(clip_id):
    for ext in ("ogg", "mp3", "wav"):
        p = EJEMPLOS / "audio" / f"{clip_id}.{ext}"
        if p.exists():
            return p
    return None


# ───────────────────────────────────────────── encabezado
st.markdown("<h1 style='text-align:center'>¿Pueden convertirse documentos escaneados y entrevistas en audio "
            "en un archivo de texto estructurado y buscable?</h1>", unsafe_allow_html=True)
st.caption(
    "Corpus: 25 documentos peruanos (8 impresos de dominio público, 8 fotos propias con sombra o inclinación y 9 manuscritos propios) "
    "y más de 30 minutos de audio en español peruano (OpenSLR 73 y entrevistas de Wikimedia Commons, CC BY-SA 4.0). "
    "Pipeline: PaddleOCR → faster-whisper con VAD y diarización → seudonimización → extracción JSON con LLM → "
    "evaluación CER/WER sobre 10 documentos y 10 clips transcritos a mano. Esta app solo muestra resultados precalculados."
)

# ───────────────────────────────────────────── barra lateral: filtros
with st.sidebar:
    st.header("Filtros")
    buscar = st.text_input("Buscar palabra en los textos OCR y ASR", placeholder="ej. lomo, Lima, chicharrón")
    tipos = st.multiselect("Tipo de documento", ["impreso", "foto", "manuscrito"], default=["impreso", "foto", "manuscrito"])
    fuentes = sorted(audios["fuente"].unique()) if len(audios) else []
    fuente_sel = st.multiselect("Fuente del audio", fuentes, default=fuentes)
    if len(audios):
        dmin, dmax = float(audios.duracion_seg.min()), float(audios.duracion_seg.max())
        rango = st.slider("Duración del clip (s)", dmin, dmax, (dmin, dmax))
    modelos_disp = sorted(comparacion["modelo"].unique()) if len(comparacion) else []
    modelos_sel = st.multiselect("Modelos a comparar", modelos_disp, default=modelos_disp)

f_docs = docs[docs.tipo.isin(tipos)] if len(docs) else docs
f_aud = audios[audios.fuente.isin(fuente_sel) & audios.duracion_seg.between(*rango)] if len(audios) else audios
if buscar:
    f_docs = f_docs[f_docs.texto_ocr.str.contains(buscar, case=False, regex=False)]
    f_aud = f_aud[f_aud.texto_asr.str.contains(buscar, case=False, regex=False)]
f_comp = comparacion[comparacion.modelo.isin(modelos_sel)] if len(comparacion) else comparacion

# ───────────────────────────────────────────── indicadores
c = st.columns(5)
c[0].metric("Documentos procesados", len(docs))
c[1].metric("Minutos de audio transcritos", f"{audios.duracion_seg.sum() / 60:.1f}" if len(audios) else "—")
cer = metrica("documento")
wer = metrica("audio")
c[2].metric("Mejor CER (10 docs)", f"{cer['error_%'].min():.1f} %" if len(cer) else "—",
            help=cer.loc[cer['error_%'].idxmin(), "modelo"] if len(cer) else None)
c[3].metric("Mejor WER (10 clips)", f"{wer['error_%'].min():.1f} %" if len(wer) else "—",
            help=wer.loc[wer['error_%'].idxmin(), "modelo"] if len(wer) else None)
if len(auditoria) and "correcto" in auditoria:
    ok = auditoria.correcto.str.strip().str.lower().isin({"si", "sí", "1", "x"}).sum()
    c[4].metric("Acuerdo LLM vs. auditoría humana", f"{ok}/20 ({ok / 20:.0%})")
else:
    c[4].metric("Acuerdo LLM vs. auditoría humana", "—")

if buscar:
    st.info(f"'{buscar}' aparece en {len(f_docs)} documentos y {len(f_aud)} clips.")

tab_res, tab_doc, tab_aud = st.tabs(["📊 Resultados", "📜 Documentos", "🎙️ Audios"])

# ───────────────────────────────────────────── resultados
with tab_res:
    col1, col2 = st.columns(2)
    if len(f_docs):
        por_tipo = f_docs.groupby("tipo").agg(documentos=("id", "count"), confianza=("confianza_media", "mean")).reset_index()
        fig = px.bar(por_tipo, x="tipo", y="documentos", color="tipo", text="documentos", hover_data={"confianza": ":.2f"},
                     title="Documentos por tipo (filtrados)")
        fig.update_layout(showlegend=False)
        col1.plotly_chart(fig, use_container_width=True)
    if len(f_aud):
        fig = px.bar(f_aud.sort_values("id"), x="id", y="duracion_seg", color="fuente",
                     hover_data=["n_hablantes"], title="Duración de cada clip (filtrados)")
        fig.update_layout(xaxis_title="clip", yaxis_title="segundos", xaxis={"showticklabels": False})
        col2.plotly_chart(fig, use_container_width=True)

    if len(f_comp):
        st.subheader("Error por modelo sobre las mismas muestras de evaluación")
        col3, col4 = st.columns(2)
        g = f_comp[f_comp.modalidad == "documento"].groupby(["modelo", "grupo"])["error"].mean().mul(100).reset_index()
        if len(g):
            col3.plotly_chart(px.bar(g, x="grupo", y="error", color="modelo", barmode="group", text_auto=".0f",
                                     title="CER medio (%) por tipo de documento", labels={"error": "CER %", "grupo": "tipo"}),
                              use_container_width=True)
        h = f_comp[f_comp.modalidad == "audio"].groupby(["modelo", "grupo"])["error"].mean().mul(100).reset_index()
        if len(h):
            col4.plotly_chart(px.bar(h, x="grupo", y="error", color="modelo", barmode="group", text_auto=".0f",
                                     title="WER medio (%) por fuente de audio", labels={"error": "WER %", "grupo": "fuente"}),
                              use_container_width=True)
        st.dataframe(metricas, use_container_width=True, hide_index=True)

    st.subheader("Tabla de registros (textos seudonimizados)")
    tabla = pd.concat([
        f_docs.assign(modalidad="documento", texto=f_docs.texto_ocr, modelo=f_docs.modelo_ocr)[["id", "modalidad", "tipo", "texto", "modelo"]]
        if len(f_docs) else pd.DataFrame(),
        f_aud.assign(modalidad="audio", tipo=f_aud.fuente, texto=f_aud.texto_asr, modelo=f_aud.modelo_asr)[["id", "modalidad", "tipo", "texto", "modelo"]]
        if len(f_aud) else pd.DataFrame(),
    ], ignore_index=True)
    st.dataframe(tabla, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Descargar CSV", tabla.to_csv(index=False).encode("utf-8-sig"), "textos_filtrados.csv", "text/csv")

# ───────────────────────────────────────────── explorador de documentos
with tab_doc:
    if not len(f_docs):
        st.warning("Ningún documento coincide con los filtros.")
    else:
        etiquetas = {r.id: f"{r.id} · {r.tipo} · {r.descripcion}" for r in f_docs.itertuples()}
        doc_id = st.selectbox("Documento", list(etiquetas), format_func=etiquetas.get)
        d = docs[docs.id == doc_id].iloc[0]
        izq, der = st.columns([1, 1])
        img = imagen_publicable(doc_id)
        if img:
            izq.image(str(img), caption=f"{d.descripcion} · {d.fuente}", use_container_width=True)
        else:
            izq.info("Imagen no publicada (contiene personas o datos de particulares). Se muestran solo el texto y los metadatos.")
        izq.caption(f"Modelo: {d.modelo_ocr} · confianza media {d.confianza_media:.2f}")
        der.markdown("**Texto OCR (seudonimizado)**")
        der.text_area("ocr", d.texto_ocr, height=260, label_visibility="collapsed")
        if d.texto_referencia:
            der.markdown("**Transcripción manual de referencia**")
            der.text_area("ref", d.texto_referencia, height=150, label_visibility="collapsed")
            filas = comparacion[(comparacion.id == doc_id)] if len(comparacion) else pd.DataFrame()
            for r in filas.itertuples():
                der.metric(f"CER {r.modelo}", f"{r.error * 100:.1f} %")
        if doc_id in campos:
            st.markdown("**Campos estructurados extraídos por el LLM**")
            st.json(campos[doc_id])

# ───────────────────────────────────────────── explorador de audios
with tab_aud:
    if not len(f_aud):
        st.warning("Ningún clip coincide con los filtros.")
    else:
        etiquetas = {r.id: f"{r.id} · {r.fuente} · {r.duracion_seg:.0f} s · {r.n_hablantes} hablante(s)" for r in f_aud.itertuples()}
        clip_id = st.selectbox("Clip", list(etiquetas), format_func=etiquetas.get)
        a = audios[audios.id == clip_id].iloc[0]
        ruta = audio_publicable(clip_id)
        if ruta:
            st.audio(str(ruta))
            st.caption(f"{a.get('origen', '')} · {a.fuente} · licencia CC BY-SA 4.0")
        else:
            st.info("Este clip no está entre los ejemplos publicados; se muestra su transcripción y metadatos.")
        st.markdown(f"**Transcripción ASR** ({a.modelo_asr}) · hablantes detectados: **{a.n_hablantes}**")
        texto = a.texto_asr.replace("[HABLANTE_", "\n\n**[HABLANTE_").replace("] ", "]** ") if "[HABLANTE_" in a.texto_asr else a.texto_asr
        st.markdown(texto)
        filas = comparacion[comparacion.id == clip_id] if len(comparacion) else pd.DataFrame()
        if len(filas):
            st.markdown("**Comparación de modelos sobre este clip**")
            cols = st.columns(len(filas))
            for col, r in zip(cols, filas.itertuples()):
                col.metric(r.modelo, f"WER {r.error * 100:.1f} %", f"RTF {r.rtf:.2f}", delta_color="off")
                col.caption(str(r.texto)[:600])
        if a.texto_referencia:
            with st.expander("Transcripción manual de referencia"):
                st.write(a.texto_referencia)
        if clip_id in campos:
            st.markdown("**Campos estructurados extraídos por el LLM**")
            st.json(campos[clip_id])

st.divider()
st.caption("Fuentes y licencias de cada archivo: datos/fuentes.csv · Código de voz.py: Sesión 13 del curso (d2cml-ai/Data-Science-Python, MIT).")


