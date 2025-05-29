import streamlit as st
import pandas as pd
from PIL import Image

# --- 1) Configurazione pagina wide ---
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- 2) CSS in-file per colori, font e bottone ---
st.markdown("""
<style>
  html, body {
    background-color: #e0ecf8 !important;
    font-family: 'Sans-Serif', Arial !important;
  }
  h1, h2 {
    font-weight: 700 !important;
    color: #1a1a1a !important;
  }
  .stButton>button {
    background-color: #d21f2d !important;
    color: white !important;
    border-radius: 5px !important;
    padding: 0.6em 1.2em !important;
  }
  .stButton>button:hover {
    background-color: #b41c29 !important;
  }
  .block-container {
    background-color: white !important;
    padding: 2rem !important;
    border-radius: 10px !important;
    box-shadow: 0 0 15px rgba(0,0,0,0.15) !important;
  }
  section.main div[data-testid="column"]:nth-of-type(2) {
    background-color: #f0f7fc !important;
    padding-left: 1.5rem !important;
    border-left: 2px solid #ccc !important;
    border-radius: 0 10px 10px 0 !important;
  }
</style>
""", unsafe_allow_html=True)

# --- 3) Header con titolo a sinistra e logo Flowserve a destra ---
flowserve_logo = Image.open("assets/IMG_1456.png")
col_title, col_logo = st.columns([3,1], gap="small")
with col_title:
    st.markdown("# Oracle Item Setup - Web App")
with col_logo:
    st.image(flowserve_logo, width=100)
st.markdown("---")

# --- 4) Caricamento dati da Excel ---
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df      = pd.read_excel(xls, sheet_name="Pump Size")
    features_df  = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type","Prefix","Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- 5) Selezione parte da configurare ---
part = st.selectbox("Seleziona il tipo di parte da configurare:", ["Gasket, Flat"])
st.markdown("---")

# --- 6) Layout a tre colonne ---
col1, col2, col3 = st.columns(3)

# ---- COLONNA 1: INPUT ----
with col1:
    st.markdown("## 🛠️ Input")
    thickness = st.number_input("Thickness (mm)", min_value=0.0, step=0.1, key="thk")
    uom       = st.selectbox("UOM", ["mm","inches"], key="uom")
    dwg       = st.text_input("Dwg/doc number", key="dwg")
    mtype     = st.selectbox("Material Type", [""] + material_types, key="mtype")

    df_pref = materials_df[
        (materials_df["Material Type"] == mtype) &
        (materials_df["Prefix"].notna())
    ]
    prefixes = sorted(df_pref["Prefix"].unique()) if mtype!="MISCELLANEOUS" else []
    mprefix  = st.selectbox("Material Prefix", [""]+prefixes, key="mprefix")

    if mtype=="MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"]==mtype]["Name"].dropna().tolist()
    else:
        names = (
            materials_df[
                (materials_df["Material Type"]==mtype)&
                (materials_df["Prefix"]==mprefix)
            ]["Name"]
            .dropna()
            .tolist()
        )
    mname = st.selectbox("Material Name", [""]+names, key="mname")

    if st.button("Genera Output", key="gen"):
        # costruzione stringhe
        if mtype!="MISCELLANEOUS":
            materiale = f"{mtype} {mprefix} {mname}".strip()
            match     = materials_df[
                (materials_df["Material Type"]==mtype)&
                (materials_df["Prefix"]==mprefix)&
                (materials_df["Name"]==mname)
            ]
        else:
            materiale = mname
            match     = materials_df[
                (materials_df["Material Type"]==mtype)&
                (materials_df["Name"]==mname)
            ]
        codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
        descr      = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {materiale}"

        st.session_state.output = {
            "Item":              "50158…",
            "Description":       descr,
            "Identificativo":    "4590-GASKET",
            "Classe ricambi":    "1-2-3",
            "Categories":        "FASCIA ITE 5",
            "Catalog":           "ARTVARI",
            "Disegno":           dwg,
            "Material":          materiale,
            "FPD material code": codice_fpd,
            "Template":          "FPD_BUY_2",
            "ERP_L1":            "55_GASKETS_OR_SEAL",
            "ERP_L2":            "20_OTHER",
            "To supplier":       "",
            "Quality":           ""
        }
        st.success("✅ Output generato con successo!")

# ---- COLONNA 2: OUTPUT ----
with col2:
    st.markdown("## 📤 Output")
    if "output" in st.session_state:
        for k, v in st.session_state.output.items():
            if k=="Description":
                st.text_area(k, value=v, height=80)
            else:
                st.text_input(k, value=v)

# ---- COLONNA 3: DATALOAD ----
with col3:
    st.markdown("## 🧾 DataLoad")
    mode      = st.radio("Operazione", ["Creazione item","Aggiornamento item"], index=0, horizontal=True)
    item_code = st.text_input("Item Number", placeholder="Es. 50158-0001", key="item_code")
    dl = ""
    if "output" in st.session_state and item_code:
        out = st.session_state.output
        if mode=="Creazione item":
            dl = (
                f"{item_code}\t{out['Description']}\t{out['Template']}\t"
                f"{out['Identificativo']}\t{out['ERP_L1']}\t{out['ERP_L2']}\t"
                f"{out['Catalog']}\t{out['Material']}\t{out['FPD material code']}"
            )
        else:
            dl = (
                f"{item_code}\tAggiornamento:\t{out['Description']}\t"
                f"{out['Material']}\t{out['FPD material code']}"
            )
    st.text_area("Stringa per DataLoad", value=dl, height=150)

# --- 7) Footer minimale ---
st.markdown("---")
st.markdown("<div style='text-align:center;'><small>v1.0 • © 2025 Flowserve Engineering</small></div>", unsafe_allow_html=True)