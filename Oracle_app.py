import streamlit as st

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === STILE per bordo rosso ===
st.markdown("""
    <style>
    .red-border {
        border: 2px solid red !important;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# === inizializzazione
if "highlighted_fields" not in st.session_state:
    st.session_state["highlighted_fields"] = []

# === funzione per gestire il clic ===
def on_focus(campo):
    if campo not in st.session_state["highlighted_fields"]:
        st.session_state["highlighted_fields"].append(campo)

# === PARTE ===
part_options = ["Casing, Pump", "Impeller", "Shaft"]
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
    mprefix = st.selectbox("Material Prefix", ["", "A", "B"])
    mname = st.selectbox("Material Name", ["", "A105", "A216", "BRONZE", "PLASTIC"])
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
        st.session_state["highlighted_fields"] = []

# === OUTPUT ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca dentro il campo e premi Ctrl+C per copiare_")

    for campo, valore in st.session_state["output_data"].items():
        css_class = "red-border" if campo in st.session_state["highlighted_fields"] else ""
        st.markdown(f"""<div class="{css_class}">""", unsafe_allow_html=True)
        st.text_input(f"{campo}", value=valore, key=f"out_{campo}", on_change=on_focus, args=(campo,))
        st.markdown("</div>", unsafe_allow_html=True)

if selected_part != "Casing, Pump":
    st.info("La configurazione per **" + selected_part + "** è in fase di sviluppo.")