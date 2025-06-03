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
        if model not in special:
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
            descr = f"CASING, PUMP - MODEL: {model}, SIZE: {size}, FEATURES: {feature_1}, {feature_2}, NOTE: {note}"
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

# --- CASING COVER, PUMP
elif selected_part == "Casing Cover, Pump":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        model_cc    = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="cc_model")
        size_list_cc = size_df[size_df["Pump Model"] == model_cc]["Size"].dropna().tolist()
        size_cc     = st.selectbox("Product/Pump Size", [""] + size_list_cc, key="cc_size")
        feature_1_cc = ""
        special_cc = ["HDO", "DMX", "WXB", "WIK"]
        if not (model_cc in special_cc):
            f1_list_cc = features_df[
                (features_df["Pump Model"] == model_cc) & (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_cc = st.selectbox("Additional Feature 1", [""] + f1_list_cc, key="f1_cc")
        feature_2_cc = ""
        if model_cc in ["HPX", "HED"]:
            f2_list_cc = features_df[
                (features_df["Pump Model"] == model_cc) & (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2_cc = st.selectbox("Additional Feature 2", [""] + f2_list_cc, key="f2_cc")
        note_cc     = st.text_area("Note (opzionale)", height=80, key="note_cc")
        dwg_cc      = st.text_input("Dwg/doc number", key="dwg_cc")
        mtype_cc    = st.selectbox("Material Type", [""] + material_types, key="mtype_cc")
        pref_df_cc  = materials_df[(materials_df["Material Type"] == mtype_cc) & (materials_df["Prefix"].notna())]
        prefixes_cc = sorted(pref_df_cc["Prefix"].unique()) if mtype_cc != "MISCELLANEOUS" else []
        mprefix_cc  = st.selectbox("Material Prefix", [""] + prefixes_cc, key="mprefix_cc")
        if mtype_cc == "MISCELLANEOUS":
            names_cc = materials_df[materials_df["Material Type"] == mtype_cc]["Name"].dropna().tolist()
        else:
            names_cc = materials_df[
                (materials_df["Material Type"] == mtype_cc) & (materials_df["Prefix"] == mprefix_cc)
            ]["Name"].dropna().tolist()
        mname_cc    = st.selectbox("Material Name", [""] + names_cc, key="mname_cc")
        if st.button("Genera Output", key="gen_cc"):
            materiale_cc = f"{mtype_cc} {mprefix_cc} {mname_cc}".strip() if mtype_cc != "MISCELLANEOUS" else mname_cc
            match_cc    = materials_df[
                (materials_df["Material Type"] == mtype_cc) & (materials_df["Prefix"] == mprefix_cc) & (materials_df["Name"] == mname_cc)
            ]
            codice_fpd_cc = match_cc["FPD Code"].values[0] if not match_cc.empty else ""
            descr_cc = f"CASING COVER, PUMP - MODEL: {model_cc}, SIZE: {size_cc}, FEATURES: {feature_1_cc}, {feature_2_cc}, NOTE: {note_cc}"
            st.session_state["output_data"] = {
                "Item": "40205…",
                "Description": descr_cc,
                "Identificativo": "1221-CASING COVER",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "COPERCHIO",
                "Disegno": dwg_cc,
                "Material": materiale_cc,
                "FPD material code": codice_fpd_cc,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "13_OTHER",
                "To supplier": "",
                "Quality": ""
            }
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"cc_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"cc_{campo}")
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_cc = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="cc_dl_mode")
        item_code_cc = st.text_input("Codice item", key="cc_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_cc"):
            if not item_code_cc:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\%FN", item_code_cc,
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
                dataload_string = "	".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(label="💾 Scarica file CSV per Import Data", data=csv_buffer.getvalue(), file_name=f"dataload_{item_code_cc}.csv", mime="text/csv")
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- IMPELLER, PUMP
elif selected_part == "Impeller, Pump":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        model_imp   = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="imp_model")
        size_list_imp = size_df[size_df["Pump Model"] == model_imp]["Size"].dropna().tolist()
        size_imp    = st.selectbox("Product/Pump Size", [""] + size_list_imp, key="imp_size")
        feature_1_imp = ""
        if model_imp not in ["HDO", "DMX", "WXB", "WIK"]:
            f1_list_imp = features_df[(features_df["Pump Model"] == model_imp) & (features_df["Feature Type"] == "features1")]["Feature"].dropna().tolist()
            feature_1_imp = st.selectbox("Additional Feature 1", [""] + f1_list_imp, key="f1_imp")
        feature_2_imp = ""
        if model_imp in ["HPX", "HED"]:
            f2_list_imp = features_df[(features_df["Pump Model"] == model_imp) & (features_df["Feature Type"] == "features2")]["Feature"].dropna().tolist()
            feature_2_imp = st.selectbox("Additional Feature 2", [""] + f2_list_imp, key="f2_imp")
        note_imp    = st.text_area("Note (opzionale)", height=80, key="note_imp")
        dwg_imp     = st.text_input("Dwg/doc number", key="dwg_imp")
        mtype_imp   = st.selectbox("Material Type", [""] + material_types, key="mtype_imp")
        pref_df_imp = materials_df[(materials_df["Material Type"] == mtype_imp) & (materials_df["Prefix"].notna())]
        prefixes_imp = sorted(pref_df_imp["Prefix"].unique()) if mtype_imp != "MISCELLANEOUS" else []
        mprefix_imp = st.selectbox("Material Prefix", [""] + prefixes_imp, key="mprefix_imp")
        if mtype_imp == "MISCELLANEOUS":
            names_imp = materials_df[materials_df["Material Type"] == mtype_imp]["Name"].dropna().tolist()
        else:
            names_imp = materials_df[(materials_df["Material Type"] == mtype_imp) & (materials_df["Prefix"] == mprefix_imp)]["Name"].dropna().tolist()
        mname_imp    = st.selectbox("Material Name", [""] + names_imp, key="mname_imp")
        if st.button("Genera Output", key="gen_imp"):
            materiale_imp = f"{mtype_imp} {mprefix_imp} {mname_imp}".strip() if mtype_imp != "MISCELLANEOUS" else mname_imp
            match_imp    = materials_df[(materials_df["Material Type"] == mtype_imp) & (materials_df["Prefix"] == mprefix_imp) & (materials_df["Name"] == mname_imp)]
            codice_fpd_imp = match_imp["FPD Code"].values[0] if not match_imp.empty else ""
            descr_imp = f"IMPELLER, PUMP - MODEL: {model_imp}, SIZE: {size_imp}, FEATURES: {feature_1_imp}, {feature_2_imp}, NOTE: {note_imp}"
            st.session_state["output_data"] = {
                "Item": "40229…",
                "Description": descr_imp,
                "Identificativo": "2200-IMPELLER",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "GIRANTE",
                "Disegno": dwg_imp,
                "Material": materiale_imp,
                "FPD material code": codice_fpd_imp,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "20_IMPELLER_DIFFUSER",
                "To supplier": "",
                "Quality": ""
            }
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"imp_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"imp_{campo}")
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_imp = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="imp_dl_mode")
        item_code_imp = st.text_input("Codice item", key="imp_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_imp"):
            if not item_code_imp:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\%FN", item_code_imp,
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
                dataload_string = "	".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(label="💾 Scarica file CSV per Import Data", data=csv_buffer.getvalue(), file_name=f"dataload_{item_code_imp}.csv", mime="text/csv")
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BALANCE BUSHING, PUMP
elif selected_part == "Balance Bushing, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model_bb    = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bb_model")
        size_list_bb = size_df[size_df["Pump Model"] == model_bb]["Size"].dropna().tolist()
        size_bb     = st.selectbox("Product/Pump Size", [""] + size_list_bb, key="bb_size")

        feature_1_bb = ""
        special_bb = ["HDO", "DMX", "WXB", "WIK"]
        if model_bb not in special_bb:
            f1_list_bb = features_df[
                (features_df["Pump Model"] == model_bb) & (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_bb = st.selectbox("Additional Feature 1", [""] + f1_list_bb, key="f1_bb")

        feature_2_bb = ""
        if model_bb in ["HPX", "HED"]:
            f2_list_bb = features_df[
                (features_df["Pump Model"] == model_bb) & (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2_bb = st.selectbox("Additional Feature 2", [""] + f2_list_bb, key="f2_bb")

        note_bb    = st.text_area("Note (opzionale)", height=80, key="note_bb")
        dwg_bb     = st.text_input("Dwg/doc number", key="dwg_bb")

        # Campi extra diametri
        int_dia_bb = st.number_input("Diametro interno (mm)", min_value=0, step=1, format="%d", key="int_dia_bb")
        ext_dia_bb = st.number_input("Diametro esterno (mm)", min_value=0, step=1, format="%d", key="ext_dia_bb")

        mtype_bb   = st.selectbox("Material Type", [""] + material_types, key="mtype_bb")
        pref_df_bb = materials_df[
            (materials_df["Material Type"] == mtype_bb) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bb = sorted(pref_df_bb["Prefix"].unique()) if mtype_bb != "MISCELLANEOUS" else []
        mprefix_bb  = st.selectbox("Material Prefix", [""] + prefixes_bb, key="mprefix_bb")

        if mtype_bb == "MISCELLANEOUS":
            names_bb = materials_df[materials_df["Material Type"] == mtype_bb]["Name"].dropna().tolist()
        else:
            names_bb = materials_df[
                (materials_df["Material Type"] == mtype_bb) &
                (materials_df["Prefix"] == mprefix_bb)
            ]["Name"].dropna().tolist()
        mname_bb = st.selectbox("Material Name", [""] + names_bb, key="mname_bb")

        if st.button("Genera Output", key="gen_bb"):
            materiale_bb = (
                f"{mtype_bb} {mprefix_bb} {mname_bb}".strip()
                if mtype_bb != "MISCELLANEOUS" else mname_bb
            )
            match_bb = materials_df[
                (materials_df["Material Type"] == mtype_bb) &
                (materials_df["Prefix"] == mprefix_bb) &
                (materials_df["Name"] == mname_bb)
            ]
            codice_fpd_bb = match_bb["FPD Code"].values[0] if not match_bb.empty else ""
            descr_bb = (
                f"BALANCE BUSHING, PUMP - MODEL: {model_bb}, SIZE: {size_bb}, "
                f"ID: {int(int_dia_bb)}mm, OD: {int(int_dia_bb) + 2*int(ext_dia_bb)}mm, "  # oppure formula corretta
                f"FEATURES: {feature_1_bb}, {feature_2_bb}, NOTE: {note_bb}"
            )
            st.session_state["output_data"] = {
                "Item": "40226…",
                "Description": descr_bb,
                "Identificativo": "6231-BALANCE DRUM BUSH",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg_bb,
                "Material": materiale_bb,
                "FPD material code": codice_fpd_bb,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "16_BUSHING",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bb_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bb_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_bb = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bb_dl_mode")
        item_code_bb = st.text_input("Codice item", key="bb_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_bb"):
            if not item_code_bb:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_bb(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields_bb = [
                    "\\%FN", item_code_bb,
                    "\\%TC", get_val_bb("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_bb("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_bb("Identificativo"), "TAB",
                    get_val_bb("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_bb('ERP_L1')}.{get_val_bb('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_bb("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_bb("Catalog"), "TAB", "TAB", "TAB",
                    get_val_bb("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_bb("FPD material code"), "TAB",
                    get_val_bb("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_bb("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_bb("Quality") if get_val_bb("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_bb("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_bb("To supplier") if get_val_bb("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_bb = "\t".join(dataload_fields_bb)
                st.text_area("Anteprima (per copia manuale)", dataload_string_bb, height=200)
                csv_buffer_bb = io.StringIO()
                writer_bb = csv.writer(csv_buffer_bb, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_bb:
                    writer_bb.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_bb.getvalue(),
                    file_name=f"dataload_{item_code_bb}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BALANCE DRUM, PUMP
elif selected_part == "Balance Drum, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model_bd     = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bd_model")
        size_list_bd = size_df[size_df["Pump Model"] == model_bd]["Size"].dropna().tolist()
        size_bd      = st.selectbox("Product/Pump Size", [""] + size_list_bd, key="bd_size")

        feature_1_bd = ""
        special_bd = ["HDO", "DMX", "WXB", "WIK"]
        if model_bd not in special_bd:
            f1_list_bd = features_df[
                (features_df["Pump Model"] == model_bd) & (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_bd = st.selectbox("Additional Feature 1", [""] + f1_list_bd, key="f1_bd")

        feature_2_bd = ""
        if model_bd in ["HPX", "HED"]:
            f2_list_bd = features_df[
                (features_df["Pump Model"] == model_bd) & (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2_bd = st.selectbox("Additional Feature 2", [""] + f2_list_bd, key="f2_bd")

        note_bd     = st.text_area("Note (opzionale)", height=80, key="note_bd")
        dwg_bd      = st.text_input("Dwg/doc number", key="dwg_bd")

        # Campi extra diametri
        int_dia_bd  = st.number_input("Diametro interno (mm)", min_value=0, step=1, format="%d", key="int_dia_bd")
        ext_dia_bd  = st.number_input("Diametro esterno (mm)", min_value=0, step=1, format="%d", key="ext_dia_bd")

        mtype_bd    = st.selectbox("Material Type", [""] + material_types, key="mtype_bd")
        pref_df_bd  = materials_df[
            (materials_df["Material Type"] == mtype_bd) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bd = sorted(pref_df_bd["Prefix"].unique()) if mtype_bd != "MISCELLANEOUS" else []
        mprefix_bd  = st.selectbox("Material Prefix", [""] + prefixes_bd, key="mprefix_bd")

        if mtype_bd == "MISCELLANEOUS":
            names_bd = materials_df[materials_df["Material Type"] == mtype_bd]["Name"].dropna().tolist()
        else:
            names_bd = materials_df[
                (materials_df["Material Type"] == mtype_bd) &
                (materials_df["Prefix"] == mprefix_bd)
            ]["Name"].dropna().tolist()
        mname_bd = st.selectbox("Material Name", [""] + names_bd, key="mname_bd")

        if st.button("Genera Output", key="gen_bd"):
            materiale_bd = (
                f"{mtype_bd} {mprefix_bd} {mname_bd}".strip()
                if mtype_bd != "MISCELLANEOUS" else mname_bd
            )
            match_bd = materials_df[
                (materials_df["Material Type"] == mtype_bd) &
                (materials_df["Prefix"] == mprefix_bd) &
                (materials_df["Name"] == mname_bd)
            ]
            codice_fpd_bd = match_bd["FPD Code"].values[0] if not match_bd.empty else ""
            descr_bd = (
                f"BALANCE DRUM, PUMP - MODEL: {model_bd}, SIZE: {size_bd}, "
                f"ID: {int(int_dia_bd)}mm, OD: {int(int_dia_bd) + 2*int(ext_dia_bd)}mm, "
                f"FEATURES: {feature_1_bd}, {feature_2_bd}, NOTE: {note_bd}"
            )
            st.session_state["output_data"] = {
                "Item": "40227…",
                "Description": descr_bd,
                "Identificativo": "6231-BALANCE DRUM BUSH",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ARTVARI",
                "Disegno": dwg_bd,
                "Material": materiale_bd,
                "FPD material code": codice_fpd_bd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "16_BUSHING",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bd_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bd_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_bd = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bd_dl_mode")
        item_code_bd = st.text_input("Codice item", key="bd_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_bd"):
            if not item_code_bd:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_bd(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields_bd = [
                    "\\%FN", item_code_bd,
                    "\\%TC", get_val_bd("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_bd("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_bd("Identificativo"), "TAB",
                    get_val_bd("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_bd('ERP_L1')}.{get_val_bd('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_bd("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_bd("Catalog"), "TAB", "TAB", "TAB",
                    get_val_bd("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_bd("FPD material code"), "TAB",
                    get_val_bd("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_bd("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_bd("Quality") if get_val_bd("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_bd("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_bd("To supplier") if get_val_bd("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_bd = "\t".join(dataload_fields_bd)
                st.text_area("Anteprima (per copia manuale)", dataload_string_bd, height=200)
                csv_buffer_bd = io.StringIO()
                writer_bd = csv.writer(csv_buffer_bd, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_bd:
                    writer_bd.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_bd.getvalue(),
                    file_name=f"dataload_{item_code_bd}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- FLANGE, PIPE
elif selected_part == "Flange, Pipe":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        flange_type = st.selectbox("Type", ["SW", "BW"], key="flange_type")
        size_fp     = st.selectbox(
            "Size",
            ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'],
            key="flange_size"
        )
        face_type   = st.selectbox("Face Type", ["RF", "FF", "RJ"], key="flange_face")
        flange_cls  = st.selectbox("Class", ["150", "300", "600", "1500", "2500"], key="flange_class")
        if flange_cls in ["1500", "2500"] and face_type != "RJ":
            st.warning("Attenzione: per classi 1500 o 2500 è raccomandato l'uso di faccia tipo RJ. Verificare lo scopo di fornitura.")
        schedule_fp = st.selectbox(
            "Schedule",
            ["5","10","20","30","40","60","80","100","120","140","160"],
            key="flange_schedule"
        )
        flange_mat  = st.selectbox(
            "Flange Material",
            ["A105", "A106-GR B", "UNS-S31803", "UNS-S32760", "A350 LF2", "A182-F316L",
             "ALLOY 825", "GALVANIZED CARBON STEEL"],
            key="flange_material"
        )
        note_fp = st.text_area("Note (opzionale)", height=80, key="note_fp")
        dwg_fp  = st.text_input("Dwg/doc number", key="dwg_fp")
        if st.button("Genera Output", key="gen_flange"):
            descr_fp = (
                f"FLANGE, PIPE - TYPE: {flange_type}, SIZE: {size_fp}, "
                f"FACE TYPE: {face_type}, CLASS: {flange_cls}, SCHEDULE: {schedule_fp}, MATERIAL: {flange_mat}"
            )
            if note_fp:
                descr_fp += f", NOTE: {note_fp}"
            st.session_state["output_data"] = {
                "Item": "50155…",
                "Description": descr_fp,
                "Identificativo": "1245-FLANGE",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Material": "NOT AVAILABLE",
                "FPD material code": "BO-NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "23_FLANGE",
                "ERP_L2": "13_OTHER",
                "To supplier": "",
                "Quality": ""
            }
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"flange_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"flange_{campo}")
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_fp = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="fp_dl_mode")
        item_code_fp = st.text_input("Codice item", key="fp_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_fp"):
            if not item_code_fp:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_fp(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields_fp = [
                    "\\%FN", item_code_fp,
                    "\\%TC", get_val_fp("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_fp("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_fp("Identificativo"), "TAB",
                    get_val_fp("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_fp('ERP_L1')}.{get_val_fp('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_fp("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_fp("Catalog"), "TAB", "TAB", "TAB",
                    get_val_fp("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_fp("FPD material code"), "TAB",
                    get_val_fp("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_fp("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_fp("Quality") if get_val_fp("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_fp("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_fp("To supplier") if get_val_fp("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_fp = "\t".join(dataload_fields_fp)
                st.text_area("Anteprima (per copia manuale)", dataload_string_fp, height=200)
                csv_buffer_fp = io.StringIO()
                writer_fp = csv.writer(csv_buffer_fp, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_fp:
                    writer_fp.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",  
                    data=csv_buffer_fp.getvalue(),
                    file_name=f"dataload_{item_code_fp}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# (continua inserendo i restanti blocchi nello stesso formato)
