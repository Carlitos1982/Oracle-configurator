import streamlit as st
import pandas as pd
from PIL import Image

# --- Configurazione pagina wide ---
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- (Opzionale) solo sfondo pagina ---
st.markdown("""
    <style>
      body {
        background-color: #e0ecf8 !important;
      }
    </style>
""", unsafe_allow_html=True)

# --- Header con logo e titolo, 2 colonne ---
flowserve_logo = Image.open("assets/IMG_1456.png")

col_left, col_right = st.columns([4, 1], gap="small")
with col_left:
    st.title("Oracle Item Setup - Web App")
with col_right:
    st.image(flowserve_logo, width=150, use_column_width=False)

st.markdown("---")

# --- Caricamento dati da Excel ---
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df      = pd.read_excel(xls, sheet_name="Pump Size")
    features_df  = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type","Prefix","Name"]).reset_index(drop=True)
    return {"size_df":size_df, "features_df":features_df, "materials_df":materials_df}

data           = load_config_data()
size_df        = data["size_df"]
features_df    = data["features_df"]
materials_df   = data["materials_df"]
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- Selezione parte da configurare ---
part_options  = ["Gasket, Flat"]
selected_part = st.selectbox("Seleziona il tipo di parte da configurare:", part_options)

# --- Logica per “Gasket, Flat” ---
if selected_part == "Gasket, Flat":
    col1, col2, col3 = st.columns([1,1,1])

    # INPUT
    with col1:
        st.header("🛠️ Input")
        thickness = st.number_input("Thickness (mm)", min_value=0.0, step=0.1, key="flat_thk")
        uom       = st.selectbox("UOM", ["mm","inches"], key="flat_uom")
        dwg       = st.text_input("Dwg/doc number", key="flat_dwg")
        mtype     = st.selectbox("Material Type", [""]+material_types, key="flat_mtype")

        pref_df  = materials_df[
            (materials_df["Material Type"]==mtype)&
            (materials_df["Prefix"].notna())
        ]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype!="MISCELLANEOUS" else []
        mprefix  = st.selectbox("Material Prefix", [""]+prefixes, key="flat_mprefix")

        if mtype=="MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"]==mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"]==mtype)&
                (materials_df["Prefix"]==mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""]+names, key="flat_mname")

        if st.button("Genera Output", key="gen_flat"):
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
            st.session_state["output_data"] = {
                "Item":"50158…","Description":descr,
                "Identificativo":"4590-GASKET","Classe ricambi":"1-2-3",
                "Categories":"FASCIA ITE 5","Catalog":"ARTVARI","Disegno":dwg,
                "Material":materiale,"FPD material code":codice_fpd,
                "Template":"FPD_BUY_2","ERP_L1":"55_GASKETS_OR_SEAL",
                "ERP_L2":"20_OTHER","To supplier":"","Quality":""
            }

    # OUTPUT
    with col2:
        st.header("📤 Output")
        if "output_data" in st.session_state:
            for fld in [
                "Item","Description","Identificativo","Classe ricambi",
                "Categories","Catalog","Disegno","Material",
                "FPD material code","Template","ERP_L1","ERP_L2",
                "To supplier","Quality"
            ]:
                val = st.session_state["output_data"].get(fld,"")
                if fld=="Description":
                    st.text_area(fld, value=val, height=80)
                else:
                    st.text_input(fld, value=val)

    # DATALOAD
    with col3:
        st.header("🧾 DataLoad")
        mode      = st.radio("Operazione", ["Creazione item","Aggiornamento item"], index=0, horizontal=True)
        item_code = st.text_input("Item Number", placeholder="50158-0001", key="flat_item")

        dl = ""
        if "output_data" in st.session_state and item_code:
            d = st.session_state["output_data"]
            if mode=="Creazione item":
                dl = (
                    f"{item_code}\t{d['Description']}\t{d['Template']}\t"
                    f"{d['Identificativo']}\t{d['ERP_L1']}\t{d['ERP_L2']}\t"
                    f"{d['Catalog']}\t{d['Material']}\t{d['FPD material code']}"
                )
            else:
                dl = (
                    f"{item_code}\tAggiornamento:\t{d['Description']}\t"
                    f"{d['Material']}\t{d['FPD material code']}"
                )
        st.text_area("Stringa per DataLoad", value=dl, height=150)