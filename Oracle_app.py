
import streamlit as st

st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")
st.markdown("""<style>
    body {
        background-color: #f5f7fa;
    }
    .block-container {
        padding-top: 1rem;
    }
</style>""", unsafe_allow_html=True)

st.title("Oracle Item Setup - Web App")
st.write("Seleziona il tipo di parte da configurare:")

parti = ["Gasket, Flat"]
selected_part = st.selectbox("", parti)

st.markdown("---")

col1, col2, col3 = st.columns(3)

# Simulazione dei dati
descr = "GASKET, FLAT - THK: 0.1mm,\nMATERIAL:"
item_number = "50158..."
item_code_input = "Es. 50158-0001"
dataload_string = "GASKET, FLAT - THK: 0.1mm,\nMATERIAL: FPD_BUY_2\n55_GASKETS_OR_SEAL\n20_OTHER"

with col1:
    st.markdown("### 🛠️ Input")
    st.number_input("Thickness", value=0.0, step=0.1)
    st.selectbox("UOM", ["mm", "inch"])
    st.text_input("Dwg/doc number")
    st.selectbox("Material Type", ["ASTM", "EN", "Miscellaneous"])
    st.selectbox("Material Prefix", ["A", "B", "C"])
    st.selectbox("Material Name", ["316L", "304", "Carbon Steel"])
    st.button("Genera Output")

with col2:
    st.markdown("### 📤 Output")
    st.text_input("Item", item_number)
    st.text_area("Description", value=descr, height=60)
    st.text_input("Identificativo", "4590-GASKET")
    st.text_input("Classe ricambi", "1-2-3")
    st.text_input("Categories", "FASCIA ITE 5")
    st.text_input("Catalog", "ARTVARI")
    st.text_input("Material", "NA")
    st.text_input("FPD material code", "NOT AVAILABLE")
    st.text_input("Template", "FPD_BUY_2")
    st.text_input("ERP L1", "55_GASKETS_OR_SEAL")
    st.text_input("ERP L2", "20_OTHER")

with col3:
    st.markdown("### 🧾 DataLoad")
    operazione = st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"])
    st.text_input("Item Number", item_code_input)
    st.text_area("Stringa per DataLoad", value=dataload_string, height=90)
