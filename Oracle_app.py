
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

# ROUTING PRINCIPALE
if selected_part == "Flange, Pipe":
    st.subheader("Configurazione - Flange, Pipe")

    flange_type = st.selectbox("Type", ["SW", "BW"])
    size = st.selectbox("Size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    face_type = st.selectbox("Face Type", ["RF", "FF", "RJ"])
    flange_class = st.selectbox("Class", ["150", "300", "600", "1500", "2500"])
    schedule = st.selectbox("Schedula", ["5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160"])
    flange_material = st.selectbox("Flange Material", [
        "A105", "A106-GR B", "UNS-S31803", "UNS-S32760", "A350 LF2", "A182-F316L",
        "ALLOY 825", "GALVANIZED CARBON STEEL"
    ])
    note = st.text_area("Note (opzionale)", height=80)

    if st.button("Genera Output", key="gen_flange"):
        descrizione = (
            f"FLANGE, PIPE - TYPE: {flange_type}, SIZE: {size}, FACE TYPE: {face_type}, "
            f"CLASS: {flange_class}, SCHEDULA: {schedule}, MATERIAL: {flange_material}"
        )
        if note:
            descrizione += f", NOTE: {note}"

        st.session_state["output_data"] = {
            "Item": "50155…",
            "Description": descrizione,
            "Identificativo": "1245-FLANGE",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": "NOT AVAILABLE",
            "FPD material code": "BO-NA",
            "Template": "FPD_BUY_2",
            "ERP_L1": "23_FLANGE",
            "ERP_L2": "13_OTHER",
            "To supplier": "",
            "Quality": ""
        }

# OUTPUT FINALE
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")
