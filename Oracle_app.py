import streamlit as st

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === STILE per campo cliccato ===
st.markdown("""
    <style>
    .red-border > div > input, .red-border textarea {
        border: 2px solid red !important;
        border-radius: 4px !important;
    }
    </style>
""", unsafe_allow_html=True)

# === STATO CAMPI EVIDENZIATI ===
if "highlighted_fields" not in st.session_state:
    st.session_state["highlighted_fields"] = []

# === FUNZIONE: MEMORIZZA CAMPO CLICCATO ===
def on_focus(campo):
    if campo not in st.session_state["highlighted_fields"]:
        st.session_state["highlighted_fields"].append(campo)

# === PARTE ===
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
        st.session_state["highlighted_fields"] = []  # reset bordi

# === RISULTATO ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nel campo e premi Ctrl+C per copiare il valore_")

    for campo, valore in st.session_state["output_data"].items():
        field_key = f"out_{campo}"
        css_class = "red-border" if campo in st.session_state["highlighted_fields"] else ""

        with st.container():
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            if campo == "Description":
                st.text_area(campo, value=valore, key=field_key, height=100, on_change=on_focus, args=(campo,))
            else:
                st.text_input(campo, value=valore, key=field_key, on_change=on_focus, args=(campo,))
            st.markdown("</div>", unsafe_allow_html=True)

# === ALTRE PARTI ===
if selected_part != "Casing, Pump":
    st.info(f"La configurazione per **{selected_part}** è in fase di sviluppo. Riprova più tardi.")