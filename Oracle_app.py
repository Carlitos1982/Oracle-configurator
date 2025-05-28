import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")

    materials_df = materials_df.drop_duplicates(
        subset=["Material Type", "Prefix", "Name"]
    ).reset_index(drop=True)

    return {
        "size_df": size_df,
        "features_df": features_df,
        "materials_df": materials_df
    }

data = load_config_data()
size_df = data["size_df"]
features_df = data["features_df"]
materials_df = data["materials_df"]

# Liste base
part_options = ["Baseplate, Pump", "Casing, Pump", "Impeller, Pump"]  # esempio
material_types = materials_df["Material Type"].dropna().unique().tolist()
pump_models = sorted(size_df["Pump Model"].dropna().unique())

# Scelta parte
selected_part = st.selectbox("Seleziona Parte", part_options)

# Colonne layout
col1, col2 = st.columns([2, 1])

# --- BASEPLATE, PUMP --- #
if selected_part == "Baseplate, Pump":
    with col1:
        st.subheader("Configurazione - Baseplate, Pump")

        model = st.selectbox("Pump Model", [""] + pump_models, key="mod_bp")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="size_bp")

        length = st.number_input("Length (mm)", min_value=0, step=1, key="len_bp")
        width = st.number_input("Width (mm)", min_value=0, step=1, key="wid_bp")
        weight = st.number_input("Weight (kg)", min_value=0, step=1, key="wgt_bp")
        sourcing = st.selectbox("Sourcing", ["Europe", "India", "China"], key="sour_bp")
        note = st.text_area("Note (opzionale)", height=80, key="note_bp")
        dwg = st.text_input("Dwg/doc number", key="dwg_bp")

        mtype = st.selectbox("Material Type", [""] + material_types, key="mtype_bp")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix_bp")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="mname_bp")

        if st.button("Genera Output", key="gen_bp"):
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
            descrizione = f"Baseplate, Pump {model} {size} Length: {length}mm Width: {width}mm Weight: {weight}kg Sourcing: {sourcing}"
            if note:
                descrizione += f", {note}"
            descrizione += f", {materiale}"

            st.session_state["output_data"] = {
                "Item": "477…",
                "Description": descrizione,
                "Identificativo": "6110-BASE PLATE",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_4",
                "ERP_L1": "21_FABRICATION_OR_BASEPLATES",
                "ERP_L2": "18_FOUNDATION_PLATE",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
                    
# --- CASING, PUMP --- #
if selected_part == "Casing, Pump":
    with col1:
        st.subheader("Configurazione - Casing, Pump")

        model = st.selectbox("Pump Model", [""] + pump_models, key="mod_casing")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="size_casing")

        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="f1_casing")

        f2_list = []
        if model in ["HPX", "HED"]:
            f2_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
        feature2 = st.selectbox("Additional Feature 2", [""] + f2_list, key="f2_casing")

        note = st.text_area("Note (opzionale)", height=80, key="note_casing")
        dwg = st.text_input("Dwg/doc number", key="dwg_casing")

        mtype = st.selectbox("Material Type", [""] + material_types, key="mtype_casing")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix_casing")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="mname_casing")

        if st.button("Genera Output", key="gen_casing"):
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
            descrizione = f"Casing, Pump {model} {size} {feature1} {feature2}".strip()
            if note:
                descrizione += f", {note}"
            descrizione += f", {materiale}"

            st.session_state["output_data"] = {
                "Item": "40202…",
                "Description": descrizione,
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
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

# --- CASING COVER, PUMP --- #
elif selected_part == "Casing Cover, Pump":
    with col1:
        st.subheader("Configurazione - Casing Cover, Pump")

        model = st.selectbox("Pump Model", [""] + pump_models, key="mod_cover")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="size_cover")

        note = st.text_area("Note (opzionale)", height=80, key="note_cover")
        dwg = st.text_input("Dwg/doc number", key="dwg_cover")

        mtype = st.selectbox("Material Type", [""] + material_types, key="mtype_cover")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix_cover")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="mname_cover")

        if st.button("Genera Output", key="gen_cover"):
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
            descrizione = f"Casing Cover, Pump {model} {size}"
            if note:
                descrizione += f", {note}"
            descrizione += f", {materiale}"

            st.session_state["output_data"] = {
                "Item": "40205…",
                "Description": descrizione,
                "Identificativo": "1221-CASING COVER",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "COPERCHIO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "13_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                
                
# --- IMPELLER, PUMP --- #
elif selected_part == "Impeller, Pump":
    with col1:
        st.subheader("Configurazione - Impeller, Pump")

        model = st.selectbox("Pump Model", [""] + pump_models, key="mod_imp")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="size_imp")

        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="f1_imp")

        note = st.text_area("Note (opzionale)", height=80, key="note_imp")
        dwg = st.text_input("Dwg/doc number", key="dwg_imp")

        mtype = st.selectbox("Material Type", [""] + material_types, key="mtype_imp")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix_imp")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="mname_imp")

        if st.button("Genera Output", key="gen_imp"):
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
            descrizione = f"Impeller, Pump {model} {size} {feature1}".strip()
            if note:
                descrizione += f", {note}"
            descrizione += f", {materiale}"

            st.session_state["output_data"] = {
                "Item": "40229…",
                "Description": descrizione,
                "Identificativo": "2200-IMPELLER",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "GIRANTE",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "20_IMPELLER_DIFFUSER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

# --- BALANCE BUSHING / DRUM / DISC --- #
elif selected_part in ["Balance Bushing, Pump", "Balance Drum, Pump", "Balance Disc, Pump"]:
    with col1:
        part_map = {
            "Balance Bushing, Pump": ("40226…", "6231-BALANCE DRUM BUSH", "ALBERO"),
            "Balance Drum, Pump":    ("40227…", "6231-BALANCE DRUM BUSH", "ARTVARI"),
            "Balance Disc, Pump":    ("40228…", "6210-BALANCE DISC",      "ARTVARI")
        }
        codice, identificativo, catalog = part_map[selected_part]

        st.subheader(f"Configurazione - {selected_part}")

        model = st.selectbox("Pump Model", [""] + pump_models, key=f"mod_bal_{selected_part}")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key=f"size_bal_{selected_part}")

        int_dia = st.number_input("Internal Diameter (mm)", min_value=0, step=1, format="%d", key=f"int_dia_{selected_part}")
        ext_dia = st.number_input("External Diameter (mm)", min_value=0, step=1, format="%d", key=f"ext_dia_{selected_part}")
        note = st.text_area("Note (opzionale)", height=80, key=f"note_bal_{selected_part}")
        dwg = st.text_input("Dwg/doc number", key=f"dwg_bal_{selected_part}")

        mtype = st.selectbox("Material Type", [""] + material_types, key=f"mtype_bal_{selected_part}")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key=f"mprefix_bal_{selected_part}")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key=f"mname_bal_{selected_part}")

        if st.button("Genera Output", key=f"gen_bal_{selected_part}"):
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

            descrizione = f"{selected_part} {model} {size} int. dia.: {int_dia}mm ext. dia.: {ext_dia}mm"
            if note:
                descrizione += f", {note}"
            descrizione += f", {materiale}"

            erp_l2 = "16_BUSHING" if "Disc" not in selected_part else "30_DISK"

            st.session_state["output_data"] = {
                "Item": codice,
                "Description": descrizione,
                "Identificativo": identificativo,
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": catalog,
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": erp_l2,
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
# --- SHAFT, PUMP --- #
elif selected_part == "Shaft, Pump":
    with col1:
        st.subheader("Configurazione - Shaft, Pump")

        model = st.selectbox("Pump Model", [""] + pump_models, key="mod_shaft")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="size_shaft")

        feature1 = st.selectbox("Additional Feature 1", [""] + features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist(), key="f1_shaft")

        feature2 = st.selectbox("Additional Feature 2", [""] + features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features2")
        ]["Feature"].dropna().tolist(), key="f2_shaft")

        brg_type = st.text_input("Brg. type", key="brg_type")
        brg_size = st.text_input("Brg. size", key="brg_size")
        max_dia  = st.number_input("Max diameter (mm)", min_value=0, step=1, key="max_dia")
        max_len  = st.number_input("Max length (mm)", min_value=0, step=1, key="max_len")

        note = st.text_area("Note (opzionale)", height=80, key="note_shaft")
        dwg = st.text_input("Dwg/doc number", key="dwg_shaft")

        mtype = st.selectbox("Material Type", [""] + material_types, key="mtype_shaft")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix_shaft")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="mname_shaft")

        if st.button("Genera Output", key="gen_shaft"):
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
            descrizione = f"Shaft, Pump {model} {size} {feature1} {feature2} Brg. type: {brg_type} Brg. size: {brg_size} Max dia: {max_dia}mm Max len: {max_len}mm"
            if note:
                descrizione += f", {note}"
            descrizione += f", {materiale}"

            st.session_state["output_data"] = {
                "Item": "40231…",
                "Description": descrizione,
                "Identificativo": "2100-SHAFT",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "25_SHAFTS",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)

# --- FLANGE, PIPE --- #
elif selected_part == "Flange, Pipe":
    with col1:
        st.subheader("Configurazione - Flange, Pipe")

        flange_type = st.selectbox("Type", ["SW", "BW"], key="flg_type")
        size_fp = st.selectbox("Size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="flg_size")
        face_type = st.selectbox("Face Type", ["RF","FF","RJ"], key="flg_face")
        flange_cls = st.selectbox("Class", ["150","300","600","1500","2500"], key="flg_cls")

        if flange_cls in ["1500", "2500"] and face_type != "RJ":
            st.warning("Attenzione: per classi 1500 o 2500 è raccomandato l'uso di faccia tipo RJ (Ring Joint). Verificare lo scopo di fornitura")

        schedule_fp = st.selectbox("Schedula", ["5","10","20","30","40","60","80","100","120","140","160"], key="flg_sched")
        flange_mat = st.selectbox("Flange Material", [
            "A105", "A106-GR B", "UNS-S31803", "UNS-S32760", "A350 LF2",
            "A182-F316L", "ALLOY 825", "GALVANIZED CARBON STEEL"
        ], key="flg_mat")
        note_fp = st.text_area("Note (opzionale)", height=80, key="flg_note")
        dwg_fp = st.text_input("Dwg/doc number", key="flg_dwg")

        if st.button("Genera Output", key="gen_flange"):
            descr_fp = (
                f"FLANGE, PIPE - TYPE: {flange_type}, SIZE: {size_fp}, "
                f"FACE TYPE: {face_type}, CLASS: {flange_cls}, SCHEDULA: {schedule_fp}, MATERIAL: {flange_mat}"
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
                "Disegno": dwg_fp,
                "Material": "NOT AVAILABLE",
                "FPD material code": "BO-NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "23_FLANGE",
                "ERP_L2": "13_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
    elif selected_part == "Gate, Valve":
    with col1:
        st.subheader("Configurazione - Gate, Valve")

        size = st.selectbox("Size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="gate_size")
        pclass = st.selectbox("Pressure class", ["150","300","600","1500","2500"], key="gate_pclass")
        inlet_type = st.selectbox("Inlet connection type", ["SW","WN"], key="gate_inlet_type")
        inlet_size = st.selectbox("Inlet connection size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="gate_inlet_size")
        outlet_type = st.selectbox("Outlet connection type", ["SW","WN"], key="gate_outlet_type")
        outlet_size = st.selectbox("Outlet connection size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="gate_outlet_size")
        valve_mat = st.selectbox("Valve material", [
            "A105","A106-GR B","UNS-S31803","UNS-S32760","A350 LF2","A182-F316L","ALLOY 825","GALVANIZED CARBON STEEL"
        ], key="gate_mat")
        schedule = st.selectbox("Schedula", ["5","10","20","30","40","60","80","100","120","140","160"], key="gate_sched")
        note_gate = st.text_area("Note (opzionale)", height=80, key="gate_note")

        if st.button("Genera Output", key="gen_gate"):
            descr_gate = (
                f"Gate, Valve; Size {size} Pressure class {pclass} "
                f"Inlet connection type {inlet_type} size {inlet_size} "
                f"Outlet connection type {outlet_type} size {outlet_size} "
                f"Body material {valve_mat} Sch {schedule}"
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
                "Material": "NOT AVAILABLE",
                "FPD material code": "BO-NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "72_VALVE",
                "ERP_L2": "18_GATE_VALVE",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
elif selected_part == "Gasket, Spiral Wound":
    with col1:
        st.subheader("Configurazione - Gasket, Spiral Wound")

        winding_colors = {
            "304 stainless steel":"Yellow RAL1021","316L stainless steel":"Green RAL6005",
            "317L stainless steel":"Maroon RAL3003","321 stainless steel":"Turquoise RAL5018",
            "347 stainless steel":"Blue RAL5017","MONEL":"Orange RAL2003","Nickel":"Red RAL3024",
            "Titanium":"Purple RAL4003","Alloy20":"Black RAL9005","INCONEL 600":"Gold RAL1004",
            "HASTELLOY B":"Brown RAL8003","HASTELLOY C":"Beige RAL1001","INCOLOY800":"White RAL9010",
            "DUPLEX":"Yellow+Blue RAL1021+5017","SUPERDUPLEX":"Red+Black RAL3024+9005",
            "ALLOY 825":"Orange+Green RAL2003+6005","UNS S31254":"Orange+Blue RAL2003+5017",
            "ZYRCONIUM 702":"Gold+Green RAL1004+6005","INCONEL X750HT":"Gold+Black RAL1004+9005"
        }
        filler_colors = {
            "Graphite":"Gray RAL7011","PTFE":"White RAL9010",
            "Ceramic":"Ceramic Lt. Green RAL6021","Verdicarb (Mica Graphite)":"Pink RAL3015"
        }
        rating_stripes = {
            "STANDARD PRESSURE m=3 y=10000 psi":"(1 stripe)",
            "HIGH PRESSURE m=3 y=17500 psi":"(2 stripes)",
            "ULTRA HIGH PRESSURE m=3 y=23500 psi":"(3 stripes)"
        }

        winding = st.selectbox("Winding material", list(winding_colors.keys()), key="gask_wind")
        filler = st.selectbox("Filler", list(filler_colors.keys()), key="gask_fill")
        inner_dia = st.number_input("Inner Diameter (mm)", min_value=0.0, step=0.1, key="gask_id")
        outer_dia = st.number_input("Outer Diameter (mm)", min_value=0.0, step=0.1, key="gask_od")
        thickness = st.number_input("Thickness (mm)", min_value=0.0, step=0.1, key="gask_thk")
        rating = st.selectbox("Rating", list(rating_stripes.keys()), key="gask_rating")
        dwg = st.text_input("Dwg/doc number", key="gask_dwg")
        note = st.text_area("Note (opzionale)", height=80, key="gask_note")

        if st.button("Genera Output", key="gen_gask"):
            color1 = winding_colors[winding]
            color2 = filler_colors[filler]
            stripe = rating_stripes[rating]

            descr = (
                f"GASKET, SPIRAL WOUND - WINDING: {winding}, FILLER: {filler}, "
                f"ID: {inner_dia}mm, OD: {outer_dia}mm, THK: {thickness}mm, "
                f"RATING: {rating}, COLOR CODE 1: {color1}, COLOR CODE 2: {color2}, {stripe}"
            )
            if note:
                descr += f", NOTE: {note}"

            st.session_state["output_data"] = {
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
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
elif selected_part == "Gasket, Flat":
    with col1:
        st.subheader("Configurazione - Gasket, Flat")

        thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f", key="flat_thk")
        uom = st.selectbox("UOM", ["mm", "inches"], key="flat_uom")
        dwg = st.text_input("Dwg/doc number", key="flat_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="flat_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="flat_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="flat_mname")

        if st.button("Genera Output", key="gen_flat"):
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
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    

elif selected_part == "Nut, Hex":
    with col1:
        st.subheader("Configurazione - Nut, Hex")

        nut_type = "Heavy"
        nut_size = st.selectbox("Size", ['M6', 'M8', 'M10', 'M12', 'M14', 'M16', 'M18', 'M20', 'M24'], key="nut_size")
        note1 = st.text_area("Note (opzionale)", height=60, key="nut_note")

        mtype = st.selectbox("Material Type", [""] + material_types, key="nut_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="nut_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="nut_mname")
        mat_note = st.text_area("Material note (opzionale)", height=40, key="nut_mat_note")

        if st.button("Genera Output", key="gen_nut"):
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
            descr = f"NUT, HEX, TYPE: {nut_type}, SIZE: {nut_size}"
            if note1:
                descr += f", {note1}"
            descr += f", {materiale}"
            if mat_note:
                descr += f", {mat_note}"

            st.session_state["output_data"] = {
                "Item": "56030…",
                "Description": descr,
                "Identificativo": "6581-HEXAGON NUT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
elif selected_part == "Stud, Threaded":
    with col1:
        st.subheader("Configurazione - Stud, Threaded")

        thread_type = st.selectbox("Threaded", ["Full", "Partial"], key="stud_thread")
        stud_size = st.selectbox("Size", ['M6', 'M8', 'M10', 'M12', 'M14', 'M16', 'M18', 'M20', 'M24'], key="stud_size")
        stud_length = st.selectbox("Length", ['30', '40', '50', '60', '70', '80', '100', '120'], key="stud_length")
        note_stud = st.text_area("Note (opzionale)", height=60, key="stud_note")
        dwg_stud = st.text_input("Dwg/doc number", key="stud_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="stud_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="stud_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="stud_mname")
        mat_note = st.text_area("Material note (opzionale)", height=40, key="stud_mat_note")

        if st.button("Genera Output", key="gen_stud"):
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

            descr = f"STUD, {thread_type} THREADED, SIZE: {stud_size}, LENGTH: {stud_length}mm"
            if note_stud:
                descr += f", {note_stud}"
            descr += f", {materiale}"
            if mat_note:
                descr += f", {mat_note}"

            st.session_state["output_data"] = {
                "Item": "56146…",
                "Description": descr,
                "Identificativo": "6572-STUD",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_stud,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "12_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
elif selected_part == "Ring, Wear":
    with col1:
        st.subheader("Configurazione - Ring, Wear")

        ring_type = st.selectbox("Type", ["Stationary", "Rotary"], key="ring_type")
        model = st.selectbox("Pump Model", [""] + pump_models, key="ring_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="ring_size")

        int_dia = st.number_input("Internal Diameter (mm)", min_value=0.0, step=0.1, key="ring_id")
        ext_dia = st.number_input("External Diameter (mm)", min_value=0.0, step=0.1, key="ring_od")
        clearance = st.radio("Increased clearance", ["No", "Yes"], key="ring_clr")
        note = st.text_area("Note (opzionale)", height=80, key="ring_note")
        dwg = st.text_input("Dwg/doc number", key="ring_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="ring_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="ring_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="ring_mname")
        mat_note = st.text_area("Material note (opzionale)", height=40, key="ring_mat_note")

        if st.button("Genera Output", key="gen_ring"):
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

            descr = (
                f"{ring_type.upper()} WEAR RING for {model} {size}, ID: {int_dia}mm, OD: {ext_dia}mm"
            )
            if clearance == "Yes":
                descr += ", Increased clearance"
            if note:
                descr += f", {note}"
            descr += f", {materiale}"
            if mat_note:
                descr += f", {mat_note}"

            if ring_type == "Stationary":
                codice_item = "40223…"
                identificativo = "1500-CASING WEAR RING"
            else:
                codice_item = "40224…"
                identificativo = "2300-IMPELLER WEAR RING"

            st.session_state["output_data"] = {
                "Item": codice_item,
                "Description": descr,
                "Identificativo": identificativo,
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "24_RINGS",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        if "output_data" in st.session_state:
            st.subheader("Output")
            st.markdown("_Clicca nei campi e usa Ctrl+C per copiare_")
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100)
                else:
                    st.text_input(campo, value=valore)
                    
                    