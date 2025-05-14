import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === Inizializzazione stato
if "highlighted_fields" not in st.session_state:
    st.session_state["highlighted_fields"] = []

# === Funzione: genera blocco HTML selezionabile con bordo rosso se cliccato
def campo_html(label, value, campo):
    clicked = campo in st.session_state["highlighted_fields"]
    border = "2px solid red" if clicked else "1px solid #ccc"

    html = f"""
    <div style="margin-bottom: 12px;">
        <label style="font-weight: bold; display: block; margin-bottom: 4px;">{label}</label>
        <textarea id="{campo}" readonly onclick="this.select(); this.style.border='2px solid red'; fetch('/?field={campo}')" 
        style="width: 100%; padding: 6px; font-size: 0.9rem; border: {border}; border-radius: 4px;">{value}</textarea>
    </div>
    """
    components.html(html, height=100)

# === Parte
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
        st.session_state["highlighted_fields"] = []

# === Output ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nel campo per selezionare, poi premi Ctrl+C per copiare._")

    for campo, valore in st.session_state["output_data"].items():
        campo_html(campo, valore, campo)

# === Aggiorna lista campi cliccati (hack temporaneo via query param)
query_params = st.experimental_get_query_params()
if "field" in query_params:
    field = query_params["field"][0]
    if field not in st.session_state["highlighted_fields"]:
        st.session_state["highlighted_fields"].append(field)
    # pulizia (evita persist che ricarica sempre)
    st.experimental_set_query_params()