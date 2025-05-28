
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Oracle Item Setup - Web App", page_icon="⚙️")

st.markdown("""
    <style>
        body {
            background-color: #f8f9fa;
        }
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Oracle Item Setup - Web App")

# Inizializzazione della variabile per evitare errori
descr = ""

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.header("🔧 Input")
    thickness = st.number_input("Thickness", step=0.1, format="%.1f")
    uom = st.selectbox("UOM", ["mm", "in"])
    dwg_doc = st.text_input("Dwg/doc number")
    material_type = st.selectbox("Material Type", ["ASTM", "EN", "Miscellaneous"])
    material_prefix = st.selectbox("Material Prefix", ["A", "B", "C"])
    material_name = st.selectbox("Material Name", ["Material 1", "Material 2"])

    if st.button("Genera Output"):
        descr = f"GASKET, FLAT - THK: {thickness}{uom},\nMATERIAL:"

with col2:
    st.header("📤 Output")
    item = st.text_input("Item", "50158...")
    st.text_area("Description", value=descr, height=60)
    identificativo = st.text_input("Identificativo", "4590-GASKET")
    classe_ricambi = st.text_input("Classe ricambi", "1-2-3")

with col3:
    st.header("🧾 DataLoad")
    op_mode = st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"])
    item_number = st.text_input("Item Number", "Es. 50158-0001")
    dataload_string = st.text_area("Stringa per DataLoad", value=descr, height=100)
