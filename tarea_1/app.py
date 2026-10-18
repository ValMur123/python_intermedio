"""Dashboard Streamlit · Tarea 1: Noticias peruanas, del titular al clasificador.
Ejecutar:  streamlit run app.py
"""
import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# Rutas relativas a la carpeta de este archivo (así funciona desde cualquier lugar)
BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_NOTICIAS = os.path.join(BASE, "datos", "noticias.csv")
RUTA_LLM = os.path.join(BASE, "datos", "etiquetas_llm.csv")
RUTA_METRICAS = os.path.join(BASE, "modelo", "metricas.json")
RUTA_COMPARATIVA = os.path.join(BASE, "modelo", "comparativa.csv")
RUTA_MATRIZ = os.path.join(BASE, "figuras", "matriz_confusion_test.png")
MODELO_LOCAL = os.path.join(BASE, "modelo")

# Nombres bonitos para mostrar
NOMBRES = {"politica": "Política", "economia": "Economía", "deportes": "Deportes",
           "ciencia_tecnologia": "Ciencia y tecnología"}

st.set_page_config(page_title="Clasificador de titulares peruanos", page_icon="🗞️", layout="wide")
st.title("🗞️ ¿Podemos convertir titulares peruanos en un clasificador de noticias?")

# ---------------- Carga de datos (con caché, como en la sesión 8) ----------------
@st.cache_data                     # lee los archivos una sola vez, no en cada clic
def cargar_datos():
    df = pd.read_csv(RUTA_NOTICIAS, encoding="utf-8-sig")
    if os.path.exists(RUTA_LLM):   # agrega la etiqueta del LLM a cada titular
        llm = pd.read_csv(RUTA_LLM, encoding="utf-8-sig")[["titular", "etiqueta_llm", "confianza"]]
        df = df.merge(llm, on="titular", how="left")
    df["categoria"] = df["etiqueta"].map(NOMBRES)
    return df


@st.cache_data
def cargar_metricas():
    if os.path.exists(RUTA_METRICAS):
        with open(RUTA_METRICAS, encoding="utf-8") as f:
            return json.load(f)
    return {}                       # si aún no existe el archivo, el dashboard igual funciona


df = cargar_datos()
met = cargar_metricas()

st.markdown(
    f"""
Recolecté **{len(df)} titulares** de {", ".join(sorted(df["medio"].unique()))} mediante sus RSS y sitemaps
oficiales, los etiqueté en 4 categorías (**política, economía, deportes, ciencia y tecnología**) con un LLM
(**Gemini**, supervisión débil auditada a mano) y ajusté **BETO**, un BERT en español, evaluado en un conjunto de
test que el modelo nunca vio. Más abajo puedes escribir cualquier titular para probarlo en vivo.
"""
)

# ---------------- Paso 2: filtros en la barra lateral ----------------
st.sidebar.header("Filtros")
medios = st.sidebar.multiselect("Medio", sorted(df["medio"].unique()),
                                default=sorted(df["medio"].unique()))
cats = st.sidebar.multiselect("Categoría", list(NOMBRES.values()),
                              default=list(NOMBRES.values()))
buscar = st.sidebar.text_input("Buscar en titulares", placeholder="Ej.: Congreso, BCR, Alianza")

# Tabla filtrada: la usan el gráfico y la tabla que vienen después
filtrado = df[df["medio"].isin(medios) & df["categoria"].isin(cats)]
if buscar.strip():
    filtrado = filtrado[filtrado["titular"].str.contains(buscar.strip(), case=False, na=False, regex=False)]
st.sidebar.caption(f"{len(filtrado)} de {len(df)} noticias seleccionadas")

# ---------------- Paso 3: indicadores clave (st.metric) ----------------
c1, c2, c3 = st.columns(3)

# 1) Total de noticias recolectadas
c1.metric("Noticias recolectadas", f"{len(df)}",
          help=f"{len(filtrado)} con los filtros actuales")

# 2) F1 macro del modelo en el test (y cuánto mejora frente al zero-shot)
f1 = met.get("f1_macro_test")
f1_zs = met.get("f1_macro_zero_shot")
c2.metric("F1 macro en test", f"{f1:.2f}" if f1 is not None else "—",
          delta=f"{f1 - f1_zs:+.2f} vs. zero-shot" if f1 is not None and f1_zs is not None else None)

# 3) Concordancia entre el LLM y la auditoría humana (viene como "19/20")
acuerdo = met.get("acuerdo_llm_humano")
if acuerdo:
    a, b = map(int, acuerdo.split("/"))
    c3.metric("Concordancia LLM vs. auditoría humana", f"{a / b:.0%}",
              help=f"{acuerdo} titulares coincidieron")
else:
    c3.metric("Concordancia LLM vs. auditoría humana", "—")