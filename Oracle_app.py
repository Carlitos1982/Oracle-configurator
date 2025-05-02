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

# === FUNZIONE COPIA ===
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

# === MODELLO E DIMENSIONE ===
st.markdown("### Modello e Dimensione")

col1, col2 = st.columns(2)

with col1:
    model = st.selectbox("Modello", [""] + list(size_options.keys()), key="model")

with col2:
    size_choices = size_options.get(model, [])
    if not size_choices:
        size_choices = ["Seleziona un modello"]
    size = st.selectbox("Dimensione", size_choices, key="size")
    if size == "Seleziona un modello":
        size = ""

# === CARATTERISTICHE AGGIUNTIVE ===
st.markdown("### Caratteristiche Aggiuntive")

features = features_options.get(model, {})
feature_1 = st.selectbox("Caratteristica 1", features.get("features1", ["N/A"]), key="feature1")
feature_2 = st.selectbox("Caratteristica 2", features.get("features2", ["N/A"]) if features.get("features2") else ["N/A"], key="feature2")

# === NOTE E DISEGNO ===
st.markdown("### Note e Disegno")

note = st.text_area("Note (opzionale)", height=80, key="note_input")
dwg = st.text_input("Dwg/doc number", key="dwg_input")

# === MATERIALI ===
st.markdown("### Materiali")

col1, col2 = st.columns(2)

with col1:
    mtype = st.selectbox("Material Type", [""] + list(material_options.keys()), key="mtype")

with col2:
    if mtype == "MISCELLANEOUS":
        st.selectbox("Material Prefix", ["N/A"], index=0, disabled=True)
        mname = st.selectbox("Material Name", material_options["MISCELLANEOUS"][None], key="mname_misc")
        mprefix = ""
    elif mtype:
        mprefix_options = list(material_options[mtype].keys())
        mprefix = st.selectbox("Material Prefix", mprefix_options, key="mprefix")
        mname_options = material_options[mtype].get(mprefix, [])
        mname = st.selectbox("Material Name", mname_options if mname_options else ["N/A"], key="mname_std")
    else:
        st.selectbox("Material Prefix", ["Seleziona un tipo materiale"], index=0, disabled=True)
        st.selectbox("Material Name", ["Seleziona un tipo materiale"], index=0, disabled=True)
        mprefix = ""
        mname = ""

madd = st.text_input("Material add. Features (opzionale)", key="madd_input")

# === GENERA OUTPUT ===
if st.button("Genera Output", key="genera_output"):
    descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature_1, feature_2, note]))
    materiale = f"{mtype} {mprefix}{mname}".strip()

    output_data = {
        "Item": "40202...",
        "Description": descrizione,
        "Identificativo": "1100-CASING",
        "Classe ricambi": "3",
        "Categories": "Fascia ite 4",
        "Catalog": "CORPO",
        "Disegno": dwg,
        "Mater+Descr_FPD": materiale,
        "Material add. Features": madd,
        "Template": "FPD_MAKE",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "17_CASING",
        "To supplier": "",
        "Quality": ""
    }

    st.subheader("Risultato finale")

    style = """
        <style>
        .output-block {
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            color: #222;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        .output-label {
            font-weight: 600;
            margin-bottom: 2px;
        }
        .output-value {
            background-color: #f9f9f9;
            padding: 6px 10px;
            border-radius: 5px;
            font-family: monospace;
            display: block;
        }
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

    for campo, valore in output_data.items():
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            if campo == "Description":
                st.markdown(f"""
                    <div class='output-block'>
                        <div class='output-label'>{campo}</div>
                        <textarea readonly rows='4' style='width:100%; resize: none; font-family: monospace; padding:6px;'>{valore}</textarea>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='output-block'>
                        <div class='output-label'>{campo}</div>
                        <span class='output-value'>{valore if valore else '-'}</span>
                    </div>
                """, unsafe_allow_html=True)
        with col2:
            copy_button(valore if valore else "", campo.replace(" ", "_"))
