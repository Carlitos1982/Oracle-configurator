import streamlit as st
import streamlit.components.v1 as components
import base64

# === FUNZIONE: BOTTONE HTML CON STATO COPIATO ===
def render_copy_button(text, campo):
    b64 = base64.b64encode(text.encode()).decode()
    copied_fields = st.session_state.get("copied_fields", [])
    copied = campo in copied_fields

    style_normal = "padding:6px 12px; font-size:0.9rem; border:1px solid #ccc; border-radius:4px; cursor:pointer;"
    style_copied = "padding:6px 12px; font-size:0.9rem; background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; border-radius:4px; font-weight: bold;"
    style = style_copied if copied else style_normal
    label = "✅ Copiato!" if copied else "Copia"

    html = f"""
    <script>
    function copyAndMark_{campo}() {{
        navigator.clipboard.writeText(atob('{b64}'));
        const input = window.parent.document.querySelector('input[data-streamlit-input="{campo}"]');
        if (input) {{
            input.value = "1";
            const event = new Event("input", {{ bubbles: true }});
            input.dispatchEvent(event);
        }}
    }}
    </script>
    <div style="margin-top: 6px;">
        <button onclick="copyAndMark_{campo}()" style="{style}">{label}</button>
    </div>
    """
    st.text_input("", "", key=campo, label_visibility="collapsed")
    components.html(html, height=50)

    if st.session_state.get(campo) == "1" and campo not in copied_fields:
        st.session_state["copied_fields"].append(campo)
        st.session_state[campo] = "0"

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

    model = st.selectbox("Product/Pump Model", [""] + list(size_options.keys()), key="model")
    size_choices = size_options.get(model, [])
    size = st.selectbox("Product/Pump Size", [""] + size_choices, key="size")
    features = features_options.get(model, {})
    feature_1 = st.selectbox("Additional Feature 1", [""] + features.get("features1", []), key="feature1")
    feature_2 = st.selectbox("Additional Feature 2", [""] + features.get("features2", []) if features.get("features2") else [""], key="feature2")
    note = st.text_area("Note (opzionale)", height=80, key="note_input")
    dwg = st.text_input("Dwg/doc number", key="dwg_input")

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
    madd = st.text_input("Material add. Features (opzionale)", key="madd_input")

    if st.button("Genera Output", key="genera_output"):
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

if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    output_data = st.session_state["output_data"]

    for campo, valore in output_data.items():
        st.markdown("**" + campo + "**")
        if campo == "Description":
            st.text_area(label="", value=valore, height=100, key=f"txt_{campo}", label_visibility="collapsed")
        else:
            st.code(valore, language="text")
        render_copy_button(valore, campo)

    full_output = "\n".join([f"{k}: {v}" for k, v in output_data.items()])
    st.markdown("---")
    st.text_area("Output completo (per copia manuale su iPhone)", value=full_output, height=300)

if selected_part != "Casing, Pump":
    st.info("La configurazione per **" + selected_part + "** è in fase di sviluppo. Riprova più tardi.")