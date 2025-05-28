
import streamlit as st

# Config pagina
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# Messaggio per utenti mobile in verticale
if st.session_state.get("show_rotate_message", True):
    st.warning("📱 Ruota lo smartphone in orizzontale per una migliore visualizzazione")
    st.session_state["show_rotate_message"] = False

# Layout a 3 colonne con larghezza bilanciata
col1, col2, col3 = st.columns([1, 1, 1])

# Colonna 1: Input
with col1:
    st.markdown("### 🛠️ Input")
    thickness = st.number_input("Thickness", value=0.0, step=0.1, format="%.1f")
    uom = st.selectbox("UOM", ["mm", "inches"])
    dwg = st.text_input("Dwg/doc number")
    mtype = st.selectbox("Material Type", ["ASTM", "EN", "MISCELLANEOUS"])
    mprefix = st.selectbox("Material Prefix", ["A", "B", "C"])
    mname = st.selectbox("Material Name", ["304", "316", "321"])

# Colonna 2: Output
with col2:
    st.markdown("### 📤 Output")
    item_code = "50158..."
    descr = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL:"
    st.text_input("Item", value=item_code)
    st.text_area("Description", value=descr, height=60)
    st.text_input("Identificativo", value="4590-GASKET")
    st.text_input("Classe ricambi", value="1-2-3")
    st.text_input("Categories", value="FASCIA ITE 5")
    st.text_input("Catalog", value="ARTVARI")

# Colonna 3: Dataload
with col3:
    st.markdown("### 🧾 DataLoad")
    operation = st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"])
    item_number = st.text_input("Item Number", placeholder="Es. 50158-0001")
    dataload_string = descr + "\nMATERIAL: FPD_BUY_2\n55_GASKETS_OR_SEAL\n20_OTHER"
    st.text_area("Stringa per DataLoad", value=dataload_string, height=100)
