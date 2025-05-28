import streamlit as st
import pandas as pd

# Configura la pagina
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# Applica lo stile personalizzato alle colonne
st.markdown("""
    <style>
    .main > div {
        display: flex;
        gap: 1rem;
    }
    .block-container {
        padding-top: 1rem;
    }
    div[data-testid="column"]:nth-of-type(1) {
        border-right: 2px solid #aaa;
        padding-right: 1.5rem;
    }
    div[data-testid="column"]:nth-of-type(2) {
        background-color: #f9f9f9;
        padding-left: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Titolo
st.title("Oracle Item Setup - Web App")

# Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")

    materials_df = materials_df.drop_duplicates(
        subset=["Material Type", "Prefix", "Name"]
    ).reset_index(drop=True)

    return {
        "size_df": size_df,
        "features_df": features_df,
        "materials_df": materials_df
    }

data = load_config_data()
size_df = data["size_df"]
features_df = data["features_df"]
materials_df = data["materials_df"]

# Liste base
part_options = ["Baseplate, Pump", "Casing, Pump", "Impeller, Pump"]  # esempio
material_types = materials_df["Material Type"].dropna().unique().tolist()
pump_models = sorted(size_df["Pump Model"].dropna().unique())

# Scelta parte
selected_part = st.selectbox("Seleziona Parte", part_options)

# Colonne layout
col1, col2 = st.columns([2, 1])


elif selected_part == "Gasket, Flat":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛠️ Input - Gasket, Flat")

        thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f", key="flat_thk")
        uom = st.selectbox("UOM", ["mm", "inches"], key="flat_uom")
        dwg = st.text_input("Dwg/doc number", key="flat_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="flat_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="flat_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="flat_mname")

        if st.button("Genera Output", key="gen_flat"):
            if mtype != "MISCELLANEOUS":
                materiale = f"{mtype} {mprefix} {mname}".strip()
                match = materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Prefix"] == mprefix) &
                    (materials_df["Name"] == mname)
                ]
            else:
                materiale = mname
                match = materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Name"] == mname)
                ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            descr = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {materiale}"

            st.session_state["output_data"] = {
                "Item": "50158…",
                "Description": descr,
                "Identificativo": "4590-GASKET",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
