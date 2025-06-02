import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

# --- Configurazione pagina wide
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- Header con titolo e logo Flowserve
flowserve_logo = Image.open("assets/IMG_1456.png")
col_header, col_spacer, col_logo = st.columns([3, 4, 1], gap="small")
with col_header:
    st.markdown("# Oracle Item Setup - Web App")
with col_logo:
    st.image(flowserve_logo, width=100)

st.markdown("---")

# --- Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- Selezione parte
part = st.selectbox("Seleziona il tipo di parte da configurare:", [
    "Shaft, Pump",
    "Gasket, Flat",
    "Flange, Pipe",
    "Gasket, Spiral Wound",
    "Nut, Hex",
    "Stud, Threaded",
    "Ring, Wear",
    "Gusset, Other"
])
st.markdown("---")

# --- GASKET, SPIRAL WOUND
if part == "Gasket, Spiral Wound":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        winding = st.selectbox("Material winding", ["SS304", "SS316", "MONEL", "INCONEL"], key="gsw_winding")
        filler = st.selectbox("Filler", ["GRAPHITE", "PTFE"], key="gsw_filler")
        out_dia = st.number_input("Outer diameter (mm)", min_value=0.0, step=0.1, key="gsw_od")
        in_dia = st.number_input("Inner diameter (mm)", min_value=0.0, step=0.1, key="gsw_id")
        thickness = st.text_input("Thickness", key="gsw_thk")
        rating = st.text_input("Rating", key="gsw_rating")
        dwg = st.text_input("Disegno", key="gsw_dwg")
        note = st.text_area("Note", key="gsw_note")

        if st.button("Genera Output", key="gen_gsw"):
            st.session_state["output"] = {}
            descr = f"GASKET, SPIRAL WOUND - OD: {out_dia}mm, ID: {in_dia}mm, THK: {thickness}, RATING: {rating}, COLOR CODE 1: {winding}, COLOR CODE 2: {filler}"
            if note:
                descr += f", NOTE: {note}"
            st.session_state["output"] = {
                "Item": "50415…",
                "Description": descr,
                "Identificativo": "4510-JOINT",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": "NA",
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_1",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "16_SPIRAL_WOUND",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        st.subheader("📤 Output")
        if "output" in st.session_state:
            for k, v in st.session_state.output.items():
                if k == "Description":
                    st.text_area(k, value=v, height=80, key=f"gsw_{k}")
                else:
                    st.text_input(k, value=v, key=f"gsw_{k}")

    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="gsw_dl_mode")
        item_code_input = st.text_input("Codice item", key="gsw_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_gsw"):
            if not item_code_input:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\%FN", item_code_input,
                    "\%TC", get_val("Template"), "TAB",
                    "\%D", "\%O", "TAB",
                    get_val("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\%O", "\^S",
                    "\%TA", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val("Categories").split()[-1], "\^S", "\^{F4}",
                    "\%TG", get_val("Catalog"), "TAB", "TAB", "TAB",
                    get_val("Disegno"), "TAB", "\^S", "\^{F4}",
                    "\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\^S", "\^{F4}",
                    "\%VA", "TAB",
                    get_val("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val("Quality") if get_val("Quality") != "." else ".", "\^S",
                    "\%FN", "TAB",
                    get_val("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val("To supplier") if get_val("To supplier") != "." else ".", "\^S", "\^S", "\^{F4}", "\^S"
                ]
                dataload_string = "\t".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(
                    label="📎 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code_input}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
