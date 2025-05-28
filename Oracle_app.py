import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# CSS per sfondo chiaro forzato e layout responsive
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
h1, h2, h3, h4, h5, h6, p, label, div, span, textarea, input, select {
    color: #000000 !important;
}
input, textarea, select {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #999 !important;
}
::placeholder {
    color: #666 !important;
    opacity: 1 !important;
}
.block-container {
    background-color: white !important;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 0 15px rgba(0,0,0,0.15);
}
section.main div[data-testid="column"]:nth-of-type(1)::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 2px;
    height: 100%;
    background-color: #ccc;
}
section.main div[data-testid="column"]:nth-of-type(2) {
    background-color: #f0f7fc;
    padding-left: 1.5rem;
    border-left: 2px solid #ccc;
    border-radius: 0 10px 10px 0;
}
@media (max-width: 800px) {
    #rotate-msg {
        display: block;
        font-weight: bold;
        color: #AA0000;
        margin-bottom: 1rem;
        background-color: #fff0f0;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
    }
}
#rotate-msg {
    display: none;
}
@media (max-width: 1000px) {
    .block-container .main .element-container {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto;
    }
    .block-container section[data-testid="stHorizontalBlock"] > div {
        min-width: 300px !important;
        margin-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="rotate-msg">📱 Per una migliore esperienza, ruota il telefono in orizzontale.</div>', unsafe_allow_html=True)

st.title("Oracle Item Setup - Web App")

@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return {"size_df": size_df, "features_df": features_df, "materials_df": materials_df}

data = load_config_data()
materials_df = data["materials_df"]
material_types = materials_df["Material Type"].dropna().unique().tolist()

part_options = ["Gasket, Flat"]
selected_part = st.selectbox("Seleziona il tipo di parte da configurare:", part_options)

if selected_part == "Gasket, Flat":
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("### 🛠️ Input")
        st.markdown("---")
        thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f")
        uom = st.selectbox("UOM", ["mm", "inches"])
        dwg = st.text_input("Dwg/doc number")
        mtype = st.selectbox("Material Type", [""] + material_types)
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes)
        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names)

        if st.button("Genera Output"):
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
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

    with col3:
        st.markdown("### 🧾 DataLoad")
        st.markdown("---")
        dataload_mode = st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"], horizontal=True)
        item_code = st.text_input("Item Number", placeholder="Es. 50158-0001")
        dataload_string = ""
        if "output_data" in st.session_state and item_code:
            d = st.session_state["output_data"]
            if dataload_mode == "Creazione item":
                dataload_string = f"{item_code}\t{d['Description']}\t{d['Template']}\t{d['Identificativo']}\t{d['ERP_L1']}\t{d['ERP_L2']}\t{d['Catalog']}\t{d['Material']}\t{d['FPD material code']}"
            else:
                dataload_string = f"{item_code}\tAggiorna:\t{d['Description']}\t{d['Material']}\t{d['FPD material code']}"
        st.text_area("Stringa per DataLoad", value=dataload_string, height=200)