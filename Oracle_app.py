import streamlit as st
import streamlit.components.v1 as components
import base64

# === FUNZIONE COPIA ===
def copy_text_to_clipboard(text):
    b64 = base64.b64encode(text.encode()).decode()
    copy_code = f"""
    <script>
    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text);
    }}
    copyToClipboard(atob("{b64}"));
    </script>
    """
    components.html(copy_code, height=0)

# === CONFIGURAZIONE STREAMLIT ===
st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# === SCELTA PARTE ===
part_options = [
    "Casing, Pump",
    "Impeller",
    "Shaft",
    "Bearing Housing",
    "Seal Cover",
    "Mechanical Seal",
    "Coupling Guard"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# === SOLO CASING, PUMP ATTIVO ===
if selected_part == "Casing, Pump":

    st.subheader("Configurazione - Casing, Pump")

    # === DATI ===
    size_options = {
        "HPX": ["1.5HPX15A", "2HPX10A"],
        "HDX": ["4HDX14A", "6HDX13A"],
        "HED": ["1,5HED11", "2HED13"]
    }
    features_options = {
        "HPX": {"features1": ["STD", "INDUCER"], "features2": ["PLUGGED DISCHARGE NOZZLE"]},
        "HDX": {"features1": ["TOP-TOP", "SIDE-SIDE PL"], "features2": None},
        "HED": {"features1": ["TOP-TOP"], "features2": ["HEAVY"]}
    }
    material_options = {
        "ASTM": {
            "A": ["A105", "A216 WCB"],
            "B": ["B564 UNS N06625"]
        },
        "EN": {
            "C": ["1.4301"],
            "D": ["1.0619"]
        },
        "MISCELLANEOUS": {
            None: ["BRONZE", "PLASTIC"]
        }
    }

    # === MODELLO ===
    model = st.selectbox("Product/Pump Model", [""] + list(size_options.keys()), key="model")

    # === SIZE e FEATURES ===
    size_choices = size_options.get(model, [])
    size = st.selectbox("Product/Pump Size", [""] + size_choices, key="size")

    features = features_options.get(model, {})
    feature_1 = st.selectbox("Additional Feature 1", [""] + features.get("features1", []), key="feature1")
    feature_2 = st.selectbox("Additional Feature 2", [""] + features.get("features2", []) if features.get("features2") else [""], key="feature2")

    # === ALTRI CAMPI ===
    note = st.text_area("Note (opzionale)", height=80, key="note_input")
    dwg = st.text_input("Dwg/doc number", key="dwg_input")

    # === MATERIALI ===
    mtype = st.selectbox("Material Type", [""] + list(material_options.keys()), key="mtype")

    prefix_options = []
    if mtype and mtype != "MISCELLANEOUS":
        prefix_options = list(material_options[mtype].keys())
    mprefix = st.selectbox("Material Prefix", [""] + prefix_options, key="mprefix")

    name_options = []
    if mtype == "MISCELLANEOUS":
        name_options = material_options[mtype][None]
    elif mtype and mprefix:
        name_options = material_options[mtype].get(mprefix, [])
    mname = st.selectbox("Material Name", [""] + name_options, key="mname")

    # === CAMPO ADDIZIONALE ===
    madd = st.text_input("Material add. Features (opzionale)", key="madd_input")

    # === GENERAZIONE OUTPUT ===
    if st.button("Genera Output", key="genera_output"):
        descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note]))
        materiale = " ".join(filter(None, [mtype, mprefix + mname, madd]))

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
        st.session_state["copied_fields"] = []

    # === MOSTRA OUTPUT SE PRESENTE ===
    if "output_data" in st.session_state:
        st.subheader("Risultato finale")
        output_data = st.session_state["output_data"]

        for campo, valore in output_data.items():
            with st.container():
                st.markdown(f"**{campo}**")
                if campo == "Description":
                    st.text_area(label="", value=valore, height=100, key=f"txt_{campo}", label_visibility="collapsed")
                else:
                    st.code(valore, language="text")

                # Pulsante copia responsive
                copiato = st.button("Copia", key=f"copy_{campo}", use_container_width=True)
                if copiato:
                    copy_text_to_clipboard(valore)
                    if "copied_fields" not in st.session_state:
                        st.session_state["copied_fields"] = []
                    if campo not in st.session_state["copied_fields"]:
                        st.session_state["copied_fields"].append(campo)

                if campo in st.session_state.get("copied_fields", []):
                    st.markdown(
                        "<div style='text-align: right; margin-top: -0.5rem;'>"
                        "<span style='color: green; font-size: 0.85rem;'>✅ Copiato!</span>"
                        "</div>",
                        unsafe_allow_html=True
                    )

# === ALTRE PARTI ===
else:
    st.info(f"La configurazione per **{selected_part}** è in fase di sviluppo. Riprova più tardi.")