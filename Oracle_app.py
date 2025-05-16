import streamlit as st
import pandas as pd

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    return {
        "size_df": pd.read_excel(xls, sheet_name="Pump Size"),
        "features_df": pd.read_excel(xls, sheet_name="Features"),
        "materials_df": pd.read_excel(xls, sheet_name="Materials")
    }

data = load_config_data()
size_df = data["size_df"]
features_df = data["features_df"]
materials_df = data["materials_df"]

part_options = [
    "Baseplate, Pump",
    "Casing, Pump",
    "Casing Cover, Pump",
    "Impeller, Pump",
    "Balance Bushing, Pump",
    "Balance Drum, Pump",
    "Balance Disc, Pump",
    "Shaft, Pump",
    "Flange, Pipe"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

pump_models = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

def genera_output_flange():
    pipe_type = st.selectbox("Pipe type", ["SW", "WN"])
    size = st.selectbox("Size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    face_type = st.selectbox("Face type", ["RF", "FF", "RJ"])
    class_flange = st.text_input("Class (es. 150 Sch)")
    material = st.text_input("Material (es. A106-GR.B)")
    additional = st.text_input("Additional features (opzionale)")
    note = st.text_area("Note (opzionale)", height=80)
    description = f"Flange, Pipe type {pipe_type} Size {size} Face type {face_type} Class {class_flange} Material {material}"
    if additional:
        description += f" Additional features: {additional}"
    if note:
        description += f" Note: {note}"
    st.session_state["output_data"] = {
        "Item": "50155…",
        "Description": description,
        "Identificativo": "1245-FLANGE",
        "Classe ricambi": "",
        "Categories": "Fascia ite 5",
        "Catalog": "",        "Material": "NOT AVAILABLE",
        "Template": "FPD_BUY_2",
        "FPD material code": "NA",
        "Template": "",
        "ERP_L1": "23_FLANGE",
        "ERP_L2": "13_OTHER",
        "To supplier": "",
        "Quality": ""
    }

# === ROUTING ===
if selected_part == "Flange, Pipe":
    st.subheader("Configurazione - Flange, Pipe")
    genera_output_flange()

# === OUTPUT FINALE ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")