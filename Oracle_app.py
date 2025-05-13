import streamlit as st
import streamlit.components.v1 as components

# === CONFIGURAZIONE STREAMLIT (PRIMA DI TUTTO) ===
st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")

# === STILE PER BOTTONE COPIA CLICCATO ===
st.markdown("""
    <style>
    .copied-button {
        background-color: #d4edda !important;
        color: #155724 !important;
        font-weight: bold;
        border: 1px solid #c3e6cb !important;
    }
    </style>
""", unsafe_allow_html=True)

# === FUNZIONE: BOTTONE COPIA CHE CAMBIA COLORE ===
def render_copy_button(text, campo):
    copied_fields = st.session_state.get("copied_fields", [])
    copied = campo in copied_fields

    label = "Copia"
    style = "copied-button" if copied else ""

    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    html = f"""
    <input type="button" value="{label}" class="{style}" onclick='navigator.clipboard.writeText("{escaped}");
    const input = window.parent.document.querySelector("input[data-streamlit-input=\'{campo}\']");
    if (input) {{
        input.value = "1";
        input.dispatchEvent(new Event("input", {{ bubbles: true }}));
    }}' style="padding:6px 12px; font-size:0.9rem; border-radius:4px; cursor:pointer; border:1px solid #ccc;" />
    """
    st.text_input("", "", key=campo, label_visibility="collapsed")
    components.html(html, height=40)

    if st.session_state.get(campo) == "1" and campo not in copied_fields:
        st.session_state["copied_fields"].append(campo)
        st.session_state[campo] = "0"

# === TITOLO ===
st.title("Oracle Item Setup - Web App")

# === SCELTA PARTE ===
part_options = [
    "Casing, Pump", "Impeller", "Shaft",
    "Bearing Housing", "Seal Cover", "Mechanical Seal", "Coupling Guard"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# === SOLO CASING, PUMP ATTIVO ===
if selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")

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

    model = st.selectbox("Product/Pump Model", [""] + list(size_options.keys()))
    size_choices = size_options.get(model, [])
    size = st.selectbox("Product/Pump Size", [""] + size_choices)
    features = features_options.get(model, {})
    feature_1 = st.selectbox("Additional Feature 1", [""] + features.get("features1", []))
    feature_2 = st.selectbox("Additional Feature 2", [""] + features.get("features2", []) if features.get("features2") else [""])
    note = st.text_area("Note (opzionale)", height=80)
    dwg = st.text_input("Dwg/doc number")

    mtype = st.selectbox("Material Type", [""] + list(material_options.keys()))
    prefix_options = []
    if mtype and mtype != "MISCELLANEOUS":
        prefix_options = list(material_options[mtype].keys())
    mprefix = st.selectbox("Material Prefix", [""] + prefix_options)

    name_options = []
    if mtype == "MISCELLANEOUS":
        name_options = material_options[mtype][None]
    elif mtype and mprefix:
        name_options = material_options[mtype].get(mprefix, [])
    mname = st.selectbox("Material Name", [""] + name_options)
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
        st.session_state["copied_fields"] = []

# === MOSTRA OUTPUT ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    for campo, valore in st.session_state["output_data"].items():
        st.markdown(f"**{campo}**")
        if campo == "Description":
            st.text_area("", value=valore, height=100, label_visibility="collapsed")
        else:
            st.code(valore)
        render_copy_button(valore, campo)

    st.markdown("---")
    output_all = "\n".join(f"{k}: {v}" for k, v in st.session_state["output_data"].items())
    st.text_area("Output completo (per copia manuale su iPhone)", value=output_all, height=300)

# === ALTRE PARTI ===
if selected_part != "Casing, Pump":
    st.info("La configurazione per **" + selected_part + "** è in fase di sviluppo. Riprova più tardi.")