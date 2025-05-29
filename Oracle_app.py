import streamlit as st
import pandas as pd
from PIL import Image

# --- Configurazione pagina ---
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- CSS personalizzato ---
st.markdown("""
    <style>
    body {
        background-color: #e0ecf8 !important;
    }
    .block-container {
        background-color: white !important;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0,0,0,0.15);
    }
    section.main div[data-testid="column"] {
        position: relative;
    }
    section.main div[data-testid="column"]:nth-of-type(2) {
        background-color: #f0f7fc;
        padding-left: 1.5rem;
        border-left: 2px solid #ccc;
        border-radius: 0 10px 10px 0;
    }
    h3 {
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Loghi e titolo ---
# --- Loghi e titolo (allineati a sinistra) ---
st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 20px;
        padding-bottom: 1rem;
    ">
        <img
            src="https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/assets/IMG_1456.png"
            alt="Flowserve Logo"
            style="height: 80px; object-fit: contain;"
        >
        <h1 style="margin: 0; font-size: 2.5rem;">
            Oracle Item Setup - Web App
        </h1>
        <img
            src="https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/assets/IMG_1455.png"
            alt="Oracle Logo"
            style="height: 80px; object-fit: contain;"
        >
    </div>
    """,
    unsafe_allow_html=True
)

# --- Caricamento dati da Excel ---
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df     = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df= pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(
        subset=["Material Type", "Prefix", "Name"]
    ).reset_index(drop=True)
    return {
        "size_df":      size_df,
        "features_df":  features_df,
        "materials_df": materials_df
    }

data = load_config_data()
size_df      = data["size_df"]
features_df  = data["features_df"]
materials_df = data["materials_df"]
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- Selezione parte ---
part_options   = ["Gasket, Flat"]
selected_part  = st.selectbox("Seleziona il tipo di parte da configurare:", part_options)

# --- Logica per “Gasket, Flat” ---
if selected_part == "Gasket, Flat":
    st.markdown("---")
    col1, col2, col3 = st.columns([1,1,1])

    # --- Colonna 1: Input ---
    with col1:
        st.markdown("### 🛠️ Input")
        st.markdown("---")
        thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f", key="flat_thk")
        uom       = st.selectbox("UOM", ["mm", "inches"], key="flat_uom")
        dwg       = st.text_input("Dwg/doc number", key="flat_dwg")
        mtype     = st.selectbox("Material Type", [""] + material_types, key="flat_mtype")

        pref_df = materials_df[
            (materials_df["Material Type"] == mtype) &
            (materials_df["Prefix"].notna())
        ]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix  = st.selectbox("Material Prefix", [""] + prefixes, key="flat_mprefix")

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
                match      = materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Prefix"] == mprefix) &
                    (materials_df["Name"] == mname)
                ]
            else:
                materiale = mname
                match      = materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Name"] == mname)
                ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
            descr      = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {materiale}"

            st.session_state["output_data"] = {
                "Item":               "50158…",
                "Description":        descr,
                "Identificativo":     "4590-GASKET",
                "Classe ricambi":     "1-2-3",
                "Categories":         "FASCIA ITE 5",
                "Catalog":            "ARTVARI",
                "Disegno":            dwg,
                "Material":           materiale,
                "FPD material code":  codice_fpd,
                "Template":           "FPD_BUY_2",
                "ERP_L1":             "55_GASKETS_OR_SEAL",
                "ERP_L2":             "20_OTHER",
                "To supplier":        "",
                "Quality":            ""
            }

    # --- Colonna 2: Output ---
    with col2:
        st.markdown("### 📤 Output")
        st.markdown("---")
        if "output_data" in st.session_state:
            for campo in [
                "Item", "Description", "Identificativo", "Classe ricambi",
                "Categories", "Catalog", "Disegno", "Material",
                "FPD material code", "Template", "ERP_L1", "ERP_L2",
                "To supplier", "Quality"
            ]:
                valore = st.session_state["output_data"].get(campo, "")
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

    # --- Colonna 3: DataLoad ---
    with col3:
        st.markdown("### 🧾 DataLoad")
        st.markdown("---")
        dataload_mode = st.radio(
            "Modalità operazione",
            options=["Creazione item", "Aggiornamento item"],
            index=0,
            horizontal=True
        )
        item_code = st.text_input("Item Number", placeholder="Es. 50158-0001", key="item_code_input")

        dataload_string = ""
        if "output_data" in st.session_state and item_code:
            data = st.session_state["output_data"]
            if dataload_mode == "Creazione item":
                dataload_string = (
                    f"{item_code}\t{data['Description']}\t{data['Template']}\t"
                    f"{data['Identificativo']}\t{data['ERP_L1']}\t{data['ERP_L2']}\t"
                    f"{data['Catalog']}\t{data['Material']}\t{data['FPD material code']}"
                )
            else:
                dataload_string = (
                    f"{item_code}\tAggiorna:\t{data['Description']}\t"
                    f"{data['Material']}\t{data['FPD material code']}"
                )

        st.text_area("Stringa per DataLoad", value=dataload_string, height=200)