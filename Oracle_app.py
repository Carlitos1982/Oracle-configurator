#=== Oracle App (versione Streamlit) ===

import streamlit as st

#=== Data ===

size_options = { "HPX": ["", "1.5HPX15A", "10HPX15A", "10HPX18A"], "HDX": ["", "4HDX14A", "6HDX11A"], "HED": ["", "1,5HED11", "2HED15"], }

features_options = { "HPX": {"features1": ["", "STD", "INDUCER"], "features2": ["", "PLUGGED DISCHARGE NOZZLE"]}, "HDX": {"features1": ["", "TOP-TOP"], "features2": None}, "HED": {"features1": ["TOP-TOP"], "features2": ["", "HEAVY"]}, }

material_options = { "ASTM": { "A": ["A105", "A216 WCB"], "B": ["B564 UNS N06625"] }, "EN": { "C": ["1.4301"], "D": ["1.0619"] }, "MISCELLANEOUS": { None: ["BRONZE", "PLASTIC"] } }

material_type_list = list(material_options.keys())

#=== UI ===

st.set_page_config(page_title="Oracle Item Setup", layout="wide") st.title("Oracle Item Setup - Web Version") st.subheader("Configurazione: Casing, Pump")

with st.form("casing_form"): model = st.selectbox("Product/Pump Model", list(size_options.keys())) size = st.selectbox("Product/Pump Size", size_options.get(model, [""]))

features1 = features_options.get(model, {}).get("features1", [])
features2 = features_options.get(model, {}).get("features2", [])

feat1 = st.selectbox("Additional Features", features1) if features1 else ""
feat2 = st.selectbox("Additional Features2", features2) if features2 else ""

note = st.text_input("Note")
dwg = st.text_input("Dwg/doc number")

mtype = st.selectbox("Material Type", material_type_list)
prefixes = list(material_options[mtype].keys())
prefix = st.selectbox("Material Prefix", prefixes) if prefixes[0] else ""
names = material_options[mtype][prefix] if prefix else material_options[mtype][None]
name = st.selectbox("Material Name", names)

madd = st.text_input("Material additional features")
submitted = st.form_submit_button("Genera Output")

#=== Output ===

if submitted: descrizione = "Casing, Pump " + " ".join(filter(None, [model, size, feat1, feat2, note, dwg, mtype, prefix, name, madd])) materiale = f"{mtype} {prefix}{name}"

st.success("Output generato!")
st.markdown("### Risultato finale")
st.table({
    "Campo": ["Item", "Description", "Disegno", "Materiale"],
    "Valore": ["40202...", descrizione, dwg, materiale]
})

