
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
    "Flange, Pipe",
    "Gasket, Spiral Wound"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# === SEZIONE GASKET ===
if selected_part == "Gasket, Spiral Wound":
    st.subheader("Configurazione - Gasket, Spiral Wound")

    winding_material = st.selectbox("Winding material", [
        "304 stainless steel", "316L stainless steel", "317L stainless steel", "321 stainless steel",
        "347 stainless steel", "MONEL", "Nickel", "Titanium", "Alloy20", "INCONEL 600", "HASTELLOY B",
        "HASTELLOY C", "INCOLOY800", "DUPLEX", "SUPERDUPLEX", "ALLOY 825", "UNS S31254",
        "ZYRCONIUM 702", "INCONEL X750HT"
    ])

    filler = st.selectbox("Filler", ["Graphite", "PTFE", "Ceramic", "Verdicarb (Mica Graphite)"])

    inner_dia = st.number_input("Diametro interno (mm)", min_value=0.0, step=0.1, format="%.1f", key="in_dia_gasket")
    outer_dia = st.number_input("Diametro esterno (mm)", min_value=0.0, step=0.1, format="%.1f", key="out_dia_gasket")
    thickness = st.number_input("Spessore (mm)", min_value=0.0, step=0.1, format="%.1f", key="thk_gasket")

    rating = st.selectbox("Rating", [
        "STANDARD PRESSURE m=3 y=10000 psi",
        "HIGH PRESSURE m=3 y=17500 psi",
        "ULTRA HIGH PRESSURE m=3 y=23500 psi"
    ])

    dwg = st.text_input("Dwg/doc number", key="dwg_gasket")
    note = st.text_area("Note (opzionale)", height=80, key="note_gasket")

    if st.button("Genera Output", key="gen_gasket"):
        descrizione = "GASKET, SPIRAL WOUND - [descrizione da completare]"

        st.session_state["output_data"] = {
            "Item": "50415…",
            "Description": descrizione,
            "Identificativo": "4510-JOINT",
            "Classe ricambi": "1-2-3",
            "Categories": "FASCIA ITE 5",
            "Catalog": "ARTVARI",
            "Disegno": dwg,
            "Material": "NA",
            "FPD material code": "NOT AVAILABLE",
            "Template": "FPD_BUY_1",
            "ERP_L1": "55_GASKETS_OR_SEAL",
            "ERP_L2": "16_SPIRAL_WOUND",
            "To supplier": "",
            "Quality": ""
        }

# === OUTPUT GENERICO ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")
