import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === Funzione: copia JS per ogni campo ===
def render_copy_button(valore, campo):
    if st.button(f"Copia", key=f"copy_{campo}"):
        escaped = valore.replace("\\", "\\\\").replace('"', '\\"')
        js = f"""
        <script>
        navigator.clipboard.writeText("{escaped}");
        </script>
        """
        components.html(js, height=0)

# === Configurazione attiva ===
part_options = [
    "Casing, Pump", "Impeller", "Shaft", "Bearing Housing", "Seal Cover", "Mechanical Seal", "Coupling Guard"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

if selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")

    # === Input utente ===
    model = st.selectbox("Product/Pump Model", ["", "HPX", "HDX", "HED"])
    size = st.selectbox("Product/Pump Size", ["", "1.5HPX15A", "2HPX10A"])
    feature_1 = st.selectbox("Additional Feature 1", ["", "STD", "INDUCER"])
    feature_2 = st.selectbox("Additional Feature 2", ["", "PLUGGED DISCHARGE NOZZLE"])
    note = st.text_area("Note (opzionale)", height=80)
    dwg = st.text_input("Dwg/doc number")
    mtype = st.selectbox("Material Type", ["", "ASTM", "EN", "MISCELLANEOUS"])
    mprefix = st.selectbox("Material Prefix", ["", "A", "B", "C", "D"])
    mname = st.selectbox("Material Name", ["", "A105", "A216 WCB", "1.4301", "1.0619", "BRONZE", "PLASTIC"])
    madd = st.text_input("Material add. Features (opzionale)")

    # === Genera output ===
    if st.button("Genera Output"):
        descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note]))
        materiale = " ".join(filter(None, [mtype, mprefix + mname if mprefix and mname else "", madd]))

        st.session_state["output_data"] = {
            "Item": "40202...",
            "Description": descrizione,
            "Identificativo": "1100-CASING",
            "Classe ricambi": "3",
            "Categories": "Fascia ite 4",
            "Catalog": "CORPO",
            "Disegno": dwg,
            "Mater+Descr_FPD": materiale,
            "Template": "FPD_MAKE",
            "ERP_L1": "20_TURNKEY_MACHINING",
            "ERP_L2": "17_CASING",
            "To supplier": "",
            "Quality": ""
        }

# === Output finale ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")

    for campo, valore in st.session_state["output_data"].items():
        st.markdown(f"**{campo}**")
        st.code(valore)
        render_copy_button(valore, campo)

# === Altre parti ===
if selected_part != "Casing, Pump":
    st.info("La configurazione per **" + selected_part + "** è in fase di sviluppo. Riprova più tardi.")