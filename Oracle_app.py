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

# === UI ===
st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")
st.subheader("Configurazione - Casing, Pump")

model = st.selectbox("Product/Pump Model", [""] + list(size_options.keys()))

if model:
    size = st.selectbox("Product/Pump Size", size_options[model])
    features = features_options.get(model, {})
    f1 = features.get("features1", [])
    f2 = features.get("features2", [])
    feature_1 = st.selectbox("Additional Feature 1", f1 if f1 else ["N/A"])
    feature_2 = st.selectbox("Additional Feature 2", f2 if f2 else ["N/A"])
else:
    size = st.selectbox("Product/Pump Size", ["— Seleziona prima un modello —"])
    feature_1 = feature_2 = ""

note = st.text_area("Note (opzionale)", height=60)
dwg = st.text_input("Dwg/doc number")

mtype = st.selectbox("Material Type", [""] + list(material_options.keys()))
if mtype == "MISCELLANEOUS":
    mprefix = ""
    mname = st.selectbox("Material Name", material_options[mtype][None])
elif mtype:
    mprefix = st.selectbox("Material Prefix", list(material_options[mtype].keys()))
    mname = st.selectbox("Material Name", material_options[mtype][mprefix])
else:
    mprefix = mname = ""

madd = st.text_input("Material add. Features (opzionale)")

if st.button("Genera Output"):
    descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note])).strip()
    materiale = f"{mtype} {mprefix}{mname} {madd}".strip()

    output_data = {
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

    st.subheader("Risultato finale")
    for campo, valore in output_data.items():
        st.markdown(f"**{campo}**")
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.code(valore if valore else "-", language="text")
        with col2:
            copy_button(valore if valore else "", campo.replace(" ", "_"))
