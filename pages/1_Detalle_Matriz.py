import streamlit as st
import pandas as pd

st.set_page_config(page_title="Detalle de Matriz", page_icon="📋", layout="wide")

st.title("📋 Detalle Completo de la Matriz MIPER")
st.markdown("Consulta y filtra los registros específicos de la operación.")

# Carga de datos idéntica conectada a Google Sheets
@st.cache_data(ttl=10)
def cargar_datos_miper():
    sheet_id = "14MMoJZ3zCqzsMvo6ZDzt3lQn_j6-GhE-ysVDlL175Dg" 
    gid = "398981841"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url, header=9)
    df.columns = df.columns.astype(str).str.strip()
    return df

df = cargar_datos_miper()

# Tabla interactiva completa
st.dataframe(df, use_container_width=True)
