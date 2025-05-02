# streamlit_oracle_config.py
import streamlit as st
import streamlit.components.v1 as components

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

# === FUNZIONI ===
def get_material_names(mtype, prefix):
    return material_options.get(mtype, {}).get(prefix, [])

def get_misc_names(mtype):
    return material_options.get(mtype, {}).get(None, [])

def copy_button(value, key):
    btn_id = f"btn_{key}"
    js_code = f"""
    <script>
    function copyToClipboard_{key}() {{
        navigator.clipboard.writeText(`{value}`).then(function() {{
            var btn = document.getElementById("{btn_id}");
            if (btn) {{
                btn.innerText = "Copiato!";
                setTimeout(() => {{ btn.innerText = "Copia"; }}, 1500);
            }}
        }});
    }}
    </script>
    <button id="{btn_id}" onclick="copyToClipboard_{key}()">Copia</button>
    """
    components.html(js_code, height=40)

# === INTERFACCIA STREAMLIT ===
st.set_page_config(layout="wide")
st.title("Oracle Item Setup - Web App")

with st.form("config_form"):
    st.subheader("Configurazione - Casing, Pump")

    model = st.selectbox("Product/Pump Model", [""] + list(size_options.keys()))
    sizes = size_options.get(model, [])
    size = st.selectbox("Product/Pump Size", sizes) if model else st.selectbox("Product/Pump Size", ["Seleziona modello"])

    features = features_options.get(model, {})
    features1 = features.get("features1")
    features2 = features.get("features2")
    feature_1 = st.selectbox("Additional Feature 1", features1) if features1 else st.selectbox("Additional Feature 1", ["N/A"])
    feature_2 = st.selectbox("Additional Feature 2", features2) if features2 else st.selectbox("Additional Feature 2", ["N/A"])

    note = st.text_input("Note")
    dwg = st.text_input("Dwg/doc number")

    mtype = st.selectbox("Material Type", [""] + list(material_options.keys()))
    if mtype == "MISCELLANEOUS":
        mprefix = ""
        mname = st.selectbox("Material Name", get_misc_names(mtype)) if mtype else ""
    elif mtype:
        mprefix = st.selectbox("Material Prefix", list(material_options.get(mtype, {}).keys()))
        mname = st.selectbox("Material Name", get_material_names(mtype, mprefix)) if mprefix else ""
    else:
        mprefix = ""
        mname = ""

    madd = st.text_input("Material add. Features")

    submitted = st.form_submit_button("Genera Output")

if submitted:
    st.subheader("Risultato finale")

    descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note]))
    materiale = f"{mtype} {mprefix}{mname} {madd}".strip()

    output_data = {
        "Item": "40202...",
        "Description": descrizione,
        "Identificativo": "1100-CASING",
        "Classe ricambi": "3
