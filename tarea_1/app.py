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
 # ---------------- Paso 4: gráfico y tabla (responden a los filtros) ----------------
col_g, col_t = st.columns([1, 1.4])

with col_g:
    # Título analítico: dice la conclusión, no solo la variable
    if len(filtrado):
        top = filtrado["categoria"].value_counts()
        titulo = f"{top.index[0]} lidera la selección con {top.iloc[0]} noticias ({top.iloc[0] / len(filtrado):.0%})"
    else:
        titulo = "Sin noticias para los filtros elegidos"
    datos_graf = filtrado.groupby(["categoria", "medio"]).size().reset_index(name="n")
    fig = px.bar(datos_graf, x="n", y="categoria", color="medio", barmode="group", orientation="h",
                 text_auto=True, title=titulo,
                 labels={"categoria": "", "n": "Noticias", "medio": "Medio"})
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(legend=dict(orientation="h", y=-0.2), yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, width="stretch")

with col_t:
    st.subheader("Explorar noticias")
    columnas = ["titular", "bajada", "medio", "seccion_original", "fecha", "etiqueta", "url"]
    st.dataframe(filtrado[columnas], width="stretch", height=380,
                 column_config={"url": st.column_config.LinkColumn("url")})
    st.download_button("⬇️ Descargar CSV filtrado",
                       filtrado[columnas].to_csv(index=False).encode("utf-8-sig"),
                       file_name="noticias_filtradas.csv", mime="text/csv")   
    
# ---------------- Resultados del modelo ----------------
st.divider()
st.header("📊 ¿Qué tan bien clasifica?")
col_c, col_m = st.columns([1.3, 1])

with col_c:
    if os.path.exists(RUTA_COMPARATIVA):
        st.markdown("**Comparación en el test reservado**")
        st.dataframe(pd.read_csv(RUTA_COMPARATIVA, encoding="utf-8-sig"), width="stretch", hide_index=True)
    if met.get("f1_por_categoria"):
        f1c = pd.DataFrame({"categoria": [NOMBRES.get(k, k) for k in met["f1_por_categoria"]],
                            "F1": list(met["f1_por_categoria"].values())}).sort_values("F1")
        mejor, peor = f1c.iloc[-1], f1c.iloc[0]
        fig_c = px.bar(f1c, x="F1", y="categoria", orientation="h", range_x=[0, 1],
                       text=f1c["F1"].map("{:.2f}".format), labels={"categoria": ""},
                       title=f"{mejor['categoria']} es la más fácil (F1 {mejor['F1']:.2f}); "
                             f"{peor['categoria']} la más difícil ({peor['F1']:.2f})")
        fig_c.update_layout(height=300)
        st.plotly_chart(fig_c, width="stretch")

with col_m:
    if os.path.exists(RUTA_MATRIZ):
        st.image(RUTA_MATRIZ, caption="Matriz de confusión en el test (etiqueta del diario vs. predicción)")

if "etiqueta_llm" in df.columns:
    st.caption(f"El LLM coincide con la sección del diario en el {(df['etiqueta_llm'] == df['etiqueta']).mean():.1%} "
               "de los titulares; las diferencias suelen ser titulares que mezclan temas (p. ej. política y economía).")


# ---------------- Paso 5: probador en vivo ----------------
@st.cache_resource(show_spinner="Cargando el modelo BETO…")   # carga el modelo una sola vez
def cargar_clasificador():
    from transformers import pipeline
    return pipeline("text-classification", model=MODELO_LOCAL, tokenizer=MODELO_LOCAL, top_k=None)


st.divider()
st.header("🔎 Prueba el clasificador")
titular = st.text_input("Escribe o pega un titular",
                        placeholder="Ej.: BCR mantiene su tasa de referencia por tercer mes consecutivo")

if st.button("Clasificar", type="primary"):
    if not titular.strip():
        st.warning("Escribe un titular primero.")
    else:
        try:
            clf = cargar_clasificador()
            salida = clf(titular.strip())
            salida = salida[0] if isinstance(salida[0], list) else salida     # lista de {label, score}
            probs = pd.DataFrame(salida).sort_values("score", ascending=False)
            probs["categoria"] = probs["label"].map(NOMBRES).fillna(probs["label"])
            ganador = probs.iloc[0]

            st.success(f"**{ganador['categoria']}** · probabilidad {ganador['score']:.1%}")
            if ganador["score"] < 0.6:
                st.info("Confianza baja: el titular podría pertenecer a más de una categoría.")

            fig_p = px.bar(probs, x="score", y="categoria", orientation="h", range_x=[0, 1],
                           text=probs["score"].map("{:.1%}".format),
                           labels={"score": "Probabilidad", "categoria": ""})
            fig_p.update_layout(height=260, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_p, width="stretch")
        except Exception as e:
            st.error("No se pudo cargar el modelo. Ejecuta primero `02_clasificacion.ipynb`, que guarda el "
                     f"modelo en `modelo/`. Detalle: {type(e).__name__}: {e}")

st.divider()
st.caption("Fuente: RSS y sitemaps oficiales de La República y El Comercio (octubre de 2026). Etiquetas débiles con "
           "Gemini; modelo BETO (dccuchile/bert-base-spanish-wwm-cased) ajustado. "
           "Tarea 1 · Python Intermedio · QLAB PUCP · Valeria Murga.")