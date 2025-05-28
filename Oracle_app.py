
import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- CSS per layout e fix grafici ---
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #FAFAFA !important;
    color: #222 !important;
    font-family: 'Segoe UI', sans-serif;
}
input, textarea, select {
    background-color: white !important;
    color: #222 !important;
    border: 1px solid #ccc !important;
    border-radius: 6px !important;
    padding: 0.4rem 0.6rem !important;
    font-size: 0.95rem !important;
}
select {
    appearance: none !important;
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
    background-color: white !important;
    background-image: url("data:image/svg+xml;utf8,<svg fill='black' height='10' viewBox='0 0 24 24' width='10' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/></svg>");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 1rem;
    padding-right: 2rem !important;
}
[data-baseweb="select"] > div {
    background-color: white !important;
    border-radius: 8px !important;
    border: 1px solid #ccc !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- Dummy materials ---
materials_df = pd.DataFrame({
    "Material Type": ["ASTM", "ASTM", "EN", "MISCELLANEOUS"],
    "Prefix": ["A", "B", "C", None],
    "Name": ["304", "316", "S235JR", "SPECIAL"],
    "FPD Code": ["FPD-A304", "FPD-B316", "FPD-C235", "FPD-MISC"]
})
material_types = materials_df["Material Type"].dropna().unique().tolist()

st.title("Oracle Item Setup - Web App")

selected_part = st.selectbox("Seleziona il tipo di parte da configurare:", ["Gasket, Flat"])

col1, col2, col3 = st.columns(3)

if selected_part == "Gasket, Flat":
    with col1:
        st.subheader("🔧 Input")
        thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f")
        uom = st.selectbox("UOM", ["mm", "inches"])
        dwg = st.text_input("Dwg/doc number")
        mtype = st.selectbox("Material Type", [""] + material_types)
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes)
        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names)

        if st.button("Genera Output"):
            if mtype != "MISCELLANEOUS":
                materiale = f"{mtype} {mprefix} {mname}".strip()
                match = materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Prefix"] == mprefix) &
                    (materials_df["Name"] == mname)
                ]
            else:
                materiale = mname
                match = materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Name"] == mname)
                ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
            descr = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {materiale}"
            st.session_state["output_data"] = {
                "Item": "50158…",
                "Description": descr,
                "Identificativo": "4590-GASKET",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

    with col3:
        st.subheader("🧾 DataLoad")
        mode = st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"])
        item_num = st.text_input("Item Number", placeholder="Es. 50158-0001")
        if "output_data" in st.session_state:
            out = st.session_state["output_data"]
            stringa_dl = f"{item_num}\t{out['Description']}\t{out['Template']}\t{out['ERP_L1']}\t{out['ERP_L2']}"
            st.text_area("Stringa per DataLoad", value=stringa_dl, height=100)
