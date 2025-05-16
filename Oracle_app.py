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

        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")

if selected_part == "Flange, Pipe":
    st.subheader("Configurazione - Flange, Pipe")
    genera_output("flange", "50155…", "1245-FLANGE", "", "", "13_OTHER")

elif selected_part == "Baseplate, Pump":
    st.subheader("Configurazione - Baseplate, Pump")
    genera_output(parte="baseplate", item="477...", identificativo="6110-BASE PLATE", classe="", catalog="ARTVARI", erp_l2="18_FOUNDATION PLATE", extra_fields="baseplate")

elif selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")
    genera_output(parte="casing", item="40202...", identificativo="1100-CASING", classe="3", catalog="CORPO", erp_l2="17_CASING", template_fisso="FPD_MAKE")

elif selected_part == "Casing Cover, Pump":
    st.subheader("Configurazione - Casing Cover, Pump")
    genera_output(parte="cover", item="40205...", identificativo="1221-CASING COVER", classe="3", catalog="COPERCHIO", erp_l2="13_OTHER")

elif selected_part == "Impeller, Pump":
    st.subheader("Configurazione - Impeller, Pump")
    genera_output(parte="imp", item="40229...", identificativo="2200-IMPELLER", classe="2-3", catalog="GIRANTE", erp_l2="20_IMPELLER_DIFFUSER", template_fisso="FPD_MAKE")

elif selected_part == "Balance Bushing, Pump":
    st.subheader("Configurazione - Balance Bushing, Pump")
    genera_output(parte="balance", item="40226...", identificativo="6231-BALANCE DRUM BUSH", classe="1-2-3", catalog="ALBERO", erp_l2="16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Drum, Pump":
    st.subheader("Configurazione - Balance Drum, Pump")
    genera_output(parte="drum", item="40227...", identificativo="6231-BALANCE DRUM BUSH", classe="1-2-3", catalog="ARTVARI", erp_l2="16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Disc, Pump":
    st.subheader("Configurazione - Balance Disc, Pump")
    genera_output(parte="disc", item="40228...", identificativo="6210-BALANCE DISC", classe="1-2-3", catalog="ARTVARI", erp_l2="30_DISK", extra_fields="diameters")

elif selected_part == "Shaft, Pump":
    st.subheader("Configurazione - Shaft, Pump")
    genera_output(parte="shaft", item="40231...", identificativo="2100-SHAFT", classe="2-3", catalog="ALBERO", erp_l2="25_SHAFTS", template_fisso="FPD_MAKE", extra_fields="shaft")


        else:
            st.text_input(campo, value=valore, key=f"out_{campo}"

)

if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")