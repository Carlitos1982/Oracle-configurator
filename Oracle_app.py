import streamlit as st

# === DATI ===
size_options = {
    "HPX": ["", "1.5HPX15A", "2HPX10A"],
    "HDX": ["", "4HDX14A", "6HDX13A"],
    "HED": ["", "1,5HED11", "2HED13"]
}
features_options = {
    "HPX": {"features1": ["", "STD", "INDUCER"], "features2": ["", "PLUGGED DISCHARGE NOZZLE"]},
    "HDX": {"features1": ["", "TOP-TOP", "SIDE-SIDE PL"], "features2": None},
    "HED": {"features1": ["TOP-TOP"], "features2": ["", "HEAVY"]}
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

# === INTERFACCIA ===
st.set_page_config(page_title="Oracle Item Setup", layout="wide")
st.title("Oracle Item Setup")

st.subheader("Configurazione - Casing, Pump")

# === INPUT ===
model = st.selectbox("Product/Pump Model", list(size_options.keys()), index=0)
size = st.selectbox("Product/Pump Size", size_options.get(model, [""]), index=0)

features1 = features_options.get(model, {}).get("features1", [""])
features2 = features_options.get(model, {}).get("features2", [""])

feature1 = st.selectbox("_Additional_Features", features1 or [""])
feature2 = st.selectbox("_Additional_Features2", features2 or [""]) if features2 else ""

note = st.text_input("Note")
drawing = st.text_input("Dwg/doc number")

mat_type = st.selectbox("Material Type", list(material_options.keys()))
prefixes = list(material_options[mat_type].keys())

if None in prefixes:
    mat_prefix = ""
    mat_name = st.selectbox("Material Name", material_options[mat_type][None])
else:
    mat_prefix = st.selectbox("Material Prefix", prefixes)
    mat_name = st.selectbox("Material Name", material_options[mat_type][mat_prefix])

mat_add = st.text_input("Material add. Features")

# === GENERAZIONE OUTPUT ===
if st.button("Genera Output"):
    descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feature1, feature2, note]))
    materiale = f"{mat_type} {mat_prefix}{mat_name} {mat_add}".strip()

    output_data = {
        "Item": "40202...",
        "Description": descrizione,
        "Identificativo": "1100-CASING",
        "Classe ricambi": "3",
        "Categories": "Fascia ite 4",
        "Catalog": "CORPO",
        "Disegno": drawing,
        "Mater+Descr_FPD": materiale,
        "Template": "FPD_MAKE",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "17_CASING",
        "To supplier": "",
        "Quality": ""
    }

    st.subheader("Risultato finale")
    st.table(output_data)
