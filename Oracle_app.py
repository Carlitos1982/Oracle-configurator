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
    size_df      = pd.read_excel(xls, sheet_name="Pump Size")
    features_df  = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# Lista completa delle parti
part_options = [
    "Baseplate, Pump",
    "Casing, Pump",
    "Casing Cover, Pump",
    "Impeller, Pump",
    "Balance Bushing, Pump",
    "Balance Drum, Pump",
    "Balance Disc, Pump",
    "Shaft, Pump",
    "Flange, Pipe",
    "Gate, Valve",
    "Gasket, Spiral Wound",
    "Gasket, Flat",
    "Bearing, Hydrostatic/Hydrodynamic",
    "Bearing, Rolling",
    "Bolt, Eye",
    "Bolt, Hexagonal",
    "Gasket, Ring Type Joint",
    "Gusset, Other",
    "Nut, Hex",
    "Stud, Threaded",
    "Ring, Wear",
    "Pin, Dowel",
    "Screw, Cap",
    "Screw, Grub"
]

# Selezione parte
selected_part = st.selectbox("Seleziona Parte", part_options)
st.markdown("---")

# -----------------------
# Ogni blocco: 3 colonne
# -----------------------

# --- BASEPLATE, PUMP
if selected_part == "Baseplate, Pump":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        length_bp      = st.number_input("Length (mm)", min_value=0.0, step=1.0, key="bp_length")
        width_bp       = st.number_input("Width (mm)", min_value=0.0, step=1.0, key="bp_width")
        weight_bp      = st.number_input("Weight (kg)", min_value=0.0, step=1.0, key="bp_weight")
        sourcing_bp    = st.selectbox("Sourcing", ["Europe", "India", "China"], key="bp_sourcing")
        dwg_bp         = st.text_input("Dwg/doc number", key="bp_dwg")
        note_bp        = st.text_area("Note (opzionale)", height=80, key="bp_note")
        mtype_bp       = st.selectbox("Material Type", [""] + material_types, key="bp_mtype")
        df_pref_bp = materials_df[
            (materials_df["Material Type"] == mtype_bp) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bp = sorted(df_pref_bp["Prefix"].unique()) if mtype_bp != "MISCELLANEOUS" else []
        mprefix_bp  = st.selectbox("Material Prefix", [""] + prefixes_bp, key="bp_mprefix")
        if mtype_bp == "MISCELLANEOUS":
            names_bp = materials_df[
                materials_df["Material Type"] == mtype_bp
            ]["Name"].dropna().tolist()
        else:
            names_bp = materials_df[
                (materials_df["Material Type"] == mtype_bp) &
                (materials_df["Prefix"] == mprefix_bp)
            ]["Name"].dropna().tolist()
        mname_bp = st.selectbox("Material Name", [""] + names_bp, key="bp_mname")
        if st.button("Genera Output", key="gen_bp"):
            materiale_bp = (
                f"{mtype_bp} {mprefix_bp} {mname_bp}".strip()
                if mtype_bp != "MISCELLANEOUS" else mname_bp
            )
            match_bp = materials_df[
                (materials_df["Material Type"] == mtype_bp) &
                (materials_df["Prefix"] == mprefix_bp) &
                (materials_df["Name"] == mname_bp)
            ]
            codice_fpd_bp = match_bp["FPD Code"].values[0] if not match_bp.empty else ""
            descr_bp = (
                f"BASEPLATE, PUMP - L:{int(length_bp)}mm, W:{int(width_bp)}mm, Wt:{weight_bp}kg, "
                f"Sourcing: {sourcing_bp}, Material: {materiale_bp}"
            )
            if note_bp:
                descr_bp += f", NOTE: {note_bp}"
            st.session_state["output_data"] = {
                "Item": "477…",
                "Description": descr_bp,
                "Identificativo": "6110-BASE PLATE",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_bp,
                "Material": materiale_bp,
                "FPD material code": codice_fpd_bp,
                "Template": "FPD_BUY_4",
                "ERP_L1": "21_FABRICATIONS_OR_BASEPLATES",
                "ERP_L2": "18_FOUNDATION_PLATE",
                "To supplier": "",
                "Quality": ""
            }
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bp_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bp_{campo}")
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_bp = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bp_dl_mode")
        item_code_bp = st.text_input("Codice item", key="bp_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_bp"):
            if not item_code_bp:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\\%FN", item_code_bp,
                    "\\%TC", get_val("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val("Catalog"), "TAB", "TAB", "TAB",
                    get_val("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val("Quality") if get_val("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val("To supplier") if get_val("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string = "\t".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(label="💾 Scarica file CSV per Import Data", data=csv_buffer.getvalue(), file_name=f"dataload_{item_code_bp}.csv", mime="text/csv")
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- CASING, PUMP
elif selected_part == "Casing, Pump":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        model    = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="casing_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size     = st.selectbox("Product/Pump Size", [""] + size_list, key="casing_size")
        feature_1 = ""
        special = ["HDO", "DMX", "WXB", "WIK"]
        if not (model in special and selected_part != "Casing, Pump"):
            f1_list = features_df[
                (features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="f1_casing")
        feature_2 = ""
        if (model == "HPX") or (model == "HED"):
            f2_list = features_df[
                (features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key="f2_casing")
        int_dia  = st.number_input("Diametro interno (mm)", min_value=0, step=1, format="%d", key="int_dia_casing")
        ext_dia  = st.number_input("Diametro esterno (mm)", min_value=0, step=1, format="%d", key="ext_dia_casing")
        note     = st.text_area("Note (opzionale)", height=80, key="note_casing")
        dwg      = st.text_input("Dwg/doc number", key="dwg_casing")
        mtype    = st.selectbox("Material Type", [""] + material_types, key="mtype_casing")
        pref_df  = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix  = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix_casing")
        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
        mname    = st.selectbox("Material Name", [""] + names, key="mname_casing")
        if st.button("Genera Output", key="gen_casing"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix) & (materials_df["Name"] == mname)]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
            descr = f"CASING, PUMP - MODEL: {model}, SIZE: {size}, ID: {int(int_dia)}mm, OD: {int(ext_dia)}mm, FEATURES: {feature_1}, {feature_2}, NOTE: {note}"
            st.session_state["output_data"] = {
                "Item": "40202…",
                "Description": descr,
                "Identificativo": "1100-CASING",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "CORPO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "17_CASING",
                "To supplier": "",
                "Quality": ""
            }
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"casing_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"casing_{campo}")
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="casing_dl_mode")
        item_code = st.text_input("Codice item", key="casing_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_casing"):
            if not item_code:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\\%FN", item_code,
                    "\\%TC", get_val("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val("Catalog"), "TAB", "TAB", "TAB",
                    get_val("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val("Quality") if get_val("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val("To supplier") if get_val("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string = "\t".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(label="💾 Scarica file CSV per Import Data", data=csv_buffer.getvalue(), file_name=f"dataload_{item_code}.csv", mime="text/csv")
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# (continua con tutti gli altri blocchi nello stesso stile per ciascuna parte...)
