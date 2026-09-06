import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard MIPER - Matriz de Riesgos",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Panel de Control Analítico - MIPER (Matriz de Riesgos)")
st.markdown("**Automatización e Inteligencia Operativa**")

# --- CARGA DE DATOS DESDE GOOGLE SHEETS (EN TIEMPO REAL) ---
# ttl=10 hace que los datos se actualicen automáticamente cada pocos segundos al recargar
@st.cache_data(ttl=10)
def cargar_datos_mipér():
    # Reemplaza 'TU_ID_DE_LA_HOJA' por el código que copiaste de tu URL de Google Sheets
    sheet_id = "1f2NMBj2tuCVXwAIzd63dFwovVALPXVVH" 
    
    # URL de exportación directa a formato CSV de la primera pestaña o la que necesites
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    # header=9 mantiene tu tabla iniciando en la fila 10
    df = pd.read_csv(url, header=9)
    df.columns = df.columns.astype(str).str.strip()
    return df

try:
    df = cargar_datos_mipér()
    st.sidebar.success("✅ Conectado a Google Sheets en tiempo real")
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()
# --- BUSCADOR INTELIGENTE DE COLUMNAS ---
def encontrar_columna(lista_columnas, palabras_clave):
    for col in lista_columnas:
        col_str = str(col).lower()
        if all(kw.lower() in col_str for kw in palabras_clave):
            return col
    return None

COL_TIPO = encontrar_columna(df.columns, ["peligro", "tipo"])
COL_CLASIFICACION = encontrar_columna(df.columns, ["clasificaci"])
COL_INTERPRETACION = encontrar_columna(df.columns, ["interpretación", "riesgo"])
COL_ACTIVIDAD = encontrar_columna(df.columns, ["actividad"])
COL_TAREA = encontrar_columna(df.columns, ["tárea"]) or encontrar_columna(df.columns, ["tarea"])
COL_EFICAZ = encontrar_columna(df.columns, ["eficaz"]) or encontrar_columna(df.columns, ["ap"])

# Validamos columnas críticas
if not COL_TIPO or not COL_CLASIFICACION or not COL_INTERPRETACION:
    st.error("⚠️ No se pudieron mapear automáticamente las columnas principales de peligro/riesgo.")
    st.write("Columnas detectadas en la fila 10 de tu Excel:", df.columns.tolist())
    st.stop()

# --- PANEL DE FILTROS EN EL LADO DERECHO (SIDEBAR) ---
st.sidebar.header("🎛️ Filtros de Selección")

# 1. Filtro por Actividad (si existe en el Excel)
if COL_ACTIVIDAD:
    actividades_disp = ["Todas"] + list(df[COL_ACTIVIDAD].dropna().unique())
    filtro_actividad = st.sidebar.selectbox("Seleccione Actividad:", options=actividades_disp)
else:
    filtro_actividad = "Todas"

# 2. Filtro por Tarea (si existe en el Excel)
if COL_TAREA:
    tareas_disp = ["Todas"] + list(df[COL_TAREA].dropna().unique())
    filtro_tarea = st.sidebar.selectbox("Seleccione Tarea / Tárea:", options=tareas_disp)
else:
    filtro_tarea = "Todas"

# 3. Filtro por Tipo de Peligro
tipos_disponibles = ["Todos"] + list(df[COL_TIPO].dropna().unique())
filtro_tipo = st.sidebar.selectbox("Seleccione Tipo de Peligro:", options=tipos_disponibles)

# 4. Filtro por Clasificación (Dinámico)
if filtro_tipo != "Todos":
    clasificaciones_disp = ["Todas"] + list(df[df[COL_TIPO] == filtro_tipo][COL_CLASIFICACION].dropna().unique())
else:
    clasificaciones_disp = ["Todas"] + list(df[COL_CLASIFICACION].dropna().unique())
filtro_clasificacion = st.sidebar.selectbox("Seleccione Clasificación:", options=clasificaciones_disp)

# 5. Filtro por Interpretación del Riesgo Residual
interpretaciones_disp = ["Todas"] + list(df[COL_INTERPRETACION].dropna().unique())
filtro_interpretacion = st.sidebar.selectbox("Riesgo Residual (Interpretación):", options=interpretaciones_disp)

# --- APLICACIÓN DE FILTROS ---
df_filtered = df.copy()

if filtro_actividad != "Todas" and COL_ACTIVIDAD:
    df_filtered = df_filtered[df_filtered[COL_ACTIVIDAD] == filtro_actividad]

if filtro_tarea != "Todas" and COL_TAREA:
    df_filtered = df_filtered[df_filtered[COL_TAREA] == filtro_tarea]

if filtro_tipo != "Todos":
    df_filtered = df_filtered[df_filtered[COL_TIPO] == filtro_tipo]

if filtro_clasificacion != "Todas":
    df_filtered = df_filtered[df_filtered[COL_CLASIFICACION] == filtro_clasificacion]

if filtro_interpretacion != "Todas":
    df_filtered = df_filtered[df_filtered[COL_INTERPRETACION] == filtro_interpretacion]

# --- MÉTRICAS SUPERIORES ---
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("📊 Total Registros en Vista", len(df_filtered))
col_kpi2.metric("⚠️ Tipos Activos", df_filtered[COL_TIPO].nunique() if not df_filtered.empty else 0)
col_kpi3.metric("🔍 Clasificaciones Activas", df_filtered[COL_CLASIFICACION].nunique() if not df_filtered.empty else 0)

st.divider()

# --- GRÁFICOS ---
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Recuento por Tipo de Peligro")
    if not df_filtered.empty:
        df_tipo_count = df_filtered[COL_TIPO].value_counts().reset_index()
        df_tipo_count.columns = ["Tipo", "Recuento"]
        
        fig_tipo = px.bar(
            df_tipo_count,
            x="Tipo",
            y="Recuento",
            color="Tipo",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
    else:
        st.warning("No hay datos.")

with c2:
    st.subheader("Clasificación vs Riesgo Residual")
    if not df_filtered.empty:
        fig_relacion = px.histogram(
            df_filtered,
            x=COL_CLASIFICACION,
            color=COL_INTERPRETACION,
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_relacion.update_layout(xaxis_tickangle=-35, legend_title="Riesgo Residual")
        st.plotly_chart(fig_relacion, use_container_width=True)
    else:
        st.warning("No hay datos.")

with c3:
    st.subheader("Eficacia de la Gestión")
    if not df_filtered.empty and COL_EFICAZ:
        df_eficaz = df_filtered[COL_EFICAZ].astype(str).str.strip().value_counts().reset_index()
        df_eficaz.columns = ["Eficacia", "Cantidad"]
        
        # Mapeo de colores: Verde para Si/SI, Rojo para No/NO
        color_map = {}
        for val in df_eficaz["Eficacia"]:
            if val.lower() in ["si", "sí", "s"]:
                color_map[val] = "#2ca02c" # Verde
            else:
                color_map[val] = "#d62728" # Rojo

        fig_donut = px.pie(
            df_eficaz,
            names="Eficacia",
            values="Cantidad",
            hole=0.5, # Gráfico de anillo
            color="Eficacia",
            color_discrete_map=color_map
        )
        fig_num = fig_donut.update_traces(textinfo="percent+value", textfont_size=14)
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Columna de eficacia no disponible o sin datos.")

# --- TABLA DETALLADA ---
st.subheader("📋 Detalle Filtrado de la Matriz MIPER")
st.dataframe(df_filtered, use_container_width=True)
