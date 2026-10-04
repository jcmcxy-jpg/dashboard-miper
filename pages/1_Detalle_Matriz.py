import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Detalle de Matriz", page_icon="📋", layout="wide")

# --- ESTILO CSS PERSONALIZADO PARA EL BOTÓN ---
st.markdown("""
    <style>
    /* Estilo específico para el botón de descarga basado en su clave */
    .st-key-btn_descargar button {
        background-color: #0056b3 !important;
        color: white !important;
        font-family: 'Arial', sans-serif !important;
        font-size: 12px !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 16px !important;
    }
    .st-key-btn_descargar button:hover {
        background-color: #004085 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Detalle Completo de la Matriz MIPER")
st.markdown("Consulta y filtra los registros específicos de la operación.")

# Carga de datos conectada a Google Sheets
@st.cache_data(ttl=10)
def cargar_datos_miper():
    sheet_id = "14MMoJZ3zCqzsMvo6ZDzt3lQn_j6-GhE-ysVDlL175Dg" 
    gid = "398981841"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url, header=9)
    df.columns = df.columns.astype(str).str.strip()
    return df

df = cargar_datos_miper()

# --- FUNCIÓN PARA CONVERTIR A EXCEL ---
@st.cache_data
def convertir_a_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        data.to_excel(writer, index=False, sheet_name='Matriz_Filtrada')
    return output.getvalue()

excel_data = convertir_a_excel(df)

# --- BOTÓN CON CLASE PERSONALIZADA ---
st.download_button(
    label="📥 Descargar matriz en Excel",
    data=excel_data,
    file_name="reporte_miper_detalle.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="btn_descargar" # Esta clave conecta directamente con el estilo CSS de arriba
)

# Tabla interactiva completa
st.dataframe(df, use_container_width=True)
