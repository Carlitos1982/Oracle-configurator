import streamlit as st

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === SCELTA PARTE ===
part_options = [
    "Casing, Pump", "Impeller", "Shaft",
    "Bearing Housing", "Seal Cover", "Mechanical Seal", "Coupling Guard"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

if selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")

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

# === OUTPUT ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nel campo e premi Ctrl+C per copiare il valore_")

    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")

# === ALTRE PARTI ===
if selected_part != "Casing, Pump":
    st.info(f"La configurazione per **{selected_part}** è in fase di sviluppo.")