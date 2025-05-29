import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# Intestazione con loghi e titolo
st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; padding-bottom: 10px;">
        <img src="https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/e4824ece0063e60c57011c8b5b29ad6df90fdcd6/assets/IMG_1456.png" alt="Flowserve" style="height: 60px;">
        <h1 style="margin: 0; font-size: 32px;">Oracle Item Setup - Web App</h1>
        <img src="https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/e4824ece0063e60c57011c8b5b29ad6df90fdcd6/assets/IMG_1455.png" alt="Oracle" style="height: 60px;">
    </div>
""", unsafe_allow_html=True)

@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return {
        "size_df": size_df,
        "features_df": features_df,
        "materials_df": materials_df
    }

data = load_config_data()
size_df = data["size_df"]
features_df = data["features_df"]
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
            names = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="flat_mname")

        if st.button("Genera Output", key="gen_flat"):
            if mtype != "MISCELLANEOUS":
                materiale = f"{mtype} {mprefix} {mname}".strip()
                match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix) & (materials_df["Name"] == mname)]
            else:
                materiale = mname
                match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Name"] == mname)]
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
        dataload_mode = st.radio("Modalità operazione", options=["Creazione item", "Aggiornamento item"], index=0, horizontal=True)
        item_code = st.text_input("Item Number", placeholder="Es. 50158-0001", key="item_code_input")

        dataload_string = ""
        if "output_data" in st.session_state and item_code:
            data = st.session_state["output_data"]
            if dataload_mode == "Creazione item":
                dataload_string = f"""{item_code}\t{data['Description']}\t{data['Template']}\t{data['Identificativo']}\t{data['ERP_L1']}\t{data['ERP_L2']}\t{data['Catalog']}\t{data['Material']}\t{data['FPD material code']}"""
            else:
                dataload_string = f"""{item_code}\tAggiorna:\t{data['Description']}\t{data['Material']}\t{data['FPD material code']}"""

        st.text_area("Stringa per DataLoad", value=dataload_string, height=200)