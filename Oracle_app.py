import streamlit as st
import pandas as pd

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === CARICA DATI DA EXCEL SU GITHUB ===
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

# === INTERFACCIA CONFIGURATORE ===
part_options = ["Casing, Pump"]
selected_part = st.selectbox("Seleziona Parte", part_options)

if selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")

    pump_models = sorted(size_df["Pump Model"].dropna().unique())
    model = st.selectbox("Product/Pump Model", [""] + list(pump_models))

    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list)

    feature1_list = features_df[
        (features_df["Pump Model"] == model) & 
        (features_df["Feature Type"] == "features1")
    ]["Feature"].dropna().tolist()

    feature2_list = features_df[
        (features_df["Pump Model"] == model) & 
        (features_df["Feature Type"] == "features2")
    ]["Feature"].dropna().tolist()

    feature_1 = st.selectbox("Additional Feature 1", [""] + feature1_list)
    feature_2 = st.selectbox("Additional Feature 2", [""] + feature2_list if feature2_list else [""])

    note = st.text_area("Note (opzionale)", height=80)
    dwg = st.text_input("Dwg/doc number")

    material_types = materials_df["Material Type"].dropna().unique().tolist()
    mtype = st.selectbox("Material Type", [""] + material_types)

    prefix_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefix_list = sorted(prefix_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefix_list)

    if mtype == "MISCELLANEOUS":
        name_list = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        name_list = materials_df[
            (materials_df["Material Type"] == mtype) & 
            (materials_df["Prefix"] == mprefix)
        ]["Name"].dropna().tolist()
    mname = st.selectbox("Material Name", [""] + name_list)

    madd = st.text_input("Material add. Features (opzionale)")

    if st.button("Genera Output"):
        # === COMBINA IL MATERIALE ===
        if mtype == "MISCELLANEOUS":
            materiale = f"{mtype} {mname}".strip()
        else:
            materiale = f"{mtype} {mprefix} {mname}".strip()
        if madd:
            materiale += f" {madd}"

        # === CERCA IL FPD MATERIAL CODE ===
        match = materials_df[
            (materials_df["Material Type"] == mtype) &
            (materials_df["Prefix"] == mprefix) &
            (materials_df["Name"] == mname)
        ]
        codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

        # === DESCRIZIONE COMPLETA ===
        descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note]))

        # === OUTPUT COMPLETO ===
        st.session_state["output_data"] = {
            "Item": "40202...",
            "Description": descrizione,
            "Identificativo": "1100-CASING",
            "Classe ricambi": "3",
            "Categories": "Fascia ite 4",
            "Catalog": "CORPO",
            "Disegno": dwg,
            "Material": materiale,
            "FPD material code": codice_fpd,
            "Template": "FPD_MAKE",
            "ERP_L1": "20_TURNKEY_MACHINING",
            "ERP_L2": "17_CASING",
            "To supplier": "",
            "Quality": ""
        }

# === RISULTATO FINALE ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")

    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")