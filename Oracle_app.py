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

        # AVVISO EVIDENTE
        if flange_cls in ["1500", "2500"] and face_type != "RJ":
            st.markdown(
                "<div style='background-color:#ffe6e6; padding:1rem; border:2px solid #cc0000; border-radius:6px;'>"
                "<strong>⚠️ ATTENZIONE:</strong> Per classi <strong>1500</strong> o <strong>2500</strong> "
                "È <em>FORTEMENTE RACCOMANDATO</em> usare il tipo di faccia <strong>RJ</strong>.<br>"
                "Verificare lo scopo di fornitura prima di procedere."
                "</div>",
                unsafe_allow_html=True
            )

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
# --- BALANCE DISC, PUMP
elif selected_part == "Balance Disc, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model_bdsc     = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bdsc_model")
        size_list_bdsc = size_df[size_df["Pump Model"] == model_bdsc]["Size"].dropna().tolist()
        size_bdsc      = st.selectbox("Product/Pump Size", [""] + size_list_bdsc, key="bdsc_size")

        feature_1_bdsc = ""
        special_bdsc = ["HDO", "DMX", "WXB", "WIK"]
        if model_bdsc not in special_bdsc:
            f1_list_bdsc = features_df[
                (features_df["Pump Model"] == model_bdsc) & (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_bdsc = st.selectbox("Additional Feature 1", [""] + f1_list_bdsc, key="f1_bdsc")

        feature_2_bdsc = ""
        if model_bdsc in ["HPX", "HED"]:
            f2_list_bdsc = features_df[
                (features_df["Pump Model"] == model_bdsc) & (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2_bdsc = st.selectbox("Additional Feature 2", [""] + f2_list_bdsc, key="f2_bdsc")

        note_bdsc    = st.text_area("Note (opzionale)", height=80, key="note_bdsc")
        dwg_bdsc     = st.text_input("Dwg/doc number", key="dwg_bdsc")

        # Campi extra diametri
        int_dia_bdsc = st.number_input("Diametro interno (mm)", min_value=0, step=1, format="%d", key="int_dia_bdsc")
        ext_dia_bdsc = st.number_input("Diametro esterno (mm)", min_value=0, step=1, format="%d", key="ext_dia_bdsc")

        mtype_bdsc   = st.selectbox("Material Type", [""] + material_types, key="mtype_bdsc")
        pref_df_bdsc = materials_df[
            (materials_df["Material Type"] == mtype_bdsc) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bdsc = sorted(pref_df_bdsc["Prefix"].unique()) if mtype_bdsc != "MISCELLANEOUS" else []
        mprefix_bdsc  = st.selectbox("Material Prefix", [""] + prefixes_bdsc, key="mprefix_bdsc")

        if mtype_bdsc == "MISCELLANEOUS":
            names_bdsc = materials_df[materials_df["Material Type"] == mtype_bdsc]["Name"].dropna().tolist()
        else:
            names_bdsc = materials_df[
                (materials_df["Material Type"] == mtype_bdsc) &
                (materials_df["Prefix"] == mprefix_bdsc)
            ]["Name"].dropna().tolist()
        mname_bdsc = st.selectbox("Material Name", [""] + names_bdsc, key="mname_bdsc")

        if st.button("Genera Output", key="gen_bdsc"):
            materiale_bdsc = (
                f"{mtype_bdsc} {mprefix_bdsc} {mname_bdsc}".strip()
                if mtype_bdsc != "MISCELLANEOUS" else mname_bdsc
            )
            match_bdsc = materials_df[
                (materials_df["Material Type"] == mtype_bdsc) &
                (materials_df["Prefix"] == mprefix_bdsc) &
                (materials_df["Name"] == mname_bdsc)
            ]
            codice_fpd_bdsc = match_bdsc["FPD Code"].values[0] if not match_bdsc.empty else ""
            descr_bdsc = (
                f"BALANCE DISC, PUMP - MODEL: {model_bdsc}, SIZE: {size_bdsc}, "
                f"ID: {int(int_dia_bdsc)}mm, OD: {int(int_dia_bdsc) + 2*int(ext_dia_bdsc)}mm, "
                f"FEATURES: {feature_1_bdsc}, {feature_2_bdsc}, NOTE: {note_bdsc}"
            )
            st.session_state["output_data"] = {
                "Item": "40228…",
                "Description": descr_bdsc,
                "Identificativo": "6210-BALANCE DISC",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ARTVARI",
                "Disegno": dwg_bdsc,
                "Material": materiale_bdsc,
                "FPD material code": codice_fpd_bdsc,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "30_DISK",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bdsc_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bdsc_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_bdsc = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bdsc_dl_mode")
        item_code_bdsc = st.text_input("Codice item", key="bdsc_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_bdsc"):
            if not item_code_bdsc:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_bdsc(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields_bdsc = [
                    "\\%FN", item_code_bdsc,
                    "\\%TC", get_val_bdsc("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_bdsc("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_bdsc("Identificativo"), "TAB",
                    get_val_bdsc("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_bdsc('ERP_L1')}.{get_val_bdsc('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_bdsc("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_bdsc("Catalog"), "TAB", "TAB", "TAB",
                    get_val_bdsc("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_bdsc("FPD material code"), "TAB",
                    get_val_bdsc("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_bdsc("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_bdsc("Quality") if get_val_bdsc("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_bdsc("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_bdsc("To supplier") if get_val_bdsc("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_bdsc = "\t".join(dataload_fields_bdsc)
                st.text_area("Anteprima (per copia manuale)", dataload_string_bdsc, height=200)
                csv_buffer_bdsc = io.StringIO()
                writer_bdsc = csv.writer(csv_buffer_bdsc, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_bdsc:
                    writer_bdsc.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_bdsc.getvalue(),
                    file_name=f"dataload_{item_code_bdsc}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- GATE, VALVE
elif selected_part == "Gate, Valve":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        size_gate   = st.selectbox(
            "Size",
            ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'],
            key="gate_size"
        )
        pclass      = st.selectbox(
            "Pressure class",
            ["150", "300", "600", "1500", "2500"],
            key="gate_pressure"
        )
        inlet_type  = st.selectbox(
            "Inlet connection type",
            ["SW", "WN"],
            key="gate_inlet_type"
        )
        inlet_size  = st.selectbox(
            "Inlet connection size",
            ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'],
            key="gate_inlet_size"
        )
        outlet_type = st.selectbox(
            "Outlet connection type",
            ["SW", "WN"],
            key="gate_outlet_type"
        )
        outlet_size = st.selectbox(
            "Outlet connection size",
            ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'],
            key="gate_outlet_size"
        )
        valve_mat   = st.selectbox(
            "Valve material",
            [
                "A105", "A106-GR B", "UNS-S31803", "UNS-S32760", "A350 LF2", "A182-F316L",
                "ALLOY 825", "GALVANIZED CARBON STEEL"
            ],
            key="gate_material"
        )
        schedule_g  = st.selectbox(
            "Schedule",
            ["5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160"],
            key="gate_schedule"
        )
        note_gate   = st.text_area("Note (opzionale)", height=80, key="gate_note")
        dwg_gate    = st.text_input("Dwg/doc number", key="dwg_gate")

        if st.button("Genera Output", key="gen_gate"):
            descr_gate = (
                f"GATE, VALVE - SIZE: {size_gate}, CLASS: {pclass}, "
                f"INLET: {inlet_type}-{inlet_size}, OUTLET: {outlet_type}-{outlet_size}, "
                f"BODY MATERIAL: {valve_mat}, SCHEDULE: {schedule_g}"
            )
            if note_gate:
                descr_gate += f", NOTE: {note_gate}"
            st.session_state["output_data"] = {
                "Item": "50186…",
                "Description": descr_gate,
                "Identificativo": "VALVOLA (GLOBO,SARAC,SFERA,NEEDLE,MANIF,CONTR)",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Disegno": dwg_gate,
                "Material": "NOT AVAILABLE",
                "FPD material code": "BO-NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "72_VALVE",
                "ERP_L2": "18_GATE_VALVE",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"gate_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"gate_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_gate = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="gate_dl_mode")
        item_code_gate = st.text_input("Codice item", key="gate_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_gate"):
            if not item_code_gate:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_gate(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_gate = [
                    "\\%FN", item_code_gate,
                    "\\%TC", get_val_gate("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_gate("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_gate("Identificativo"), "TAB",
                    get_val_gate("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_gate('ERP_L1')}.{get_val_gate('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_gate("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_gate("Catalog"), "TAB", "TAB", "TAB",
                    get_val_gate("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_gate("FPD material code"), "TAB",
                    get_val_gate("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_gate("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_gate("Quality") if get_val_gate("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_gate("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_gate("To supplier") if get_val_gate("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_gate = "\t".join(dataload_fields_gate)
                st.text_area("Anteprima (per copia manuale)", dataload_string_gate, height=200)

                csv_buffer_gate = io.StringIO()
                writer_gate = csv.writer(csv_buffer_gate, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_gate:
                    writer_gate.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_gate.getvalue(),
                    file_name=f"dataload_{item_code_gate}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- GASKET, SPIRAL WOUND
elif selected_part == "Gasket, Spiral Wound":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        winding_colors = {
            "304 stainless steel": "Yellow RAL1021",
            "316L stainless steel": "Green RAL6005",
            "317L stainless steel": "Maroon RAL3003",
            "321 stainless steel": "Turquoise RAL5018",
            "347 stainless steel": "Blue RAL5017",
            "MONEL": "Orange RAL2003",
            "Nickel": "Red RAL3024",
            "Titanium": "Purple RAL4003",
            "Alloy20": "Black RAL9005",
            "INCONEL 600": "Gold RAL1004",
            "HASTELLOY B": "Brown RAL8003",
            "HASTELLOY C": "Beige RAL1001",
            "INCOLOY800": "White RAL9010",
            "DUPLEX": "Yellow+Blue RAL1021+5017",
            "SUPERDUPLEX": "Red+Black RAL3024+9005",
            "ALLOY 825": "Orange+Green RAL2003+6005",
            "UNS S31254": "Orange+Blue RAL2003+5017",
            "ZYRCONIUM 702": "Gold+Green RAL1004+6005",
            "INCONEL X750HT": "Gold+Black RAL1004+9005"
        }
        filler_colors = {
            "Graphite": "Gray RAL7011",
            "PTFE": "White RAL9010",
            "Ceramic": "Ceramic Lt. Green RAL6021",
            "Verdicarb (Mica Graphite)": "Pink RAL3015"
        }
        rating_stripes = {
            "STANDARD PRESSURE m=3 y=10000 psi": "(1 stripe)",
            "HIGH PRESSURE m=3 y=17500 psi": "(2 stripes)",
            "ULTRA HIGH PRESSURE m=3 y=23500 psi": "(3 stripes)"
        }

        winding   = st.selectbox("Winding material", list(winding_colors.keys()), key="winding_sw")
        filler    = st.selectbox("Filler", list(filler_colors.keys()), key="filler_sw")
        inner_dia = st.number_input("Diametro interno (mm)", min_value=0.0, step=0.1, format="%.1f", key="inner_dia_sw")
        outer_dia = st.number_input("Diametro esterno (mm)", min_value=0.0, step=0.1, format="%.1f", key="outer_dia_sw")
        thickness = st.number_input("Spessore (mm)", min_value=0.0, step=0.1, format="%.1f", key="thickness_sw")
        rating    = st.selectbox("Rating", list(rating_stripes.keys()), key="rating_sw")
        dwg_sw    = st.text_input("Dwg/doc number", key="dwg_sw")
        note_sw   = st.text_area("Note (opzionale)", height=80, key="note_sw")

        if st.button("Genera Output", key="gen_sw"):
            c1     = winding_colors[winding]
            c2     = filler_colors[filler]
            stripe = rating_stripes[rating]
            descr_sw = (
                f"GASKET, SPIRAL WOUND - WINDING: {winding}, FILLER: {filler}, "
                f"ID: {inner_dia}mm, OD: {outer_dia}mm, THK: {thickness}mm, "
                f"RATING: {rating}, COLOR CODE: {c1}/{c2}, {stripe}"
            )
            if note_sw:
                descr_sw += f", NOTE: {note_sw}"

            st.session_state["output_data"] = {
                "Item": "50415…",
                "Description": descr_sw,
                "Identificativo": "4510-JOINT",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_sw,
                "Material": "NA",
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_1",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "16_SPIRAL_WOUND",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"sw_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"sw_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_sw = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="sw_dl_mode")
        item_code_sw = st.text_input("Codice item", key="sw_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_sw"):
            if not item_code_sw:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_sw(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_sw = [
                    "\\%FN", item_code_sw,
                    "\\%TC", get_val_sw("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_sw("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_sw("Identificativo"), "TAB",
                    get_val_sw("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_sw('ERP_L1')}.{get_val_sw('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_sw("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_sw("Catalog"), "TAB", "TAB", "TAB",
                    get_val_sw("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_sw("FPD material code"), "TAB",
                    get_val_sw("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_sw("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_sw("Quality") if get_val_sw("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_sw("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_sw("To supplier") if get_val_sw("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_sw = "\t".join(dataload_fields_sw)
                st.text_area("Anteprima (per copia manuale)", dataload_string_sw, height=200)

                csv_buffer_sw = io.StringIO()
                writer_sw = csv.writer(csv_buffer_sw, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_sw:
                    writer_sw.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_sw.getvalue(),
                    file_name=f"dataload_{item_code_sw}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BEARING, HYDROSTATIC/HYDRODYNAMIC
elif selected_part == "Bearing, Hydrostatic/Hydrodynamic":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        ins_dia        = st.number_input("InsDia (mm)", min_value=0.0, step=0.1, format="%.1f", key="insdia_bearing")
        out_dia        = st.number_input("OutDia (mm)", min_value=0.0, step=0.1, format="%.1f", key="outdia_bearing")
        width          = st.number_input("Width (mm)", min_value=0.0, step=0.1, format="%.1f", key="width_bearing")
        add_feat       = st.text_input("Additional Features", key="feat_bearing")
        dwg_bearing    = st.text_input("Dwg/doc number", key="dwg_bearing")
        
        mtype_bearing  = st.selectbox("Material Type", [""] + material_types, key="mtype_bearing")
        pref_df_bearing = materials_df[
            (materials_df["Material Type"] == mtype_bearing) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bearing = sorted(pref_df_bearing["Prefix"].unique()) if mtype_bearing != "MISCELLANEOUS" else []
        mprefix_bearing = st.selectbox("Prefix (only if ASTM or EN)", [""] + prefixes_bearing, key="mprefix_bearing")
        
        if mtype_bearing == "MISCELLANEOUS":
            names_bearing = materials_df[materials_df["Material Type"] == mtype_bearing]["Name"].dropna().tolist()
        else:
            names_bearing = materials_df[
                (materials_df["Material Type"] == mtype_bearing) &
                (materials_df["Prefix"] == mprefix_bearing)
            ]["Name"].dropna().tolist()
        mname_bearing    = st.selectbox("Name", [""] + names_bearing, key="mname_bearing")
        
        mat_feat_bearing = st.text_input("Material add. Features", key="matfeat_bearing")

        if st.button("Genera Output", key="gen_bearing"):
            if mtype_bearing != "MISCELLANEOUS":
                materiale_b = f"{mtype_bearing} {mprefix_bearing} {mname_bearing}".strip()
                match_b     = materials_df[
                    (materials_df["Material Type"] == mtype_bearing) &
                    (materials_df["Prefix"] == mprefix_bearing) &
                    (materials_df["Name"] == mname_bearing)
                ]
            else:
                materiale_b = mname_bearing
                match_b     = materials_df[
                    (materials_df["Material Type"] == mtype_bearing) &
                    (materials_df["Name"] == mname_bearing)
                ]
            codice_fpd_b = match_b["FPD Code"].values[0] if not match_b.empty else ""
            
            descr_b = (
                f"BEARING, HYDROSTATIC/HYDRODYNAMIC - InsDia: {ins_dia}mm, OutDia: {out_dia}mm, "
                f"Width: {width}mm"
            )
            if add_feat:
                descr_b += f", {add_feat}"
            descr_b += f", Material: {materiale_b}"
            if mat_feat_bearing:
                descr_b += f", {mat_feat_bearing}"
            
            st.session_state["output_data"] = {
                "Item":               "50122…",
                "Description":        descr_b,
                "Identificativo":     "3010-ANTI-FRICTION BEARING",
                "Classe ricambi":     "1-2-3",
                "Categories":         "FASCIA ITE 5",
                "Catalog":            "ALBERO",
                "Disegno":            dwg_bearing,
                "Material":           materiale_b,
                "FPD material code":  codice_fpd_b,
                "Template":           "FPD_BUY_1",
                "ERP_L1":             "31_COMMERCIAL_BEARING",
                "ERP_L2":             "18_OTHER",
                "To supplier":        "",
                "Quality":            ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bear_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bear_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_bear = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bear_dl_mode")
        item_code_bear = st.text_input("Codice item", key="bear_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_bear"):
            if not item_code_bear:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_bear(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_bear = [
                    "\\%FN", item_code_bear,
                    "\\%TC", get_val_bear("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_bear("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_bear("Identificativo"), "TAB",
                    get_val_bear("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_bear('ERP_L1')}.{get_val_bear('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_bear("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_bear("Catalog"), "TAB", "TAB", "TAB",
                    get_val_bear("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_bear("FPD material code"), "TAB",
                    get_val_bear("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_bear("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_bear("Quality") if get_val_bear("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_bear("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_bear("To supplier") if get_val_bear("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_bear = "\t".join(dataload_fields_bear)
                st.text_area("Anteprima (per copia manuale)", dataload_string_bear, height=200)

                csv_buffer_bear = io.StringIO()
                writer_bear = csv.writer(csv_buffer_bear, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_bear:
                    writer_bear.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_bear.getvalue(),
                    file_name=f"dataload_{item_code_bear}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BEARING, ROLLING
elif selected_part == "Bearing, Rolling":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        type_options  = [
            "ANGULAR_CONTACT_BEARING",
            "BALL_BEARING",
            "ROLLER_BEARING",
            "TAPERED_BEARING",
            "ANTIFRICTION_THRUST_BEARING",
            "OTHER"
        ]
        bearing_type  = st.selectbox("Type", type_options, key="rolling_type")
        designation   = st.text_input("Designation", key="rolling_designation")
        ins_dia_r     = st.number_input("InsDia (mm)", min_value=0.0, step=0.1, format="%.1f", key="insdia_rolling")
        out_dia_r     = st.number_input("OutDia (mm)", min_value=0.0, step=0.1, format="%.1f", key="outdia_rolling")
        width_r       = st.number_input("Width (mm)", min_value=0.0, step=0.1, format="%.1f", key="width_rolling")
        add_feat_r    = st.text_input("Additional Features", key="feat_rolling")
        dwg_rolling   = st.text_input("Dwg/doc number", key="dwg_rolling")
        if st.button("Genera Output", key="gen_rolling"):
            descr_rolling = (
                f"BEARING, ROLLING - TYPE: {bearing_type}, DESIGNATION: {designation}, "
                f"InsDia: {ins_dia_r}mm, OutDia: {out_dia_r}mm, Width: {width_r}mm"
            )
            if add_feat_r:
                descr_rolling += f", {add_feat_r}"
            st.session_state["output_data"] = {
                "Item":               "50122…",
                "Description":        descr_rolling,
                "Identificativo":     "3010-ANTI-FRICTION BEARING",
                "Classe ricambi":     "1-2-3",
                "Categories":         "FASCIA ITE 5",
                "Catalog":            "ALBERO",
                "Disegno":            dwg_rolling,
                "Material":           "BUY OUT NOT AVAILABLE",
                "FPD material code":  "BO-NA",
                "Template":           "FPD_BUY_2",
                "ERP_L1":             "31_COMMERCIAL_BEARING",
                "ERP_L2":             "11_BALL_BEARING",
                "To supplier":        "",
                "Quality":            ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"rolling_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"rolling_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_rolling = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="rolling_dl_mode")
        item_code_rolling    = st.text_input("Codice item", key="rolling_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_rolling"):
            if not item_code_rolling:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_rolling(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_rolling = [
                    "\\%FN", item_code_rolling,
                    "\\%TC", get_val_rolling("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_rolling("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_rolling("Identificativo"), "TAB",
                    get_val_rolling("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_rolling('ERP_L1')}.{get_val_rolling('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_rolling("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_rolling("Catalog"), "TAB", "TAB", "TAB",
                    get_val_rolling("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_rolling("FPD material code"), "TAB",
                    get_val_rolling("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_rolling("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_rolling("Quality") if get_val_rolling("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_rolling("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_rolling("To supplier") if get_val_rolling("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_rolling = "\t".join(dataload_fields_rolling)
                st.text_area("Anteprima (per copia manuale)", dataload_string_rolling, height=200)

                csv_buffer_rolling = io.StringIO()
                writer_rolling = csv.writer(csv_buffer_rolling, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_rolling:
                    writer_rolling.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_rolling.getvalue(),
                    file_name=f"dataload_{item_code_rolling}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BOLT, EYE
elif selected_part == "Bolt, Eye":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        thread_be = st.selectbox(
            "Thread type/size",
            [
                "#10-24UNC", "5/16\"-18UNC", "3/8\"-16UNC", "1/2\"-13UNC", "3/4\"-16UNF",
                "7/8\"-9UNC", "7/8\"-14UNF", "1\"-12UNF", "1-1/8\"-12UNF", "1-1/2\"-12UNC",
                "2\"-4.5UNC", "2-1/2\"-4UNC", "3\"-6UNC", "4\"-8UNC",
                "M6x1", "M8x1.25", "M10x1.5", "M12x1.75", "M16x2", "M20x2.5", "M24x3",
                "M30x3.5", "M36x4", "M42x4.5", "M48x5", "M56x5.5", "M64x6", "M72x6",
                "M80x6", "M90x6", "M100x6"
            ],
            key="be_thread"
        )
        length_be = st.selectbox(
            "Length",
            [
                "1/8\"in", "1/4\"in", "3/8\"in", "5/16\"in", "1/2\"in", "3/4\"in",
                "1\"in", "1-1/8\"in", "1-1/4\"in", "1-3/8\"in", "1-1/2\"in", "2\"in",
                "2-1/8\"in", "2-1/4\"in", "2-3/8\"in", "2-1/2\"in", "2-3/4\"in",
                "3\"in", "3-1/8\"in", "3-1/4\"in", "3-3/8\"in", "3-1/2\"in", "4\"in",
                "4-1/8\"in", "4-1/4\"in", "4-3/8\"in", "4-1/2\"in",
                "50mm", "55mm", "60mm", "65mm", "70mm", "75mm", "80mm", "85mm", "90mm", "95mm",
                "100mm", "105mm", "110mm", "115mm", "120mm", "125mm", "130mm", "135mm", "140mm",
                "145mm", "150mm", "155mm", "160mm", "165mm", "170mm", "175mm", "180mm", "185mm",
                "190mm", "195mm"
            ],
            key="be_length"
        )
        note1_be = st.text_area("Note (opzionale)", height=80, key="be_note1")

        mtype_be = st.selectbox("Material Type", [""] + material_types, key="be_mtype")
        pref_df_be = materials_df[
            (materials_df["Material Type"] == mtype_be) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_be = sorted(pref_df_be["Prefix"].unique()) if mtype_be != "MISCELLANEOUS" else []
        mprefix_be = st.selectbox("Material Prefix", [""] + prefixes_be, key="be_mprefix")

        if mtype_be == "MISCELLANEOUS":
            names_be = materials_df[materials_df["Material Type"] == mtype_be]["Name"].dropna().tolist()
        else:
            names_be = materials_df[
                (materials_df["Material Type"] == mtype_be) &
                (materials_df["Prefix"] == mprefix_be)
            ]["Name"].dropna().tolist()
        mname_be = st.selectbox("Material Name", [""] + names_be, key="be_mname")

        note2_be = st.text_area("Material Note (opzionale)", height=80, key="be_note2")

        if st.button("Genera Output", key="gen_be"):
            if mtype_be != "MISCELLANEOUS":
                materiale_be = f"{mtype_be} {mprefix_be} {mname_be}".strip()
                match_be = materials_df[
                    (materials_df["Material Type"] == mtype_be) &
                    (materials_df["Prefix"] == mprefix_be) &
                    (materials_df["Name"] == mname_be)
                ]
            else:
                materiale_be = mname_be
                match_be = materials_df[
                    (materials_df["Material Type"] == mtype_be) &
                    (materials_df["Name"] == mname_be)
                ]
            codice_fpd_be = match_be["FPD Code"].values[0] if not match_be.empty else ""

            descr_be = f"BOLT, EYE - THREAD: {thread_be}, LENGTH: {length_be}"
            if note1_be:
                descr_be += f", {note1_be}"
            descr_be += f", {materiale_be}"
            if note2_be:
                descr_be += f", {note2_be}"

            st.session_state["output_data"] = {
                "Item": "50150…",
                "Description": descr_be,
                "Identificativo": "6583-EYE BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Material": materiale_be,
                "FPD material code": codice_fpd_be,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FASTENING_COMPONENTS_EYE_NUTS_LOCK_NUTS_ETC",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"be_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"be_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_be = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="be_dl_mode")
        item_code_be = st.text_input("Codice item", key="be_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_be"):
            if not item_code_be:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_be(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_be = [
                    "\\%FN", item_code_be,
                    "\\%TC", get_val_be("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_be("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_be("Identificativo"), "TAB",
                    get_val_be("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_be('ERP_L1')}.{get_val_be('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_be("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_be("Catalog"), "TAB", "TAB", "TAB",
                    get_val_be("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_be("FPD material code"), "TAB",
                    get_val_be("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_be("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_be("Quality") if get_val_be("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_be("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_be("To supplier") if get_val_be("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_be = "\t".join(dataload_fields_be)
                st.text_area("Anteprima (per copia manuale)", dataload_string_be, height=200)

                csv_buffer_be = io.StringIO()
                writer_be = csv.writer(csv_buffer_be, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_be:
                    writer_be.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_be.getvalue(),
                    file_name=f"dataload_{item_code_be}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BOLT, HEXAGONAL
elif selected_part == "Bolt, Hexagonal":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        size_hex   = st.selectbox(
            "Size",
            bolt_sizes,  # utilizza la lista bolt_sizes già definita in alto
            key="hex_size"
        )
        length_hex = st.selectbox(
            "Length",
            bolt_lengths,  # utilizza la lista bolt_lengths già definita in alto
            key="hex_length"
        )
        full_thd   = st.radio("Full threaded?", ["Yes", "No"], horizontal=True, key="hex_fullthread")
        zinc       = st.radio("Zinc Plated?", ["Yes", "No"], horizontal=True, key="hex_zinc")
        note1_hex  = st.text_area("Note (opzionale)", height=80, key="hex_note1")

        mtype_hex = st.selectbox("Material Type", [""] + material_types, key="mtype_hex")
        pref_df_hex = materials_df[
            (materials_df["Material Type"] == mtype_hex) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_hex = sorted(pref_df_hex["Prefix"].unique()) if mtype_hex != "MISCELLANEOUS" else []
        mprefix_hex  = st.selectbox("Material Prefix", [""] + prefixes_hex, key="hex_mprefix")

        if mtype_hex == "MISCELLANEOUS":
            names_hex = materials_df[materials_df["Material Type"] == mtype_hex]["Name"].dropna().tolist()
        else:
            names_hex = materials_df[
                (materials_df["Material Type"] == mtype_hex) &
                (materials_df["Prefix"] == mprefix_hex)
            ]["Name"].dropna().tolist()
        mname_hex = st.selectbox("Material Name", [""] + names_hex, key="hex_mname")

        note2_hex = st.text_area("Material Note (opzionale)", height=80, key="hex_note2")

        if st.button("Genera Output", key="gen_hex"):
            if mtype_hex != "MISCELLANEOUS":
                materiale_hex = f"{mtype_hex} {mprefix_hex} {mname_hex}".strip()
                match_hex = materials_df[
                    (materials_df["Material Type"] == mtype_hex) &
                    (materials_df["Prefix"] == mprefix_hex) &
                    (materials_df["Name"] == mname_hex)
                ]
            else:
                materiale_hex = mname_hex
                match_hex = materials_df[
                    (materials_df["Material Type"] == mtype_hex) &
                    (materials_df["Name"] == mname_hex)
                ]
            codice_fpd_hex = match_hex["FPD Code"].values[0] if not match_hex.empty else ""

            descr_hex = f"BOLT, HEXAGONAL - SIZE: {size_hex}, LENGTH: {length_hex}"
            if full_thd == "Yes":
                descr_hex += ", FULL THREADED"
            if zinc == "Yes":
                descr_hex += ", ZINC PLATED AS PER ASTM B633"
            if note1_hex:
                descr_hex += f", {note1_hex}"
            descr_hex += f", {materiale_hex}"
            if note2_hex:
                descr_hex += f", {note2_hex}"

            st.session_state["output_data"] = {
                "Item": "56230…",
                "Description": descr_hex,
                "Identificativo": "6577-HEXAGON HEAD BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Material": materiale_hex,
                "FPD material code": codice_fpd_hex,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "10_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"hex_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"hex_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_hex = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="hex_dl_mode")
        item_code_hex = st.text_input("Codice item", key="hex_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_hex"):
            if not item_code_hex:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_hex(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_hex = [
                    "\\%FN", item_code_hex,
                    "\\%TC", get_val_hex("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_hex("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_hex("Identificativo"), "TAB",
                    get_val_hex("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_hex('ERP_L1')}.{get_val_hex('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_hex("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_hex("Catalog"), "TAB", "TAB", "TAB",
                    get_val_hex("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_hex("FPD material code"), "TAB",
                    get_val_hex("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_hex("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_hex("Quality") if get_val_hex("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_hex("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_hex("To supplier") if get_val_hex("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_hex = "\t".join(dataload_fields_hex)
                st.text_area("Anteprima (per copia manuale)", dataload_string_hex, height=200)

                csv_buffer_hex = io.StringIO()
                writer_hex = csv.writer(csv_buffer_hex, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_hex:
                    writer_hex.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_hex.getvalue(),
                    file_name=f"dataload_{item_code_hex}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- GASKET, RING TYPE JOINT
elif selected_part == "Gasket, Ring Type Joint":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        rtj_type = st.selectbox(
            "Type",
            ["Oval", "Octagonal"],
            key="rtj_type"
        )
        rtj_size = st.selectbox(
            "Size",
            [f"R{i}" for i in range(11, 61)],
            key="rtj_size"
        )
        note1_rtj = st.text_area(
            "Note (opzionale)",
            height=80,
            key="rtj_note1"
        )

        mtype_rtj = st.selectbox(
            "Material Type",
            [""] + material_types,
            key="mtype_rtj"
        )
        pref_df_rtj = materials_df[
            (materials_df["Material Type"] == mtype_rtj) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_rtj = sorted(pref_df_rtj["Prefix"].unique()) if mtype_rtj != "MISCELLANEOUS" else []
        mprefix_rtj = st.selectbox(
            "Material Prefix",
            [""] + prefixes_rtj,
            key="mprefix_rtj"
        )

        if mtype_rtj == "MISCELLANEOUS":
            names_rtj = materials_df[
                materials_df["Material Type"] == mtype_rtj
            ]["Name"].dropna().tolist()
        else:
            names_rtj = materials_df[
                (materials_df["Material Type"] == mtype_rtj) &
                (materials_df["Prefix"] == mprefix_rtj)
            ]["Name"].dropna().tolist()
        mname_rtj = st.selectbox(
            "Material Name",
            [""] + names_rtj,
            key="mname_rtj"
        )

        note2_rtj = st.text_area(
            "Material Note (opzionale)",
            height=80,
            key="rtj_note2"
        )

        if st.button("Genera Output", key="gen_rtj"):
            if mtype_rtj != "MISCELLANEOUS":
                materiale_rtj = f"{mtype_rtj} {mprefix_rtj} {mname_rtj}".strip()
                match_rtj = materials_df[
                    (materials_df["Material Type"] == mtype_rtj) &
                    (materials_df["Prefix"] == mprefix_rtj) &
                    (materials_df["Name"] == mname_rtj)
                ]
            else:
                materiale_rtj = mname_rtj
                match_rtj = materials_df[
                    (materials_df["Material Type"] == mtype_rtj) &
                    (materials_df["Name"] == mname_rtj)
                ]
            codice_fpd_rtj = match_rtj["FPD Code"].values[0] if not match_rtj.empty else ""

            descr_rtj = f"GASKET, RING TYPE JOINT - TYPE: {rtj_type}, SIZE: {rtj_size}"
            if note1_rtj:
                descr_rtj += f", {note1_rtj}"
            descr_rtj += f", {materiale_rtj}"
            if note2_rtj:
                descr_rtj += f", {note2_rtj}"

            st.session_state["output_data"] = {
                "Item": "50158…",
                "Description": descr_rtj,
                "Identificativo": "ANELLO SFERICO RING JOINT",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Material": materiale_rtj,
                "FPD material code": codice_fpd_rtj,
                "Template": "FPD_BUY_2",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "Disegno": "",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"rtj_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"rtj_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_rtj = st.radio(
            "Tipo operazione:",
            ["Crea nuovo item", "Aggiorna item"],
            key="rtj_dl_mode"
        )
        item_code_rtj = st.text_input(
            "Codice item",
            key="rtj_item_code"
        )

        if st.button("Genera stringa DataLoad", key="gen_dl_rtj"):
            if not item_code_rtj:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_rtj(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_rtj = [
                    "\\%FN", item_code_rtj,
                    "\\%TC", get_val_rtj("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_rtj("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_rtj("Identificativo"), "TAB",
                    get_val_rtj("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_rtj('ERP_L1')}.{get_val_rtj('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_rtj("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_rtj("Catalog"), "TAB", "TAB", "TAB",
                    get_val_rtj("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_rtj("FPD material code"), "TAB",
                    get_val_rtj("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_rtj("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_rtj("Quality") if get_val_rtj("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_rtj("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_rtj("To supplier") if get_val_rtj("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_rtj = "\t".join(dataload_fields_rtj)
                st.text_area("Anteprima (per copia manuale)", dataload_string_rtj, height=200)

                csv_buffer_rtj = io.StringIO()
                writer_rtj = csv.writer(csv_buffer_rtj, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_rtj:
                    writer_rtj.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_rtj.getvalue(),
                    file_name=f"dataload_{item_code_rtj}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- GUSSET, OTHER
elif selected_part == "Gusset, Other":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        width_gusset    = st.number_input("Width", min_value=0, step=1, format="%d", key="gusset_width")
        thickness_gusset = st.number_input("Thickness", min_value=0, step=1, format="%d", key="gusset_thickness")
        uom_gusset      = st.selectbox("Unità di misura", ["mm", "inches"], key="gusset_uom")
        note1_gusset    = st.text_area("Note (opzionale)", height=80, key="gusset_note1")

        mtype_gusset    = st.selectbox("Material Type", [""] + material_types, key="mtype_gusset")
        pref_df_gusset  = materials_df[
            (materials_df["Material Type"] == mtype_gusset) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_gusset = sorted(pref_df_gusset["Prefix"].unique()) if mtype_gusset != "MISCELLANEOUS" else []
        mprefix_gusset  = st.selectbox("Material Prefix", [""] + prefixes_gusset, key="mprefix_gusset")

        if mtype_gusset == "MISCELLANEOUS":
            names_gusset = materials_df[materials_df["Material Type"] == mtype_gusset]["Name"].dropna().tolist()
        else:
            names_gusset = materials_df[
                (materials_df["Material Type"] == mtype_gusset) &
                (materials_df["Prefix"] == mprefix_gusset)
            ]["Name"].dropna().tolist()
        mname_gusset   = st.selectbox("Material Name", [""] + names_gusset, key="mname_gusset")

        note2_gusset   = st.text_area("Material Note (opzionale)", height=80, key="gusset_note2")

        if st.button("Genera Output", key="gen_gusset"):
            if mtype_gusset != "MISCELLANEOUS":
                materiale_gusset = f"{mtype_gusset} {mprefix_gusset} {mname_gusset}".strip()
                match_gusset     = materials_df[
                    (materials_df["Material Type"] == mtype_gusset) &
                    (materials_df["Prefix"] == mprefix_gusset) &
                    (materials_df["Name"] == mname_gusset)
                ]
            else:
                materiale_gusset = mname_gusset
                match_gusset     = materials_df[
                    (materials_df["Material Type"] == mtype_gusset) &
                    (materials_df["Name"] == mname_gusset)
                ]
            codice_fpd_gusset = match_gusset["FPD Code"].values[0] if not match_gusset.empty else ""

            descr_gusset = (
                f"GUSSET, OTHER - WIDTH: {int(width_gusset)}{uom_gusset}, "
                f"THK: {int(thickness_gusset)}{uom_gusset}"
            )
            if note1_gusset:
                descr_gusset += f", {note1_gusset}"
            descr_gusset += f", {materiale_gusset}"
            if note2_gusset:
                descr_gusset += f", {note2_gusset}"

            st.session_state["output_data"] = {
                "Item": "565G…",
                "Description": descr_gusset,
                "Identificativo": "GUSSETING",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_gusset,
                "FPD material code": codice_fpd_gusset,
                "Template": "FPD_BUY_1",
                "ERP_L1": "21_FABRICATION_OR_BASEPLATES",
                "ERP_L2": "29_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"gusset_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"gusset_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_gusset = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="gusset_dl_mode")
        item_code_gusset     = st.text_input("Codice item", key="gusset_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_gusset"):
            if not item_code_gusset:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_gusset(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_gusset = [
                    "\\%FN", item_code_gusset,
                    "\\%TC", get_val_gusset("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_gusset("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_gusset("Identificativo"), "TAB",
                    get_val_gusset("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_gusset('ERP_L1')}.{get_val_gusset('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_gusset("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_gusset("Catalog"), "TAB", "TAB", "TAB",
                    get_val_gusset("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_gusset("FPD material code"), "TAB",
                    get_val_gusset("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_gusset("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_gusset("Quality") if get_val_gusset("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_gusset("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_gusset("To supplier") if get_val_gusset("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_gusset = "\t".join(dataload_fields_gusset)
                st.text_area("Anteprima (per copia manuale)", dataload_string_gusset, height=200)

                csv_buffer_gusset = io.StringIO()
                writer_gusset     = csv.writer(csv_buffer_gusset, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_gusset:
                    writer_gusset.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_gusset.getvalue(),
                    file_name=f"dataload_{item_code_gusset}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- STUD, THREADED
elif selected_part == "Stud, Threaded":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        threaded_type = st.selectbox(
            "Threaded",
            ["Partial", "Full"],
            key="stud_threaded"
        )

        stud_sizes = [
            "#10-24UNC", "5/16\"-18UNC", "3/8\"-16UNC", "1/2\"-13UNC",
            "3/4\"-16UNF", "7/8\"-9UNC", "7/8\"-14UNF", "1\"-12UNF",
            "1-1/8\"-12UNF", "1-1/2\"-12UNC", "2\"-4.5UNC", "2-1/2\"-4UNC",
            "3\"-6UNC", "4\"-8UNC", "M6x1", "M8x1.25", "M10x1.5", "M12x1.75",
            "M16x2", "M20x2.5", "M24x3", "M30x3.5", "M36x4", "M42x4.5",
            "M48x5", "M56x5.5", "M64x6", "M72x6", "M80x6", "M90x6", "M100x6"
        ]

        size_stud   = st.selectbox("Size", stud_sizes, key="stud_size")
        length_stud = st.selectbox(
            "Length",
            [
                "1/8\"in", "1/4\"in", "3/8\"in", "5/16\"in", "1/2\"in",
                "3/4\"in", "1\"in", "1-1/8\"in", "1-1/4\"in", "1-3/8\"in",
                "1-1/2\"in", "2\"in", "2-1/8\"in", "2-1/4\"in", "2-3/8\"in",
                "2-1/2\"in", "2-3/4\"in", "3\"in", "3-1/8\"in", "3-1/4\"in",
                "3-3/8\"in", "3-1/2\"in", "4\"in", "4-1/8\"in", "4-1/4\"in",
                "4-3/8\"in", "4-1/2\"in", "50mm", "55mm", "60mm", "65mm",
                "70mm", "75mm", "80mm", "85mm", "90mm", "95mm", "100mm",
                "105mm", "110mm", "115mm", "120mm", "125mm", "130mm",
                "135mm", "140mm", "145mm", "150mm", "155mm", "160mm",
                "165mm", "170mm", "175mm", "180mm", "185mm", "190mm",
                "195mm"
            ],
            key="stud_length"
        )
        note1_stud = st.text_area("Note (opzionale)", height=80, key="stud_note1")
        dwg_stud   = st.text_input("Dwg/doc number", key="stud_dwg")

        mtype_stud = st.selectbox("Material Type", [""] + material_types, key="mtype_stud")
        pref_df_stud = materials_df[
            (materials_df["Material Type"] == mtype_stud) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_stud = sorted(pref_df_stud["Prefix"].unique()) if mtype_stud != "MISCELLANEOUS" else []
        mprefix_stud  = st.selectbox("Material Prefix", [""] + prefixes_stud, key="mprefix_stud")

        if mtype_stud == "MISCELLANEOUS":
            names_stud = materials_df[
                materials_df["Material Type"] == mtype_stud
            ]["Name"].dropna().tolist()
        else:
            names_stud = materials_df[
                (materials_df["Material Type"] == mtype_stud) &
                (materials_df["Prefix"] == mprefix_stud)
            ]["Name"].dropna().tolist()
        mname_stud = st.selectbox("Material Name", [""] + names_stud, key="mname_stud")

        note2_stud = st.text_area("Material Note (opzionale)", height=80, key="stud_note2")

        if st.button("Genera Output", key="gen_stud"):
            if mtype_stud != "MISCELLANEOUS":
                materiale_stud = f"{mtype_stud} {mprefix_stud} {mname_stud}".strip()
                match_stud = materials_df[
                    (materials_df["Material Type"] == mtype_stud) &
                    (materials_df["Prefix"] == mprefix_stud) &
                    (materials_df["Name"] == mname_stud)
                ]
            else:
                materiale_stud = mname_stud
                match_stud = materials_df[
                    (materials_df["Material Type"] == mtype_stud) &
                    (materials_df["Name"] == mname_stud)
                ]
            codice_fpd_stud = match_stud["FPD Code"].values[0] if not match_stud.empty else ""

            descr_stud = (
                f"STUD, THREADED - THREAD: {threaded_type}, SIZE: {size_stud}, LENGTH: {length_stud}"
            )
            if note1_stud:
                descr_stud += f", {note1_stud}"
            descr_stud += f", {materiale_stud}"
            if note2_stud:
                descr_stud += f", {note2_stud}"

            st.session_state["output_data"] = {
                "Item": "56146…",
                "Description": descr_stud,
                "Identificativo": "6572-STUD",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_stud,
                "Material": materiale_stud,
                "FPD material code": codice_fpd_stud,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "12_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"stud_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"stud_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_stud = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="stud_dl_mode")
        item_code_stud     = st.text_input("Codice item", key="stud_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_stud"):
            if not item_code_stud:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_stud(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_stud = [
                    "\\%FN", item_code_stud,
                    "\\%TC", get_val_stud("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_stud("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_stud("Identificativo"), "TAB",
                    get_val_stud("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_stud('ERP_L1')}.{get_val_stud('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_stud("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_stud("Catalog"), "TAB", "TAB", "TAB",
                    get_val_stud("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_stud("FPD material code"), "TAB",
                    get_val_stud("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_stud("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_stud("Quality") if get_val_stud("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_stud("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_stud("To supplier") if get_val_stud("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_stud = "\t".join(dataload_fields_stud)
                st.text_area("Anteprima (per copia manuale)", dataload_string_stud, height=200)

                csv_buffer_stud = io.StringIO()
                writer_stud     = csv.writer(csv_buffer_stud, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_stud:
                    writer_stud.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_stud.getvalue(),
                    file_name=f"dataload_{item_code_stud}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- NUT, HEX
elif selected_part == "Nut, Hex":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        nut_type = "Heavy"  # fisso, non modificabile
        st.markdown(f"**Type:** {nut_type}")
        nut_sizes = [
            "#10-24UNC", "5/16\"-18UNC", "3/8\"-16UNC", "1/2\"-13UNC",
            "3/4\"-16UNF", "7/8\"-9UNC", "7/8\"-14UNF", "1\"-12UNF",
            "1-1/8\"-12UNF", "1-1/2\"-12UNC", "2\"-4.5UNC", "2-1/2\"-4UNC",
            "3\"-6UNC", "4\"-8UNC", "M6x1", "M8x1.25", "M10x1.5", "M12x1.75",
            "M16x2", "M20x2.5", "M24x3", "M30x3.5", "M36x4", "M42x4.5",
            "M48x5", "M56x5.5", "M64x6", "M72x6", "M80x6", "M90x6", "M100x6"
        ]
        size_nut = st.selectbox("Size", nut_sizes, key="nut_size")
        note1_nut = st.text_area("Note (opzionale)", height=80, key="nut_note1")

        mtype_nut = st.selectbox("Material Type", [""] + material_types, key="mtype_nut")
        pref_df_nut = materials_df[
            (materials_df["Material Type"] == mtype_nut) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_nut = sorted(pref_df_nut["Prefix"].unique()) if mtype_nut != "MISCELLANEOUS" else []
        mprefix_nut = st.selectbox("Material Prefix", [""] + prefixes_nut, key="nut_mprefix")

        if mtype_nut == "MISCELLANEOUS":
            names_nut = materials_df[materials_df["Material Type"] == mtype_nut]["Name"].dropna().tolist()
        else:
            names_nut = materials_df[
                (materials_df["Material Type"] == mtype_nut) &
                (materials_df["Prefix"] == mprefix_nut)
            ]["Name"].dropna().tolist()
        mname_nut = st.selectbox("Material Name", [""] + names_nut, key="nut_mname")

        note2_nut = st.text_area("Material Note (opzionale)", height=80, key="nut_note2")

        if st.button("Genera Output", key="gen_nut"):
            if mtype_nut != "MISCELLANEOUS":
                materiale_nut = f"{mtype_nut} {mprefix_nut} {mname_nut}".strip()
                match_nut = materials_df[
                    (materials_df["Material Type"] == mtype_nut) &
                    (materials_df["Prefix"] == mprefix_nut) &
                    (materials_df["Name"] == mname_nut)
                ]
            else:
                materiale_nut = mname_nut
                match_nut = materials_df[
                    (materials_df["Material Type"] == mtype_nut) &
                    (materials_df["Name"] == mname_nut)
                ]
            codice_fpd_nut = match_nut["FPD Code"].values[0] if not match_nut.empty else ""

            descr_nut = f"NUT, HEX - TYPE: {nut_type}, SIZE: {size_nut}"
            if note1_nut:
                descr_nut += f", {note1_nut}"
            descr_nut += f", {materiale_nut}"
            if note2_nut:
                descr_nut += f", {note2_nut}"

            st.session_state["output_data"] = {
                "Item": "56030…",
                "Description": descr_nut,
                "Identificativo": "6581-HEXAGON NUT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Material": materiale_nut,
                "FPD material code": codice_fpd_nut,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"nut_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"nut_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_nut = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="nut_dl_mode")
        item_code_nut = st.text_input("Codice item", key="nut_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_nut"):
            if not item_code_nut:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_nut(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_nut = [
                    "\\%FN", item_code_nut,
                    "\\%TC", get_val_nut("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_nut("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_nut("Identificativo"), "TAB",
                    get_val_nut("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_nut('ERP_L1')}.{get_val_nut('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_nut("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_nut("Catalog"), "TAB", "TAB", "TAB",
                    get_val_nut("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_nut("FPD material code"), "TAB",
                    get_val_nut("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_nut("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_nut("Quality") if get_val_nut("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_nut("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_nut("To supplier") if get_val_nut("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_nut = "\t".join(dataload_fields_nut)
                st.text_area("Anteprima (per copia manuale)", dataload_string_nut, height=200)

                csv_buffer_nut = io.StringIO()
                writer_nut     = csv.writer(csv_buffer_nut, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_nut:
                    writer_nut.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_nut.getvalue(),
                    file_name=f"dataload_{item_code_nut}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- RING, WEAR
elif selected_part == "Ring, Wear":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        ring_type    = st.selectbox(
            "Type",
            ["Stationary", "Rotary"],
            key="ring_type"
        )
        model_ring   = st.selectbox(
            "Product/Pump Model",
            [""] + sorted(size_df["Pump Model"].dropna().unique()),
            key="ring_model"
        )
        size_list    = size_df[size_df["Pump Model"] == model_ring]["Size"].dropna().tolist()
        size_ring    = st.selectbox(
            "Product/Pump Size",
            [""] + size_list,
            key="ring_size"
        )

        int_dia_ring = st.number_input(
            "Internal Diameter (mm)",
            min_value=0,
            step=1,
            format="%d",
            key="ring_int_dia"
        )
        ext_dia_ring = st.number_input(
            "External Diameter (mm)",
            min_value=0,
            step=1,
            format="%d",
            key="ring_ext_dia"
        )
        length_ring  = st.number_input(
            "Length (mm)",
            min_value=0,
            step=1,
            format="%d",
            key="ring_length"
        )

        note_ring    = st.text_area(
            "Note (opzionale)",
            height=80,
            key="ring_note"
        )
        clearance    = st.radio(
            "Increased clearance?",
            ["No", "Yes"],
            horizontal=True,
            key="ring_clearance"
        )
        dwg_ring     = st.text_input(
            "Dwg/doc number",
            key="ring_dwg"
        )

        mtype_ring   = st.selectbox(
            "Material Type",
            [""] + material_types,
            key="mtype_ring"
        )
        pref_df_ring = materials_df[
            (materials_df["Material Type"] == mtype_ring) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_ring = sorted(pref_df_ring["Prefix"].unique()) if mtype_ring != "MISCELLANEOUS" else []
        mprefix_ring  = st.selectbox(
            "Material Prefix",
            [""] + prefixes_ring,
            key="mprefix_ring"
        )

        if mtype_ring == "MISCELLANEOUS":
            names_ring = materials_df[
                materials_df["Material Type"] == mtype_ring
            ]["Name"].dropna().tolist()
        else:
            names_ring = materials_df[
                (materials_df["Material Type"] == mtype_ring) &
                (materials_df["Prefix"] == mprefix_ring)
            ]["Name"].dropna().tolist()
        mname_ring = st.selectbox(
            "Material Name",
            [""] + names_ring,
            key="mname_ring"
        )

        note2_ring = st.text_area(
            "Material Note (opzionale)",
            height=80,
            key="ring_note2"
        )

        if st.button("Genera Output", key="gen_ring"):
            # Costruzione Materiale e codice FPD
            if mtype_ring != "MISCELLANEOUS":
                materiale_ring = f"{mtype_ring} {mprefix_ring} {mname_ring}".strip()
                match_ring = materials_df[
                    (materials_df["Material Type"] == mtype_ring) &
                    (materials_df["Prefix"] == mprefix_ring) &
                    (materials_df["Name"] == mname_ring)
                ]
            else:
                materiale_ring = mname_ring
                match_ring = materials_df[
                    (materials_df["Material Type"] == mtype_ring) &
                    (materials_df["Name"] == mname_ring)
                ]
            codice_fpd_ring = match_ring["FPD Code"].values[0] if not match_ring.empty else ""

            # Identificativo e Item in base al tipo di ring
            if ring_type == "Rotary":
                identificativo = "2300-IMPELLER WEAR RING"
                item_code      = "40224…"
            else:
                identificativo = "1500-CASING WEAR RING"
                item_code      = "40223…"

            # Costruzione descrizione
            descr_ring = (
                f"RING, WEAR - {ring_type} {model_ring} {size_ring}, "
                f"ID: {int(int_dia_ring)}mm, OD: {int(int_dia_ring) + 2*int(ext_dia_ring)}mm, "
                f"LENGTH: {int(length_ring)}mm"
            )
            if note_ring:
                descr_ring += f", {note_ring}"
            if clearance == "Yes":
                descr_ring += ", INCREASED CLEARANCE"
            descr_ring += f", {materiale_ring}"
            if note2_ring:
                descr_ring += f", {note2_ring}"

            st.session_state["output_data"] = {
                "Item":               item_code,
                "Description":        descr_ring,
                "Identificativo":     identificativo,
                "Classe ricambi":     "1-2-3",
                "Categories":         "FASCIA ITE 4",
                "Catalog":            "ALBERO",
                "Disegno":            dwg_ring,
                "Material":           materiale_ring,
                "FPD material code":  codice_fpd_ring,
                "Template":           "FPD_BUY_1",
                "ERP_L1":             "20_TURNKEY_MACHINING",
                "ERP_L2":             "24_RINGS",
                "To supplier":        ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"ring_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"ring_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_ring = st.radio(
            "Tipo operazione:",
            ["Crea nuovo item", "Aggiorna item"],
            key="ring_dl_mode"
        )
        item_code_ring = st.text_input(
            "Codice item",
            key="ring_item_code"
        )

        if st.button("Genera stringa DataLoad", key="gen_dl_ring"):
            if not item_code_ring:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_ring(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_ring = [
                    "\\%FN", item_code_ring,
                    "\\%TC", get_val_ring("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_ring("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_ring("Identificativo"), "TAB",
                    get_val_ring("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_ring('ERP_L1')}.{get_val_ring('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_ring("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_ring("Catalog"), "TAB", "TAB", "TAB",
                    get_val_ring("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_ring("FPD material code"), "TAB",
                    get_val_ring("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_ring("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_ring("Quality") if get_val_ring("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_ring("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_ring("To supplier") if get_val_ring("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_ring = "\t".join(dataload_fields_ring)
                st.text_area("Anteprima (per copia manuale)", dataload_string_ring, height=200)

                csv_buffer_ring = io.StringIO()
                writer_ring     = csv.writer(csv_buffer_ring, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_ring:
                    writer_ring.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_ring.getvalue(),
                    file_name=f"dataload_{item_code_ring}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# (continua inserendo i restanti blocchi nello stesso formato)
