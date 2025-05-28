
import streamlit as st
import pandas as pd

# Configurazione della pagina
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return materials_df

materials_df = load_config_data()

# Colori e stile CSS
st.markdown(
    """
    <style>
        body {
            background-color: #f2f2f2;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .title-row {
            border-top: 2px solid #ddd;
            border-bottom: 2px solid #ddd;
            padding: 1rem 0;
            margin-bottom: 1rem;
        }
        .input-column, .output-column, .dataload-column {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True
)

# Titolo
st.markdown("<h1 style='text-align: center;'>Oracle Item Setup - Web App</h1>", unsafe_allow_html=True)
selected_part = st.selectbox("Seleziona il tipo di parte da configurare:", ["Gasket, Flat"])

st.markdown("<div class='title-row'></div>", unsafe_allow_html=True)

# Suddivisione in tre colonne
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("### 🛠️ Input")
    thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f")
    uom = st.selectbox("UOM", ["mm", "inch"])
    dwg_number = st.text_input("Dwg/doc number")
    mat_type = st.selectbox("Material Type", materials_df["Material Type"].unique())
    mat_prefix = st.selectbox("Material Prefix", materials_df[materials_df["Material Type"] == mat_type]["Prefix"].unique())
    mat_name = st.selectbox("Material Name", materials_df[
        (materials_df["Material Type"] == mat_type) &
        (materials_df["Prefix"] == mat_prefix)
    ]["Name"].drop_duplicates())

    if st.button("Genera Output"):
        st.session_state['gen_output'] = True

with col2:
    st.markdown("### 📤 Output")
    if st.session_state.get('gen_output', False):
        item = "50158..."
        descr = f"GASKET, FLAT - THK: {thickness} {uom}, MATERIAL: {mat_name}"
        identificativo = "4590-GASKET"
        classe = "1-2-3"
        categoria = "FASCIA ITE 5"
        catalog = "ARTVARI"
        template = "FPD_BUY_2"
        erp_l1 = "55_GASKETS_OR_SEAL"
        erp_l2 = "20_OTHER"

        st.text_input("Item", value=item)
        st.text_area("Description", value=descr, height=60)
        st.text_input("Identificativo", value=identificativo)
        st.text_input("Classe ricambi", value=classe)
        st.text_input("Categories", value=categoria)
        st.text_input("Catalog", value=catalog)
        st.text_input("Material", value=mat_name)
        st.text_input("FPD material code", value="NOT AVAILABLE")
        st.text_input("Template", value=template)
        st.text_input("ERP L1", value=erp_l1)
        st.text_input("ERP L2", value=erp_l2)

with col3:
    st.markdown("### 🧾 DataLoad")
    mode = st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"])
    item_number = st.text_input("Item Number", placeholder="Es. 50158-0001")
    if st.session_state.get('gen_output', False):
        dataload_str = f"{descr}\nMATERIAL: {template}\n{erp_l1}\n{erp_l2}"
        st.text_area("Stringa per DataLoad", value=dataload_str, height=100)
