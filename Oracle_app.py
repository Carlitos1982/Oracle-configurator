import streamlit as st
import pandas as pd
from PIL import Image

# --- 1) Configurazione pagina wide
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- 2) Header con titolo a sinistra e logo Flowserve a destra
flowserve_logo = Image.open("assets/IMG_1456.png")
col_header, col_spacer, col_logo = st.columns([3, 4, 1], gap="small")
with col_header:
    st.markdown("# Oracle Item Setup - Web App")
with col_spacer:
    st.empty()
with col_logo:
    st.image(flowserve_logo, width=100)

st.markdown("---")

# --- 3) Caricamento dati da Excel
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- 4) Selezione parte
part = st.selectbox("Seleziona il tipo di parte da configurare:", ["Gasket, Flat"])
st.markdown("---")

# --- 5) Layout 3 colonne
col1, col2, col3 = st.columns(3)

# ---- COLONNA 1: INPUT
with col1:
    st.subheader("🛠️ Input")
    thickness = st.number_input("Thickness (mm)", min_value=0.0, step=0.1, key="thk")
    uom = st.selectbox("UOM", ["mm", "inches"], key="uom")
    dwg = st.text_input("Dwg/doc number", key="dwg")
    mtype = st.selectbox("Material Type", [""] + material_types, key="mtype")

    df_pref = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefixes = sorted(df_pref["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix")

    if mtype == "MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        names = (
            materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        )
    mname = st.selectbox("Material Name", [""] + names, key="mname")

    if st.button("Genera Output", key="gen"):
        st.session_state["output"] = {}

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

        st.session_state["output"] = {
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

# ---- COLONNA 2: OUTPUT
with col2:
    st.subheader("📤 Output")
    if "output" in st.session_state:
        for k, v in st.session_state.output.items():
            if k == "Description":
                st.text_area(k, value=v, height=80)
            else:
                st.text_input(k, value=v)

# ---- COLONNA 3: DATALOAD
with col3:
    st.subheader("📥 DataLoad")

    dataload_mode = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="dataload_mode")
    item_code_input = st.text_input("Codice item", key="item_code")

    if "output" in st.session_state:
        data = st.session_state["output"]

        def get_val(key):
            val = data.get(key, "").strip()
            return val if val else "."

        if dataload_mode == "Crea nuovo item":
            dataload_string = (
                "\\%FN\n"
                f"{item_code_input if item_code_input else get_val('Item')}\n"
                "\\%TC\n"
                f"{get_val('Template')}\n"
                "TAB\n"
                "\\%D\n"
                "\\%O\n"
                "TAB\n"
                f"{get_val('Description')}\n"
                "TAB\nTAB\nTAB\nTAB\nTAB\nTAB\n"
                f"{get_val('Identificativo')}\n"
                "TAB\n"
                f"{get_val('Classe ricambi')}\n"
                "TAB\n"
                "\\%O\n"
                "\\^S\n"
                "\\%TA\n"
                "TAB\n"
                f"{get_val('ERP_L1')}.{get_val('ERP_L2')}\n"
                "TAB\nFASCIA ITE\n"
                "TAB\n"
                f"{get_val('Categories').split()[-1]}\n"
                "\\^S\n\\^{F4}\n"
                "\\%TG\n"
                f"{get_val('Catalog')}\n"
                "TAB\nTAB\nTAB\n"
                f"{get_val('Disegno')}\n"
                "TAB\n\\^S\n\\^{F4}\n"
                "\\%TR\n"
                "MATER+DESCR_FPD\n"
                "TAB\nTAB\n"
                f"{get_val('FPD material code')}\n"
                "TAB\n"
                f"{get_val('Material')}\n"
                "\\^S\n\\^{F4}\n"
                "\\%VA\n"
                "TAB\n"
                f"{get_val('Quality')}\n"
                "TAB\nTAB\nTAB\nTAB\n"
                f"{get_val('Quality') if get_val('Quality') != '.' else '.'}\n"
                "\\^S\n"
                "\\%FN\n"
                "TAB\n"
                f"{get_val('To supplier')}\n"
                "TAB\nTAB\nTAB\n"
                "Short Text\n"
                "TAB\n"
                f"{get_val('To supplier') if get_val('To supplier') != '.' else '.'}\n"
                "\\^S\n\\^S\n\\^{F4}\n\\^S"
            )

            st.text_area("Stringa per DataLoad (creazione)", dataload_string, height=400)

# --- Footer
st.markdown("---")
st.markdown("<div style='text-align:center;'><small>v1.0 • © 2025 Flowserve Desio Order Engineering</small></div>", unsafe_allow_html=True)
st.markdown("""
<div style="
    background-color:#f9f9f9;
    padding:0.8rem;
    border-radius:8px;
    text-align:center;
    font-size:0.9rem;
    color:#555;
    margin-top:1rem;
">
    Created by <strong>dzecchinel</strong> • (mailto:dzecchinel@gmail.com)
</div>
""", unsafe_allow_html=True)
