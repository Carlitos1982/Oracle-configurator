import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

# --- Configurazione pagina wide
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- Header con titolo e logo Flowserve
flowserve_logo = Image.open("assets/IMG_1456.png")
col_header, col_spacer, col_logo = st.columns([3, 4, 1], gap="small")
with col_header:
    st.markdown("# Oracle Item Setup - Web App")
with col_logo:
    st.image(flowserve_logo, width=100)

st.markdown("---")

# --- Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df      = pd.read_excel(xls, sheet_name="Pump Size")
    features_df  = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# Lista completa delle parti
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
    "Gate, Valve",
    "Gasket, Spiral Wound",
    "Gasket, Flat",
    "Bearing, Hydrostatic/Hydrodynamic",
    "Bearing, Rolling",
    "Bolt, Eye",
    "Bolt, Hexagonal",
    "Gasket, Ring Type Joint",
    "Gusset, Other",
    "Nut, Hex",
    "Stud, Threaded",
    "Ring, Wear",
    "Pin, Dowel",
    "Screw, Cap",
    "Screw, Grub"
]

# Selezione parte
selected_part = st.selectbox("Seleziona Parte", part_options)
st.markdown("---")

# -----------------------
# Ogni blocco: 3 colonne
# -----------------------

# --- BASEPLATE, PUMP
if selected_part == "Baseplate, Pump":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        length_bp      = st.number_input("Length (mm)", min_value=0.0, step=1.0, key="bp_length")
        width_bp       = st.number_input("Width (mm)", min_value=0.0, step=1.0, key="bp_width")
        weight_bp      = st.number_input("Weight (kg)", min_value=0.0, step=1.0, key="bp_weight")
        sourcing_bp    = st.selectbox("Sourcing", ["Europe", "India", "China"], key="bp_sourcing")
        dwg_bp         = st.text_input("Dwg/doc number", key="bp_dwg")
        note_bp        = st.text_area("Note (opzionale)", height=80, key="bp_note")
        mtype_bp       = st.selectbox("Material Type", [""] + material_types, key="bp_mtype")
        df_pref_bp = materials_df[
            (materials_df["Material Type"] == mtype_bp) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bp = sorted(df_pref_bp["Prefix"].unique()) if mtype_bp != "MISCELLANEOUS" else []
        mprefix_bp  = st.selectbox("Material Prefix", [""] + prefixes_bp, key="bp_mprefix")
        if mtype_bp == "MISCELLANEOUS":
            names_bp = materials_df[
                materials_df["Material Type"] == mtype_bp
            ]["Name"].dropna().tolist()
        else:
            names_bp = materials_df[
                (materials_df["Material Type"] == mtype_bp) &
                (materials_df["Prefix"] == mprefix_bp)
            ]["Name"].dropna().tolist()
        mname_bp = st.selectbox("Material Name", [""] + names_bp, key="bp_mname")
        if st.button("Genera Output", key="gen_bp"):
            materiale_bp = (
                f"{mtype_bp} {mprefix_bp} {mname_bp}".strip()
                if mtype_bp != "MISCELLANEOUS" else mname_bp
            )
            match_bp = materials_df[
                (materials_df["Material Type"] == mtype_bp) &
                (materials_df["Prefix"] == mprefix_bp) &
                (materials_df["Name"] == mname_bp)
            ]
            codice_fpd_bp = match_bp["FPD Code"].values[0] if not match_bp.empty else ""
            descr_bp = (
                f"BASEPLATE, PUMP - L:{int(length_bp)}mm, W:{int(width_bp)}mm, Wt:{weight_bp}kg, "
                f"Sourcing: {sourcing_bp}, Material: {materiale_bp}"
            )
            if note_bp:
                descr_bp += f", NOTE: {note_bp}"
            st.session_state["output_data"] = {
                "Item": "477…",
                "Description": descr_bp,
                "Identificativo": "6110-BASE PLATE",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_bp,
                "Material": materiale_bp,
                "FPD material code": codice_fpd_bp,
                "Template": "FPD_BUY_4",
                "ERP_L1": "21_FABRICATIONS_OR_BASEPLATES",
                "ERP_L2": "18_FOUNDATION_PLATE",
                "To supplier": "",
                "Quality": ""
            }
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bp_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bp_{campo}")
    with col3:
        st.subheader("🧾 DataLoad")
