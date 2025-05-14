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

part_options = ["Casing, Pump", "Casing Cover, Pump"]
selected_part = st.selectbox("Seleziona Parte", part_options)

pump_models = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

# === BLOCCO: CASING, PUMP ===
if selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")

    model = st.selectbox("Product/Pump Model", [""] + pump_models)
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list)

    feature1_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features1")]["Feature"].dropna().tolist()
    feature2_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features2")]["Feature"].dropna().tolist()

    feature_1 = st.selectbox("Additional Feature 1", [""] + feature1_list)
    feature_2 = st.selectbox("Additional Feature 2", [""] + feature2_list if feature2_list else [""])

    note = st.text_area("Note (opzionale)", height=80)
    dwg = st.text_input("Dwg/doc number")

    mtype = st.selectbox("Material Type", [""] + material_types)
    prefix_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefix_list = sorted(prefix_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefix_list)

    if mtype == "MISCELLANEOUS":
        name_list = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        name_list = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
    mname = st.selectbox("Material Name", [""] + name_list)

    madd = st.text_input("Material add. Features (opzionale)")

    if st.button("Genera Output"):
        materiale = f"{mtype} {mname}" if mtype == "MISCELLANEOUS" else f"{mtype} {mprefix} {mname}"
        materiale = materiale.strip()

        match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix) & (materials_df["Name"] == mname)]
        codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

        materiale_descr = " ".join(filter(None, [mtype, mprefix, mname, madd]))
        descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note, materiale_descr]))

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

# === BLOCCO: CASING COVER, PUMP ===
elif selected_part == "Casing Cover, Pump":
    st.subheader("Configurazione - Casing Cover, Pump")

    model = st.selectbox("Product/Pump Model", [""] + pump_models, key="model_cover")
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list, key="size_cover")

    feature1_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features1")]["Feature"].dropna().tolist()
    feature2_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features2")]["Feature"].dropna().tolist()

    feature_1 = st.selectbox("Additional Feature 1", [""] + feature1_list, key="f1_cover")
    feature_2 = st.selectbox("Additional Feature 2", [""] + feature2_list if feature2_list else [""], key="f2_cover")

    note = st.text_area("Note (opzionale)", height=80, key="note_cover")
    dwg = st.text_input("Dwg/doc number", key="dwg_cover")

    make_or_buy = st.radio("Make or Buy", ["Make", "Buy"], horizontal=True, key="mob_cover")

    mtype = st.selectbox("Material Type", [""] + material_types, key="mtype_cover")
    prefix_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefix_list = sorted(prefix_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefix_list, key="mprefix_cover")

    if mtype == "MISCELLANEOUS":
        name_list = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        name_list = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
    mname = st.selectbox("Material Name", [""] + name_list, key="mname_cover")

    madd = st.text_input("Material add. Features (opzionale)", key="madd_cover")

    if st.button("Genera Output", key="gen_cover"):
        materiale = f"{mtype} {mname}" if mtype == "MISCELLANEOUS" else f"{mtype} {mprefix} {mname}"
        materiale = materiale.strip()

        match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix) & (materials_df["Name"] == mname)]
        codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

        materiale_descr = " ".join(filter(None, [mtype, mprefix, mname, madd]))
        descrizione = "Casing Cover, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note, materiale_descr]))

        template = "FPD_MAKE" if make_or_buy == "Make" else "FPD_BUY_1"

        st.session_state["output_data"] = {
            "Item": "4020...",
            "Description": descrizione,
            "Identificativo": "1221-CASING COVER",
            "Classe ricambi": "3",
            "Categories": "Fascia ite 4",
            "Catalog": "COPERCHIO",
            "Disegno": dwg,
            "Material": materiale,
            "FPD material code": codice_fpd,
            "Template": template,
            "ERP_L1": "20_TURNKEY_MACHINING",
            "ERP_L2": "13_OTHER",
            "To supplier": "",
            "Quality": ""
        }

# === OUTPUT FINALE ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")

    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")