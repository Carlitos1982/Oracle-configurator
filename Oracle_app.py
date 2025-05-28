import streamlit as st
import pandas as pd

# Configura la pagina
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# Stile grafico e layout 3 colonne con sfondo
st.markdown("""
    <style>
    body {
        background-color: #eef2f7;
    }

    .main > div {
        display: flex;
        gap: 1rem;
    }

    .block-container {
        padding-top: 1rem;
    }

    section.main div[data-testid="column"] {
        position: relative;
    }

    section.main div[data-testid="column"]:nth-of-type(1)::after {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 2px;
        height: 100%;
        background-color: #aaa;
    }

    section.main div[data-testid="column"]:nth-of-type(2) {
        background-color: #f9f9f9;
        padding-left: 1.5rem;
    }

    h3 {
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Titolo dell'app
st.title("Oracle Item Setup - Web App")

# Caricamento dati di configurazione
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

# Carica i dati
data = load_config_data()
size_df = data["size_df"]
features_df = data["features_df"]
materials_df = data["materials_df"]

# Liste per dropdown
material_types = materials_df["Material Type"].dropna().unique().tolist()
pump_models = size_df["Pump Model"].dropna().unique().tolist()

# Elenco delle parti configurabili
part_options = [
    "Baseplate, Pump",
    "Casing, Pump",
    "Casing Cover, Pump",
    "Impeller, Pump",
    "Shaft, Pump",
    "Flange, Pipe",
    "Gasket, Spiral Wound",
    "Gasket, Flat",
    "Bolt, Hexagonal",
    "Gusset, Other",
    "Nut, Hex",
    "Stud, Threaded",
    "Ring, Wear"
]

# Selettore di parte
selected_part = st.selectbox("Seleziona il tipo di parte da configurare:", part_options)

if selected_part == "Gasket, Flat":
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("### 🛠️ Input")
        st.markdown("---")

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
        st.markdown("### 📤 Output")
        st.markdown("---")

        if "output_data" in st.session_state:
            for campo in [
                "Item", "Description", "Identificativo", "Classe ricambi", "Categories", "Catalog",
                "Disegno", "Material", "FPD material code", "Template", "ERP_L1", "ERP_L2",
                "To supplier", "Quality"
            ]:
                valore = st.session_state["output_data"].get(campo, "")
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

    with col3:
        st.markdown("### 🧾 DataLoad")
        st.markdown("---")
        st.text_input("Item Number (esistente o nuovo)", "")
        st.text_area("Stringa per DataLoad", value="(In arrivo…)", height=200)
        st.empty()  # Riempitivo per allineare