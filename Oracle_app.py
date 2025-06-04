import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

# --- Configurazione pagina wide
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- Header
flowserve_logo = Image.open("assets/IMG_1456.png")
col_header, col_spacer, col_logo = st.columns([3, 4, 1], gap="small")
with col_header:
    st.markdown(
        '<h1 style="white-space: nowrap; margin: 0; font-size: 2rem;">'
        'Oracle Item Setup - Web App'
        '</h1>',
        unsafe_allow_html=True
    )
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
    materials_df = materials_df.drop_duplicates(
        subset=["Material Type", "Prefix", "Name"]
    ).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- Definizione di dimensioni comuni per bulloni
bolt_sizes = [
    "#10-24UNC", "5/16\"-18UNC", "3/8\"-16UNC", "1/2\"-13UNC", "3/4\"-16UNF",
    "7/8\"-9UNC", "7/8\"-14UNF", "1\"-12UNF", "1-1/8\"-12UNF", "1-1/2\"-12UNC",
    "2\"-4.5UNC", "2-1/2\"-4UNC", "3\"-6UNC", "4\"-8UNC",
    "M6x1", "M8x1.25", "M10x1.5", "M12x1.75", "M16x2", "M20x2.5", "M24x3",
    "M30x3.5", "M36x4", "M42x4.5", "M48x5", "M56x5.5", "M64x6", "M72x6",
    "M80x6", "M90x6", "M100x6"
]

bolt_lengths = [
    "1/8\"in", "1/4\"in", "3/8\"in", "5/16\"in", "1/2\"in", "3/4\"in",
    "1\"in", "1-1/8\"in", "1-1/4\"in", "1-3/8\"in", "1-1/2\"in", "2\"in",
    "2-1/8\"in", "2-1/4\"in", "2-3/8\"in", "2-1/2\"in", "2-3/4\"in",
    "3\"in", "3-1/8\"in", "3-1/4\"in", "3-3/8\"in", "3-1/2\"in", "4\"in",
    "4-1/8\"in", "4-1/4\"in", "4-3/8\"in", "4-1/2\"in",
    "50mm", "55mm", "60mm", "65mm", "70mm", "75mm", "80mm", "85mm", "90mm", "95mm",
    "100mm", "105mm", "110mm", "115mm", "120mm", "125mm", "130mm", "135mm", "140mm",
    "145mm", "150mm", "155mm", "160mm", "165mm", "170mm", "175mm", "180mm", "185mm",
    "190mm", "195mm"
]


# --- Liste materiali Gasket Spiral Wound
winding_materials = [
    "SS316L", "SS304", "MONEL", "INCONEL", "DUPLEX", "HASTELLOY C276"
]

filler_materials = [
    "GRAPHITE", "PTFE", "MICA", "CERAMIC", "GLASS", "SS304"
]

color_codes = {
    "SS316L": "Green",
    "SS304": "Red",
    "MONEL": "Blue",
    "INCONEL": "Yellow",
    "DUPLEX": "Purple",
    "HASTELLOY C276": "Orange",
    "GRAPHITE": "Black",
    "PTFE": "White",
    "MICA": "Gray",
    "CERAMIC": "Light Gray",
    "GLASS": "Clear"
}
# --- Definizione delle categorie
categories = {
    "Machined Parts": [
        "Baseplate, Pump",
        "Casing, Pump",
        "Casing Cover, Pump",
        "Impeller, Pump",
        "Balance Bushing, Pump",
        "Balance Drum, Pump",
        "Balance Disc, Pump",
        "Shaft, Pump",
        "Ring, Wear"
    ],
    "Piping": [
        "Flange, Pipe",
        "Gate, Valve",
        "Gasket, Flat",
        "Gasket, Ring Type Joint"
    ],
    "Fasteners": [
        "Bolt, Eye",
        "Bolt, Hexagonal",
        "Nut, Hex",
        "Stud, Threaded",
        "Screw, Cap",
        "Screw, Grub",
        "Pin, Dowel"
    ],
    "Commercial Parts": [
        "Bearing, Hydrostatic/Hydrodynamic",
        "Bearing, Rolling",
        "Gusset, Other",
        "Gasket, Spiral Wound"
    ]
}

# --- Selezione categoria e parte affiancate
col1, col2 = st.columns([1, 1], gap="small")
with col1:
    selected_category = st.selectbox(
        "Categoria:",
        [""] + list(categories.keys()),
        index=0
    )
with col2:
    if selected_category:
        part_list = categories[selected_category]
    else:
        part_list = []
    selected_part = st.selectbox(
        "Parte:",
        [""] + part_list,
        key="selected_part"
    )
# ——— Gestione “output_data” per ogni cambio di selected_part ———
if "prev_part" not in st.session_state:
    st.session_state.prev_part = ""

if selected_part != st.session_state.prev_part:
    st.session_state.pop("output_data", None)
    st.session_state.prev_part = selected_part
# —————————————————————————————————————————————————————————

st.markdown("---")



# --- CASING, PUMP
if selected_part == "Casing, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="cas_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="cas_size")

        feature_1 = ""
        special = ["HDO", "DMX", "WXB", "WIK"]
        if model not in special:
            f1_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="cas_f1")

        feature_2 = ""
        if model in ["HPX", "HED"]:
            f2_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key="cas_f2")

        note = st.text_area("Note (opzionale)", height=80, key="cas_note")
        dwg = st.text_input("Dwg/doc number", key="cas_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="cas_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="cas_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="cas_mname")

        # ✅ Checkbox per SQ113 e SQ137
        hf_service = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="cas_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="cas_tmt")

        if st.button("Genera Output", key="cas_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            # Costruzione tag e quality
            sq_tags = []
            quality_lines = []
            if hf_service:
                sq_tags.append("[SQ113]")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")

            tag_string = " ".join(sq_tags)
            quality = "\n".join(quality_lines)

            descr = f"CASING, PUMP - MODEL: {model}, SIZE: {size}, FEATURES: {feature_1}, {feature_2}"
            if note:
                descr += f", NOTE: {note}"
            if tag_string:
                descr += f" {tag_string}"
            descr = "*" + descr

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
                "Quality": quality
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=80)
                else:
                    st.text_input(k, value=v)


    # COLONNA 3: DataLoad
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
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")


# --- CASING COVER, PUMP
if selected_part == "Casing Cover, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="cc_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="cc_size")

        feature_1 = ""
        special = ["HDO", "DMX", "WXB", "WIK"]
        if model not in special:
            f1_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="cc_f1")

        feature_2 = ""
        if model in ["HPX", "HED"]:
            f2_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key="cc_f2")

        note = st.text_area("Note (opzionale)", height=80, key="cc_note")
        dwg = st.text_input("Dwg/doc number", key="cc_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="cc_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="cc_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="cc_mname")

        # ✅ Checkbox SQ113 e SQ137
        hf_service = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="cc_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="cc_tmt")

        if st.button("Genera Output", key="cc_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            # SQ tag + quality
            sq_tags = []
            quality_lines = []
            if hf_service:
                sq_tags.append("[SQ113]")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")

            tag_string = " ".join(sq_tags)
            quality = "\n".join(quality_lines)

            descr = f"CASING COVER, PUMP - MODEL: {model}, SIZE: {size}, FEATURES: {feature_1}, {feature_2}"
            if note:
                descr += f", NOTE: {note}"
            if tag_string:
                descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "40203…",
                "Description": descr,
                "Identificativo": "1200-COVER",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "COPERCHIO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "18_COVER",
                "To supplier": "",
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=80)
                else:
                    st.text_input(k, value=v)

    # COLONNA 3: DataLoad
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
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code_cc}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- IMPELLER, PUMP
# --- IMPELLER, PUMP
if selected_part == "Impeller, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model_imp = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="imp_model")
        size_list_imp = size_df[size_df["Pump Model"] == model_imp]["Size"].dropna().tolist()
        size_imp = st.selectbox("Product/Pump Size", [""] + size_list_imp, key="imp_size")

        feature_1_imp = ""
        special_imp = ["HDO", "DMX", "WXB", "WIK"]
        if model_imp not in special_imp:
            f1_list_imp = features_df[
                (features_df["Pump Model"] == model_imp) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_imp = st.selectbox("Additional Feature 1", [""] + f1_list_imp, key="imp_f1")

        feature_2_imp = ""
        if model_imp in ["HPX", "HED"]:
            f2_list_imp = features_df[
                (features_df["Pump Model"] == model_imp) &
                (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2_imp = st.selectbox("Additional Feature 2", [""] + f2_list_imp, key="imp_f2")

        note_imp = st.text_area("Note (opzionale)", height=80, key="imp_note")
        dwg_imp = st.text_input("Dwg/doc number", key="imp_dwg")

        mtype_imp = st.selectbox("Material Type", [""] + material_types, key="imp_mtype")
        pref_df_imp = materials_df[(materials_df["Material Type"] == mtype_imp) & (materials_df["Prefix"].notna())]
        prefixes_imp = sorted(pref_df_imp["Prefix"].unique()) if mtype_imp != "MISCELLANEOUS" else []
        mprefix_imp = st.selectbox("Material Prefix", [""] + prefixes_imp, key="imp_mprefix")

        if mtype_imp == "MISCELLANEOUS":
            names_imp = materials_df[materials_df["Material Type"] == mtype_imp]["Name"].dropna().tolist()
        else:
            names_imp = materials_df[
                (materials_df["Material Type"] == mtype_imp) &
                (materials_df["Prefix"] == mprefix_imp)
            ]["Name"].dropna().tolist()

        mname_imp = st.selectbox("Material Name", [""] + names_imp, key="imp_mname")

        # ✅ Checkbox HF in fondo
        hf_service_imp = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="imp_hf")

        if st.button("Genera Output", key="imp_gen"):
            materiale_imp = f"{mtype_imp} {mprefix_imp} {mname_imp}".strip() if mtype_imp != "MISCELLANEOUS" else mname_imp
            match_imp = materials_df[
                (materials_df["Material Type"] == mtype_imp) &
                (materials_df["Prefix"] == mprefix_imp) &
                (materials_df["Name"] == mname_imp)
            ]
            codice_fpd_imp = match_imp["FPD Code"].values[0] if not match_imp.empty else ""

            descr_imp = f"IMPELLER, PUMP - MODEL: {model_imp}, SIZE: {size_imp}, FEATURES: {feature_1_imp}, {feature_2_imp}"
            if note_imp:
                descr_imp += f", NOTE: {note_imp}"
            if hf_service_imp:
                descr_imp += " [SQ113]"
            descr_imp = "*" + descr_imp

            quality_imp = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_imp else ""

            st.session_state["output_data"] = {
                "Item": "40203…",
                "Description": descr_imp,
                "Identificativo": "1200-IMPELLER",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": " GIRANTE",
                "Disegno": dwg_imp,
                "Material": materiale_imp,
                "FPD material code": codice_fpd_imp,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "19_IMPELLER",
                "To supplier": "",
                "Quality": quality_imp
            }


    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"imp_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"imp_{campo}")

    # COLONNA 3: DataLoad
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
                    "\\%FN", item_code_imp,
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
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code_imp}.csv",
                    mime="text/csv"
                )
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
                (features_df["Pump Model"] == model_bb) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_bb = st.selectbox("Additional Feature 1", [""] + f1_list_bb, key="f1_bb")

        feature_2_bb = ""
        if model_bb in ["HPX", "HED"]:
            f2_list_bb = features_df[
                (features_df["Pump Model"] == model_bb) &
                (features_df["Feature Type"] == "features2")
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

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_bb = (
                f"BALANCE BUSHING, PUMP - MODEL: {model_bb}, SIZE: {size_bb}, "
                f"ID: {int(int_dia_bb)}mm, OD: {int(int_dia_bb) + 2*int(ext_dia_bb)}mm, "
                f"FEATURES: {feature_1_bb}, {feature_2_bb}"
            )
            if note_bb:
                descr_bb += f", NOTE: {note_bb}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_bb = "*" + descr_bb

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

    # COLONNA 3: DataLoad
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
                (features_df["Pump Model"] == model_bd) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_bd = st.selectbox("Additional Feature 1", [""] + f1_list_bd, key="f1_bd")

        feature_2_bd = ""
        if model_bd in ["HPX", "HED"]:
            f2_list_bd = features_df[
                (features_df["Pump Model"] == model_bd) &
                (features_df["Feature Type"] == "features2")
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

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_bd = (
                f"BALANCE DRUM, PUMP - MODEL: {model_bd}, SIZE: {size_bd}, "
                f"ID: {int(int_dia_bd)}mm, OD: {int(int_dia_bd) + 2*int(ext_dia_bd)}mm, "
                f"FEATURES: {feature_1_bd}, {feature_2_bd}"
            )
            if note_bd:
                descr_bd += f", NOTE: {note_bd}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_bd = "*" + descr_bd

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

    # COLONNA 3: DataLoad
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
                (features_df["Pump Model"] == model_bdsc) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1_bdsc = st.selectbox("Additional Feature 1", [""] + f1_list_bdsc, key="f1_bdsc")

        feature_2_bdsc = ""
        if model_bdsc in ["HPX", "HED"]:
            f2_list_bdsc = features_df[
                (features_df["Pump Model"] == model_bdsc) &
                (features_df["Feature Type"] == "features2")
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

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_bdsc = (
                f"BALANCE DISC, PUMP - MODEL: {model_bdsc}, SIZE: {size_bdsc}, "
                f"ID: {int(int_dia_bdsc)}mm, OD: {int(int_dia_bdsc) + 2*int(ext_dia_bdsc)}mm, "
                f"FEATURES: {feature_1_bdsc}, {feature_2_bdsc}"
            )
            if note_bdsc:
                descr_bdsc += f", NOTE: {note_bdsc}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_bdsc = "*" + descr_bdsc

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

    # COLONNA 3: DataLoad
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
# --- GATE, VALVE
if selected_part == "Gate, Valve":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        size_gv = st.text_input("Size", key="gv_size")
        class_gv = st.text_input("Class", key="gv_class")
        type_gv = st.selectbox("Type", ["Gate", "Globe", "Check", "Ball"], key="gv_type")
        note_gv = st.text_area("Note (opzionale)", height=80, key="gv_note")
        dwg_gv = st.text_input("Dwg/doc number", key="gv_dwg")

        mtype_gv = st.selectbox("Material Type", [""] + material_types, key="gv_mtype")
        pref_df_gv = materials_df[(materials_df["Material Type"] == mtype_gv) & (materials_df["Prefix"].notna())]
        prefixes_gv = sorted(pref_df_gv["Prefix"].unique()) if mtype_gv != "MISCELLANEOUS" else []
        mprefix_gv = st.selectbox("Material Prefix", [""] + prefixes_gv, key="gv_mprefix")

        if mtype_gv == "MISCELLANEOUS":
            names_gv = materials_df[materials_df["Material Type"] == mtype_gv]["Name"].dropna().tolist()
        else:
            names_gv = materials_df[
                (materials_df["Material Type"] == mtype_gv) &
                (materials_df["Prefix"] == mprefix_gv)
            ]["Name"].dropna().tolist()

        mname_gv = st.selectbox("Material Name", [""] + names_gv, key="gv_mname")

        # ✅ Checkbox HF
        hf_service_gv = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="gv_hf")

        if st.button("Genera Output", key="gv_gen"):
            materiale_gv = f"{mtype_gv} {mprefix_gv} {mname_gv}".strip() if mtype_gv != "MISCELLANEOUS" else mname_gv
            match_gv = materials_df[
                (materials_df["Material Type"] == mtype_gv) &
                (materials_df["Prefix"] == mprefix_gv) &
                (materials_df["Name"] == mname_gv)
            ]
            codice_fpd_gv = match_gv["FPD Code"].values[0] if not match_gv.empty else ""

            descr_gv = f"{type_gv.upper()} VALVE - SIZE: {size_gv}, CLASS: {class_gv}"
            if note_gv:
                descr_gv += f", NOTE: {note_gv}"
            if hf_service_gv:
                descr_gv += " [SQ113]"
            descr_gv = "*" + descr_gv

            quality_gv = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_gv else ""

            st.session_state["output_data"] = {
                "Item": "50110…",
                "Description": descr_gv,
                "Identificativo": "4500-VALVE",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_gv,
                "Material": materiale_gv,
                "FPD material code": codice_fpd_gv,
                "Template": "FPD_BUY_2",
                "ERP_L1": "50_VALVE",
                "ERP_L2": "13_OTHER",
                "To supplier": "",
                "Quality": quality_gv
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

    # COLONNA 3: DataLoad
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
if selected_part == "Gasket, Spiral Wound":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        winding_gsw = st.selectbox("Winding Material", sorted(winding_materials), key="gsw_winding")
        filler_gsw = st.selectbox("Filler", sorted(filler_materials), key="gsw_filler")
        out_dia_gsw = st.text_input("Outer Diameter", key="gsw_out_dia")
        in_dia_gsw = st.text_input("Inner Diameter", key="gsw_in_dia")
        thickness_gsw = st.text_input("Thickness", key="gsw_thick")
        rating_gsw = st.text_input("Rating", key="gsw_rating")
        dwg_gsw = st.text_input("Dwg/doc number", key="gsw_dwg")
        note_gsw = st.text_area("Note (opzionale)", height=80, key="gsw_note")

        # ✅ Checkbox HF
        hf_service_gsw = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="gsw_hf")

        if st.button("Genera Output", key="gsw_gen"):
            color_code_1 = color_codes.get(winding_gsw, "")
            color_code_2 = color_codes.get(filler_gsw, "")

            descr_gsw = (
                f"GASKET, SPIRAL WOUND - WINDING: {winding_gsw}, FILLER: {filler_gsw}, "
                f"OD: {out_dia_gsw}, ID: {in_dia_gsw}, THK: {thickness_gsw}, RATING: {rating_gsw}, "
                f"COLOR CODE 1: {color_code_1}, COLOR CODE 2: {color_code_2}"
            )
            if note_gsw:
                descr_gsw += f", NOTE: {note_gsw}"
            if hf_service_gsw:
                descr_gsw += " [SQ113]"
            descr_gsw = "*" + descr_gsw

            quality_gsw = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_gsw else ""

            st.session_state["output_data"] = {
                "Item": "50415…",
                "Description": descr_gsw,
                "Identificativo": "4510-JOINT",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_gsw,
                "Material": "NA",
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_1",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "16_SPIRAL_WOUND",
                "To supplier": "",
                "Quality": quality_gsw
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

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_b = (
                f"BEARING, HYDROSTATIC/HYDRODYNAMIC - InsDia: {ins_dia}mm, OutDia: {out_dia}mm, "
                f"Width: {width}mm"
            )
            if add_feat:
                descr_b += f", {add_feat}"
            descr_b += f", Material: {materiale_b}"
            if mat_feat_bearing:
                descr_b += f", {mat_feat_bearing}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_b = "*" + descr_b

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
            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_rolling = (
                f"BEARING, ROLLING - TYPE: {bearing_type}, DESIGNATION: {designation}, "
                f"InsDia: {ins_dia_r}mm, OutDia: {out_dia_r}mm, Width: {width_r}mm"
            )
            if add_feat_r:
                descr_rolling += f", {add_feat_r}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_rolling = "*" + descr_rolling

            st.session_state["output_data"] = {
                "Item": "50122…",
                "Description": descr_rolling,
                "Identificativo": "3010-ANTI-FRICTION BEARING",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ALBERO",
                "Disegno": dwg_rolling,
                "Material": "BUY OUT NOT AVAILABLE",
                "FPD material code": "BO-NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "31_COMMERCIAL_BEARING",
                "ERP_L2": "11_BALL_BEARING",
                "To supplier": "",
                "Quality": ""
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

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_be = f"BOLT, EYE - THREAD: {thread_be}, LENGTH: {length_be}"
            if note1_be:
                descr_be += f", {note1_be}"
            descr_be += f", {materiale_be}"
            if note2_be:
                descr_be += f", {note2_be}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_be = "*" + descr_be

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

            # 1) Costruisci prima la descrizione base (senza asterisco)
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

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_hex = "*" + descr_hex

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

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_rtj = f"GASKET, RING TYPE JOINT - TYPE: {rtj_type}, SIZE: {rtj_size}"
            if note1_rtj:
                descr_rtj += f", {note1_rtj}"
            descr_rtj += f", {materiale_rtj}"
            if note2_rtj:
                descr_rtj += f", {note2_rtj}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_rtj = "*" + descr_rtj

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
        width_gusset     = st.number_input("Width", min_value=0, step=1, format="%d", key="gusset_width")
        thickness_gusset = st.number_input("Thickness", min_value=0, step=1, format="%d", key="gusset_thickness")
        uom_gusset       = st.selectbox("Unità di misura", ["mm", "inches"], key="gusset_uom")
        note1_gusset     = st.text_area("Note (opzionale)", height=80, key="gusset_note1")

        mtype_gusset = st.selectbox("Material Type", [""] + material_types, key="mtype_gusset")
        pref_df_gusset = materials_df[
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
        mname_gusset = st.selectbox("Material Name", [""] + names_gusset, key="mname_gusset")

        note2_gusset = st.text_area("Material Note (opzionale)", height=80, key="gusset_note2")

        if st.button("Genera Output", key="gen_gusset"):
            if mtype_gusset != "MISCELLANEOUS":
                materiale_gusset = f"{mtype_gusset} {mprefix_gusset} {mname_gusset}".strip()
                match_gusset = materials_df[
                    (materials_df["Material Type"] == mtype_gusset) &
                    (materials_df["Prefix"] == mprefix_gusset) &
                    (materials_df["Name"] == mname_gusset)
                ]
            else:
                materiale_gusset = mname_gusset
                match_gusset = materials_df[
                    (materials_df["Material Type"] == mtype_gusset) &
                    (materials_df["Name"] == mname_gusset)
                ]
            codice_fpd_gusset = match_gusset["FPD Code"].values[0] if not match_gusset.empty else ""

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_gusset = (
                f"GUSSET, OTHER - WIDTH: {int(width_gusset)}{uom_gusset}, "
                f"THK: {int(thickness_gusset)}{uom_gusset}"
            )
            if note1_gusset:
                descr_gusset += f", {note1_gusset}"
            descr_gusset += f", {materiale_gusset}"
            if note2_gusset:
                descr_gusset += f", {note2_gusset}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_gusset = "*" + descr_gusset

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
# --- STUD, THREADED
if selected_part == "Stud, Threaded":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        threaded_stu = st.selectbox("Threaded", ["Full", "Partial"], key="stu_threaded")
        size_stu = st.selectbox("Size", ["1/4''", "3/8''", "1/2''", "5/8''", "3/4''", "7/8''", "1''", "1 1/8''", "1 1/4''", "1 3/8''", "1 1/2''"], key="stu_size")
        length_stu = st.text_input("Length", key="stu_length")
        note_stu = st.text_area("Note (opzionale)", height=80, key="stu_note")
        dwg_stu = st.text_input("Dwg/doc number", key="stu_dwg")

        mtype_stu = st.selectbox("Material Type", [""] + material_types, key="stu_mtype")
        pref_df_stu = materials_df[(materials_df["Material Type"] == mtype_stu) & (materials_df["Prefix"].notna())]
        prefixes_stu = sorted(pref_df_stu["Prefix"].unique()) if mtype_stu != "MISCELLANEOUS" else []
        mprefix_stu = st.selectbox("Material Prefix", [""] + prefixes_stu, key="stu_mprefix")

        if mtype_stu == "MISCELLANEOUS":
            names_stu = materials_df[materials_df["Material Type"] == mtype_stu]["Name"].dropna().tolist()
        else:
            names_stu = materials_df[
                (materials_df["Material Type"] == mtype_stu) &
                (materials_df["Prefix"] == mprefix_stu)
            ]["Name"].dropna().tolist()

        mname_stu = st.selectbox("Material Name", [""] + names_stu, key="stu_mname")
        material_note_stu = st.text_input("Material Note (opzionale)", key="stu_mnote")

        # ✅ Checkbox HF
        hf_service_stu = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="stu_hf")

        if st.button("Genera Output", key="stu_gen"):
            materiale_stu = f"{mtype_stu} {mprefix_stu} {mname_stu}".strip() if mtype_stu != "MISCELLANEOUS" else mname_stu
            match_stu = materials_df[
                (materials_df["Material Type"] == mtype_stu) &
                (materials_df["Prefix"] == mprefix_stu) &
                (materials_df["Name"] == mname_stu)
            ]
            codice_fpd_stu = match_stu["FPD Code"].values[0] if not match_stu.empty else ""

            descr_stu = f"STUD THREADED - {threaded_stu.upper()}, SIZE: {size_stu}, LENGTH: {length_stu}"
            if note_stu:
                descr_stu += f", NOTE: {note_stu}"
            if materiale_stu:
                descr_stu += f", MATERIAL: {materiale_stu}"
            if material_note_stu:
                descr_stu += f", MATERIAL NOTE: {material_note_stu}"
            if hf_service_stu:
                descr_stu += " [SQ113]"
            descr_stu = "*" + descr_stu

            quality_stu = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_stu else ""

            st.session_state["output_data"] = {
                "Item": "56146…",
                "Description": descr_stu,
                "Identificativo": "6572-STUD",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_stu,
                "Material": materiale_stu,
                "FPD material code": codice_fpd_stu,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "12_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": quality_stu
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
# --- NUT, HEX
if selected_part == "Nut, Hex":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        nut_type = "Heavy"  # Fisso per ora
        nut_size = st.selectbox("Size", ["1/4''", "3/8''", "1/2''", "5/8''", "3/4''", "7/8''", "1''", "1 1/8''", "1 1/4''", "1 3/8''", "1 1/2''"], key="nut_size")
        note_nut = st.text_area("Note (opzionale)", height=80, key="nut_note")

        mtype_nut = st.selectbox("Material Type", [""] + material_types, key="nut_mtype")
        pref_df_nut = materials_df[(materials_df["Material Type"] == mtype_nut) & (materials_df["Prefix"].notna())]
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
        material_note_nut = st.text_input("Material Note (opzionale)", key="nut_mnote")

        # ✅ Checkbox HF
        hf_service_nut = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="nut_hf")

        if st.button("Genera Output", key="nut_gen"):
            materiale_nut = f"{mtype_nut} {mprefix_nut} {mname_nut}".strip() if mtype_nut != "MISCELLANEOUS" else mname_nut
            match_nut = materials_df[
                (materials_df["Material Type"] == mtype_nut) &
                (materials_df["Prefix"] == mprefix_nut) &
                (materials_df["Name"] == mname_nut)
            ]
            codice_fpd_nut = match_nut["FPD Code"].values[0] if not match_nut.empty else ""

            descr_nut = f"{nut_type.upper()} NUT, SIZE: {nut_size}"
            if note_nut:
                descr_nut += f", NOTE: {note_nut}"
            if materiale_nut:
                descr_nut += f", MATERIAL: {materiale_nut}"
            if material_note_nut:
                descr_nut += f", MATERIAL NOTE: {material_note_nut}"
            if hf_service_nut:
                descr_nut += " [SQ113]"
            descr_nut = "*" + descr_nut

            quality_nut = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_nut else ""

            st.session_state["output_data"] = {
                "Item": "56030…",
                "Description": descr_nut,
                "Identificativo": "6581-HEXAGON NUT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Disegno": "",
                "Material": materiale_nut,
                "FPD material code": codice_fpd_nut,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": quality_nut
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

if selected_part == "Ring, Wear":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        ring_type = st.selectbox("Type", ["Stationary", "Rotary"], key="ring_type")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="ring_model")
        in_dia = st.text_input("Internal diameter (mm)", key="ring_in_dia")
        out_dia = st.text_input("Outer diameter (mm)", key="ring_out_dia")
        note = st.text_area("Note", key="ring_note", height=80)
        increased_clearance = st.checkbox("Increased clearance", key="ring_clearance")
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

        # ✅ Checkbox SQ113 e SQ137
        hf_service = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="ring_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="ring_tmt")

        if st.button("Genera Output", key="ring_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = []
            quality_lines = []
            if hf_service:
                sq_tags.append("[SQ113]")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")

            tag_string = " ".join(sq_tags)
            quality = "\n".join(quality_lines)

            descr = f"{ring_type.upper()} WEAR RING - MODEL: {model}, IN DIA: {in_dia}, OUT DIA: {out_dia}"
            if increased_clearance:
                descr += ", INCREASED CLEARANCE"
            if note:
                descr += f", NOTE: {note}"
            if tag_string:
                descr += f" {tag_string}"
            descr = "*" + descr

            item = "40223…" if ring_type == "Stationary" else "40224…"
            identificativo = "1500-CASING WEAR RING" if ring_type == "Stationary" else "2300-IMPELLER WEAR RING"

            st.session_state["output_data"] = {
                "Item": item,
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
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=80)
                else:
                    st.text_input(k, value=v)

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
elif selected_part == "Pin, Dowel":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        diameter     = st.number_input("Diameter", min_value=0, step=1, format="%d", key="pin_diameter")
        uom_diameter = st.selectbox("UOM", ["mm", "inches"], key="pin_uom_diameter")
        length       = st.number_input("Length", min_value=0, step=1, format="%d", key="pin_length")
        uom_length   = st.selectbox("UOM", ["mm", "inches"], key="pin_uom_length")

        # Standard (può restare vuoto)
        standard     = st.selectbox("Standard", [""] + ["ISO 2338"], key="pin_standard")

        # Selezione materiale
        mtype_pin   = st.selectbox("Material Type", [""] + material_types, key="mtype_pin")
        pref_df_pin = materials_df[
            (materials_df["Material Type"] == mtype_pin) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_pin = sorted(pref_df_pin["Prefix"].unique()) if mtype_pin != "MISCELLANEOUS" else []
        mprefix_pin  = st.selectbox("Material Prefix", [""] + prefixes_pin, key="mprefix_pin")

        if mtype_pin == "MISCELLANEOUS":
            names_pin = materials_df[
                materials_df["Material Type"] == mtype_pin
            ]["Name"].dropna().drop_duplicates().tolist()
        else:
            names_pin = materials_df[
                (materials_df["Material Type"] == mtype_pin) &
                (materials_df["Prefix"] == mprefix_pin)
            ]["Name"].dropna().drop_duplicates().tolist()
        mname_pin = st.selectbox("Material Name", [""] + names_pin, key="mname_pin")

        # Nuovo campo Material Note
        material_note_pin = st.text_area("Material Note (opzionale)", height=80, key="pin_matnote")

        # Generazione output
        if st.button("Genera Output", key="gen_pin"):
            # Costruzione Material / FPD code
            if mtype_pin != "MISCELLANEOUS":
                materiale_pin = f"{mtype_pin} {mprefix_pin} {mname_pin}".strip()
                match_pin     = materials_df[
                    (materials_df["Material Type"] == mtype_pin) &
                    (materials_df["Prefix"] == mprefix_pin) &
                    (materials_df["Name"] == mname_pin)
                ]
            else:
                materiale_pin = mname_pin
                match_pin     = materials_df[
                    (materials_df["Material Type"] == mtype_pin) &
                    (materials_df["Name"] == mname_pin)
                ]
            codice_fpd_pin = match_pin["FPD Code"].values[0] if not match_pin.empty else ""

            # Costruzione descrizione
            descr_pin = (
                f"PIN, DOWEL - DIAMETER: {int(diameter)}{uom_diameter}, "
                f"LENGTH: {int(length)}{uom_length}"
            )
            if standard:
                descr_pin += f", {standard}"
            if material_note_pin:
                descr_pin += f", {material_note_pin}"

            # Aggiungi sempre l’asterisco all’inizio
            descr_pin = "*" + descr_pin

            # Memorizzo in session_state
            st.session_state["output_data"] = {
                "Item":               "56230…",
                "Description":        descr_pin,
                "Identificativo":     "6810-DOWEL PIN",
                "Classe ricambi":     "",
                "Categories":         "FASCIA ITE 5",
                "Catalog":            "",
                "Material":           materiale_pin,
                "FPD material code":  codice_fpd_pin,
                "Template":           "FPD_BUY_2",
                "ERP_L1":             "64_HARDWARE",
                "ERP_L2":             "14_PINS",
                "To supplier":        "",
                "Quality":            ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"pin_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"pin_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_pin = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="pin_dl_mode")
        item_code_pin    = st.text_input("Codice item", key="pin_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_pin"):
            if not item_code_pin:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_pin(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_pin = [
                    "\\%FN", item_code_pin,
                    "\\%TC", get_val_pin("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_pin("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_pin("Identificativo"), "TAB",
                    get_val_pin("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_pin('ERP_L1')}.{get_val_pin('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_pin("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_pin("Catalog"), "TAB", "TAB", "TAB",
                    get_val_pin("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_pin("FPD material code"), "TAB",
                    get_val_pin("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_pin("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_pin("Quality") if get_val_pin("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_pin("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_pin("To supplier") if get_val_pin("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_pin = "\t".join(dataload_fields_pin)
                st.text_area("Anteprima (per copia manuale)", dataload_string_pin, height=200)

                csv_buffer_pin = io.StringIO()
                writer_pin    = csv.writer(csv_buffer_pin, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_pin:
                    writer_pin.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_pin.getvalue(),
                    file_name=f"dataload_{item_code_pin}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- SHAFT, PUMP
if selected_part == "Shaft, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model_sha = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="sha_model")
        size_list_sha = size_df[size_df["Pump Model"] == model_sha]["Size"].dropna().tolist()
        size_sha = st.selectbox("Product/Pump Size", [""] + size_list_sha, key="sha_size")

        feature_1_sha = st.text_input("Additional Feature 1", key="sha_f1")
        feature_2_sha = st.text_input("Additional Feature 2", key="sha_f2")
        brg_type_sha = st.text_input("Bearing Type", key="sha_brg_type")
        brg_size_sha = st.text_input("Bearing Size", key="sha_brg_size")
        max_dia_sha = st.text_input("Max Diameter (mm)", key="sha_max_dia")
        max_len_sha = st.text_input("Max Length (mm)", key="sha_max_len")
        note_sha = st.text_area("Note (opzionale)", height=80, key="sha_note")
        dwg_sha = st.text_input("Dwg/doc number", key="sha_dwg")

        mtype_sha = st.selectbox("Material Type", [""] + material_types, key="sha_mtype")
        pref_df_sha = materials_df[(materials_df["Material Type"] == mtype_sha) & (materials_df["Prefix"].notna())]
        prefixes_sha = sorted(pref_df_sha["Prefix"].unique()) if mtype_sha != "MISCELLANEOUS" else []
        mprefix_sha = st.selectbox("Material Prefix", [""] + prefixes_sha, key="sha_mprefix")

        if mtype_sha == "MISCELLANEOUS":
            names_sha = materials_df[materials_df["Material Type"] == mtype_sha]["Name"].dropna().tolist()
        else:
            names_sha = materials_df[
                (materials_df["Material Type"] == mtype_sha) &
                (materials_df["Prefix"] == mprefix_sha)
            ]["Name"].dropna().tolist()

        mname_sha = st.selectbox("Material Name", [""] + names_sha, key="sha_mname")

        # ✅ Checkbox HF
        hf_service_sha = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="sha_hf")

        if st.button("Genera Output", key="sha_gen"):
            materiale_sha = f"{mtype_sha} {mprefix_sha} {mname_sha}".strip() if mtype_sha != "MISCELLANEOUS" else mname_sha
            match_sha = materials_df[
                (materials_df["Material Type"] == mtype_sha) &
                (materials_df["Prefix"] == mprefix_sha) &
                (materials_df["Name"] == mname_sha)
            ]
            codice_fpd_sha = match_sha["FPD Code"].values[0] if not match_sha.empty else ""

            descr_sha = f"SHAFT, PUMP - MODEL: {model_sha}, SIZE: {size_sha}, FEATURES: {feature_1_sha}, {feature_2_sha}, BRG TYPE: {brg_type_sha}, BRG SIZE: {brg_size_sha}, DIA: {max_dia_sha}, LENGTH: {max_len_sha}"
            if note_sha:
                descr_sha += f", NOTE: {note_sha}"
            if hf_service_sha:
                descr_sha += " [SQ113]"
            descr_sha = "*" + descr_sha

            quality_sha = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_sha else ""

            st.session_state["output_data"] = {
                "Item": "40231…",
                "Description": descr_sha,
                "Identificativo": "2100-SHAFT",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg_sha,
                "Material": materiale_sha,
                "FPD material code": codice_fpd_sha,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "25_SHAFTS",
                "To supplier": "",
                "Quality": quality_sha
            }


    # --- COLONNA 2: OUTPUT ---
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"shaft_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"shaft_{campo}")

    # --- COLONNA 3: DATALOAD ---
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_shaft = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="shaft_dl_mode")
        item_code_shaft    = st.text_input("Codice item", key="shaft_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_shaft"):
            if not item_code_shaft:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output nella colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_shaft(k):
                    v = data.get(k, "").strip()
                    return v if v else "."

                dataload_fields_shaft = [
                    "\\%FN", item_code_shaft,
                    "\\%TC", get_val_shaft("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_shaft("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_shaft("Identificativo"), "TAB",
                    get_val_shaft("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_shaft('ERP_L1')}.{get_val_shaft('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_shaft("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_shaft("Catalog"), "TAB", "TAB", "TAB",
                    get_val_shaft("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_shaft("FPD material code"), "TAB",
                    get_val_shaft("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_shaft("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_shaft("Quality") if get_val_shaft("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_shaft("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_shaft("To supplier") if get_val_shaft("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_shaft = "\t".join(dataload_fields_shaft)
                st.text_area("Anteprima (per copia manuale)", dataload_string_shaft, height=200)

                csv_buffer_shaft = io.StringIO()
                writer_shaft     = csv.writer(csv_buffer_shaft, quoting=csv.QUOTE_MINIMAL)
                for r in dataload_fields_shaft:
                    writer_shaft.writerow([r])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_shaft.getvalue(),
                    file_name=f"dataload_{item_code_shaft}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- BASEPLATE, PUMP
elif selected_part == "Baseplate, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model_bp    = st.selectbox(
            "Product/Pump Model",
            [""] + sorted(size_df["Pump Model"].dropna().unique()),
            key="bp_model"
        )
        size_list_bp = size_df[size_df["Pump Model"] == model_bp]["Size"].dropna().tolist()
        size_bp     = st.selectbox("Product/Pump Size", [""] + size_list_bp, key="bp_size")

        length_bp   = st.number_input("Length (mm)", min_value=0, step=1, format="%d", key="bp_length")
        width_bp    = st.number_input("Width (mm)",  min_value=0, step=1, format="%d", key="bp_width")
        weight_bp   = st.number_input("Weight (kg)", min_value=0, step=1, format="%d", key="bp_weight")
        sourcing_bp = st.selectbox("Sourcing", ["Europe", "India", "China"], key="bp_sourcing")

        note_bp     = st.text_area("Note (opzionale)", height=80, key="bp_note")
        dwg_bp      = st.text_input("Dwg/doc number", key="bp_dwg")

        mtype_bp    = st.selectbox("Material Type", [""] + material_types, key="bp_mtype")
        pref_df_bp  = materials_df[
            (materials_df["Material Type"] == mtype_bp) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bp = sorted(pref_df_bp["Prefix"].unique()) if mtype_bp != "MISCELLANEOUS" else []
        mprefix_bp  = st.selectbox("Material Prefix", [""] + prefixes_bp, key="bp_mprefix")

        if mtype_bp == "MISCELLANEOUS":
            names_bp = materials_df[materials_df["Material Type"] == mtype_bp]["Name"].dropna().tolist()
        else:
            names_bp = materials_df[
                (materials_df["Material Type"] == mtype_bp) &
                (materials_df["Prefix"] == mprefix_bp)
            ]["Name"].dropna().tolist()
        mname_bp = st.selectbox("Material Name", [""] + names_bp, key="bp_mname")

        if st.button("Genera Output", key="gen_bp"):
            if mtype_bp != "MISCELLANEOUS":
                materiale_bp = f"{mtype_bp} {mprefix_bp} {mname_bp}".strip()
                match_bp     = materials_df[
                    (materials_df["Material Type"] == mtype_bp) &
                    (materials_df["Prefix"] == mprefix_bp) &
                    (materials_df["Name"] == mname_bp)
                ]
            else:
                materiale_bp = mname_bp
                match_bp     = materials_df[
                    (materials_df["Material Type"] == mtype_bp) &
                    (materials_df["Name"] == mname_bp)
                ]
            codice_fpd_bp = match_bp["FPD Code"].values[0] if not match_bp.empty else ""

            # 1) Costruisci prima la descrizione base (senza asterisco)
            descr_bp = (
                f"BASEPLATE, PUMP - MODEL: {model_bp}, SIZE: {size_bp}, "
                f"LENGTH: {int(length_bp)}mm, WIDTH: {int(width_bp)}mm, WEIGHT: {int(weight_bp)}kg, "
                f"SOURCING: {sourcing_bp}"
            )
            if note_bp:
                descr_bp += f", NOTE: {note_bp}"
            descr_bp += f", {materiale_bp}"

            # 2) Aggiungi sempre l’asterisco all’inizio
            descr_bp = "*" + descr_bp

            st.session_state["output_data"] = {
                "Item":              "477…",
                "Description":       descr_bp,
                "Identificativo":    "6110-BASE PLATE",
                "Classe ricambi":    "",
                "Categories":        "FASCIA ITE 5",
                "Catalog":           "ARTVARI",
                "Disegno":           dwg_bp,
                "Material":          materiale_bp,
                "FPD material code": codice_fpd_bp,
                "Template":          "FPD_BUY_4",
                "ERP_L1":            "21_FABRICATIONS_OR_BASEPLATES",
                "ERP_L2":            "18_FOUNDATION_PLATE",
                "To supplier":       "",
                "Quality":           ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"bp_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"bp_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_bp = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bp_dl_mode")
        item_code_bp    = st.text_input("Codice item", key="bp_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_bp"):
            if not item_code_bp:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_bp(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_bp = [
                    "\\%FN", item_code_bp,
                    "\\%TC", get_val_bp("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_bp("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_bp("Identificativo"), "TAB",
                    get_val_bp("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_bp('ERP_L1')}.{get_val_bp('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_bp("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_bp("Catalog"), "TAB", "TAB", "TAB",
                    get_val_bp("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_bp("FPD material code"), "TAB",
                    get_val_bp("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_bp("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_bp("Quality") if get_val_bp("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_bp("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_bp("To supplier") if get_val_bp("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_bp = "\t".join(dataload_fields_bp)
                st.text_area("Anteprima (per copia manuale)", dataload_string_bp, height=200)

                csv_buffer_bp = io.StringIO()
                writer_bp    = csv.writer(csv_buffer_bp, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_bp:
                    writer_bp.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_bp.getvalue(),
                    file_name=f"dataload_{item_code_bp}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
# --- FLANGE, PIPE
if selected_part == "Flange, Pipe":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        pipe_type_fp = st.selectbox("Pipe Type", ["SW", "WN"], key="fp_pipe_type")
        size_fp = st.selectbox("Size", ["1/8”", "1/4”", "3/8”", "1/2”", "3/4”", "1”", "1 1/4”", "1 1/2”", "2”", "2 1/2”", "3”", "4”"], key="fp_size")
        face_fp = st.selectbox("Face Type", ["RF", "FF", "RJ"], key="fp_face")
        class_fp = st.text_input("Class (e.g. 150 Sch)", key="fp_class")
        material_fp = st.text_input("Material (e.g. A106-GR.B)", key="fp_material")
        add_feat_fp = st.text_input("Additional Features (opzionale)", key="fp_feat")

        # ✅ Checkbox HF
        hf_service_fp = st.checkbox("Is it an hydrofluoric acid (HF) alkylation service?", key="fp_hf")

        if st.button("Genera Output", key="fp_gen"):
            descr_fp = f"FLANGE TYPE: {pipe_type_fp}, SIZE: {size_fp}, FACE: {face_fp}, CLASS: {class_fp}, MATERIAL: {material_fp}"
            if add_feat_fp:
                descr_fp += f", FEATURES: {add_feat_fp}"
            if hf_service_fp:
                descr_fp += " [SQ113]"
            descr_fp = "*" + descr_fp

            quality_fp = "Applicable procedure: SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)" if hf_service_fp else ""

            st.session_state["output_data"] = {
                "Item": "50155…",
                "Description": descr_fp,
                "Identificativo": "1245-FLANGE",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "",
                "Disegno": "",
                "Material": "NOT AVAILABLE",
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "23_FLANGE",
                "ERP_L2": "13_OTHER",
                "To supplier": "",
                "Quality": quality_fp
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"fp_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"fp_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_fp = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="fp_dl_mode")
        item_code_fp     = st.text_input("Codice item", key="fp_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_fp"):
            if not item_code_fp:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_fp(k):
                    v = data.get(k, "").strip()
                    return v if v else "."

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
                    get_val_fp("Quality"), "\\^S",
                    "\\%FN", "TAB",
                    get_val_fp("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_fp("To supplier"), "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_fp = "\t".join(dataload_fields_fp)
                st.text_area("Anteprima (per copia manuale)", dataload_string_fp, height=200)

                csv_buffer_fp = io.StringIO()
                writer_fp = csv.writer(csv_buffer_fp, quoting=csv.QUOTE_MINIMAL)
                for r in dataload_fields_fp:
                    writer_fp.writerow([r])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_fp.getvalue(),
                    file_name=f"dataload_{item_code_fp}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
elif selected_part == "Gasket, Flat":
    st.subheader("Configurazione - Gasket, Flat")
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        thickness_gf = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f", key="gf_thickness")
        uom_gf        = st.selectbox("UOM", ["mm", "inches"], key="gf_uom")
        dwg_gf        = st.text_input("Disegno / Doc", key="gf_dwg")

        mtype_gf   = st.selectbox("Material Type", [""] + material_types, key="gf_mtype")
        pref_df_gf = materials_df[
            (materials_df["Material Type"] == mtype_gf) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_gf = sorted(pref_df_gf["Prefix"].unique()) if mtype_gf != "MISCELLANEOUS" else []
        mprefix_gf  = st.selectbox("Material Prefix", [""] + prefixes_gf, key="gf_mprefix")

        if mtype_gf == "MISCELLANEOUS":
            names_gf = materials_df[
                materials_df["Material Type"] == mtype_gf
            ]["Name"].dropna().drop_duplicates().tolist()
        else:
            names_gf = materials_df[
                (materials_df["Material Type"] == mtype_gf) &
                (materials_df["Prefix"] == mprefix_gf)
            ]["Name"].dropna().drop_duplicates().tolist()
        mname_gf = st.selectbox("Material Name", [""] + names_gf, key="gf_mname")

        material_note_gf = st.text_area("Material Note (opzionale)", height=80, key="gf_matnote")

        if st.button("Genera Output", key="gen_gf"):
            if mtype_gf != "MISCELLANEOUS":
                materiale_gf = f"{mtype_gf} {mprefix_gf} {mname_gf}".strip()
                match_gf     = materials_df[
                    (materials_df["Material Type"] == mtype_gf) &
                    (materials_df["Prefix"] == mprefix_gf) &
                    (materials_df["Name"] == mname_gf)
                ]
            else:
                materiale_gf = mname_gf
                match_gf     = materials_df[
                    (materials_df["Material Type"] == mtype_gf) &
                    (materials_df["Name"] == mname_gf)
                ]
            codice_fpd_gf = match_gf["FPD Code"].values[0] if not match_gf.empty else ""

            descr_gf = (
                f"GASKET, FLAT - THK: {thickness_gf}{uom_gf}, "
                f"MATERIAL: {materiale_gf}"
            )
            if material_note_gf:
                descr_gf += f", {material_note_gf}"

            descr_gf = "*" + descr_gf

            st.session_state["output_data"] = {
                "Item":              "50410…",
                "Description":       descr_gf,
                "Identificativo":    "4500-JOINT",
                "Classe ricambi":    "",
                "Categories":        "FASCIA ITE 5",
                "Catalog":           "ARTVARI",
                "Disegno":           dwg_gf,
                "Material":          materiale_gf,
                "FPD material code": codice_fpd_gf,
                "Template":          "FPD_BUY_1",
                "ERP_L1":            "55_GASKETS_OR_SEAL",
                "ERP_L2":            "17_FLAT",
                "To supplier":       "",
                "Quality":           ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"gf_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"gf_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_gf = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="gf_dl_mode")
        item_code_gf     = st.text_input("Codice item", key="gf_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_gf"):
            if not item_code_gf:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_gf(k):
                    v = data.get(k, "").strip()
                    return v if v else "."

                dataload_fields_gf = [
                    "\\%FN", item_code_gf,
                    "\\%TC", get_val_gf("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_gf("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_gf("Identificativo"), "TAB",
                    get_val_gf("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_gf('ERP_L1')}.{get_val_gf('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_gf("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_gf("Catalog"), "TAB", "TAB", "TAB",
                    get_val_gf("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_gf("FPD material code"), "TAB",
                    get_val_gf("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_gf("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_gf("Quality"), "\\^S",
                    "\\%FN", "TAB",
                    get_val_gf("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_gf("To supplier"), "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_gf = "\t".join(dataload_fields_gf)
                st.text_area("Anteprima (per copia manuale)", dataload_string_gf, height=200)

                csv_buffer_gf = io.StringIO()
                writer_gf = csv.writer(csv_buffer_gf, quoting=csv.QUOTE_MINIMAL)
                for r in dataload_fields_gf:
                    writer_gf.writerow([r])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_gf.getvalue(),
                    file_name=f"dataload_{item_code_gf}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
elif selected_part == "Screw, Cap":
    st.subheader("Configurazione - Screw, Cap")
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        screw_type = st.selectbox("Type", ["Socket Head", "Button Head", "Flat Head"], key="sc_type")
        size_sc    = st.text_input("Size", key="sc_size")
        length_sc  = st.text_input("Length", key="sc_length")
        note1_sc   = st.text_area("Note (opzionale)", height=60, key="sc_note1")

        mtype_sc   = st.selectbox("Material Type", [""] + material_types, key="sc_mtype")
        pref_df_sc = materials_df[
            (materials_df["Material Type"] == mtype_sc) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_sc = sorted(pref_df_sc["Prefix"].unique()) if mtype_sc != "MISCELLANEOUS" else []
        mprefix_sc  = st.selectbox("Material Prefix", [""] + prefixes_sc, key="sc_mprefix")

        if mtype_sc == "MISCELLANEOUS":
            names_sc = materials_df[
                materials_df["Material Type"] == mtype_sc
            ]["Name"].dropna().drop_duplicates().tolist()
        else:
            names_sc = materials_df[
                (materials_df["Material Type"] == mtype_sc) &
                (materials_df["Prefix"] == mprefix_sc)
            ]["Name"].dropna().drop_duplicates().tolist()
        mname_sc = st.selectbox("Material Name", [""] + names_sc, key="sc_mname")

        material_note_sc = st.text_area("Material Note (opzionale)", height=60, key="sc_matnote")

        if st.button("Genera Output", key="gen_sc"):
            if mtype_sc != "MISCELLANEOUS":
                materiale_sc = f"{mtype_sc} {mprefix_sc} {mname_sc}".strip()
                match_sc     = materials_df[
                    (materials_df["Material Type"] == mtype_sc) &
                    (materials_df["Prefix"] == mprefix_sc) &
                    (materials_df["Name"] == mname_sc)
                ]
            else:
                materiale_sc = mname_sc
                match_sc     = materials_df[
                    (materials_df["Material Type"] == mtype_sc) &
                    (materials_df["Name"] == mname_sc)
                ]
            codice_fpd_sc = match_sc["FPD Code"].values[0] if not match_sc.empty else ""

            descr_sc = f"*SCREW, CAP - TYPE: {screw_type}, SIZE: {size_sc}, LENGTH: {length_sc}"
            if note1_sc:
                descr_sc += f", {note1_sc}"
            descr_sc += f", {materiale_sc}"
            if material_note_sc:
                descr_sc += f", {material_note_sc}"

            st.session_state["output_data"] = {
                "Item":              "56310…",
                "Description":       descr_sc,
                "Identificativo":    "6805-CAP SCREW",
                "Classe ricambi":    "",
                "Categories":        "FASCIA ITE 5",
                "Catalog":           "ARTVARI",
                "Disegno":           "",
                "Material":          materiale_sc,
                "FPD material code": codice_fpd_sc,
                "Template":          "FPD_BUY_2",
                "ERP_L1":            "64_HARDWARE",
                "ERP_L2":            "15_SCREWS",
                "To supplier":       "",
                "Quality":           ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"sc_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"sc_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_sc = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="sc_dl_mode")
        item_code_sc     = st.text_input("Codice item", key="sc_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_sc"):
            if not item_code_sc:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_sc(k):
                    v = data.get(k, "").strip()
                    return v if v else "."

                dataload_fields_sc = [
                    "\\%FN", item_code_sc,
                    "\\%TC", get_val_sc("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_sc("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_sc("Identificativo"), "TAB",
                    get_val_sc("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_sc('ERP_L1')}.{get_val_sc('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_sc("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_sc("Catalog"), "TAB", "TAB", "TAB",
                    get_val_sc("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_sc("FPD material code"), "TAB",
                    get_val_sc("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_sc("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_sc("Quality"), "\\^S",
                    "\\%FN", "TAB",
                    get_val_sc("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_sc("To supplier"), "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_sc = "\t".join(dataload_fields_sc)
                st.text_area("Anteprima (per copia manuale)", dataload_string_sc, height=200)

                csv_buffer_sc = io.StringIO()
                writer_sc = csv.writer(csv_buffer_sc, quoting=csv.QUOTE_MINIMAL)
                for r in dataload_fields_sc:
                    writer_sc.writerow([r])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_sc.getvalue(),
                    file_name=f"dataload_{item_code_sc}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
elif selected_part == "Screw, Grub":
    st.subheader("Configurazione - Screw, Grub")
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        size_sg    = st.text_input("Size", key="sg_size")
        length_sg  = st.text_input("Length", key="sg_length")
        note1_sg   = st.text_area("Note (opzionale)", height=60, key="sg_note1")

        mtype_sg   = st.selectbox("Material Type", [""] + material_types, key="sg_mtype")
        pref_df_sg = materials_df[
            (materials_df["Material Type"] == mtype_sg) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_sg = sorted(pref_df_sg["Prefix"].unique()) if mtype_sg != "MISCELLANEOUS" else []
        mprefix_sg  = st.selectbox("Material Prefix", [""] + prefixes_sg, key="sg_mprefix")

        if mtype_sg == "MISCELLANEOUS":
            names_sg = materials_df[
                materials_df["Material Type"] == mtype_sg
            ]["Name"].dropna().drop_duplicates().tolist()
        else:
            names_sg = materials_df[
                (materials_df["Material Type"] == mtype_sg) &
                (materials_df["Prefix"] == mprefix_sg)
            ]["Name"].dropna().drop_duplicates().tolist()
        mname_sg = st.selectbox("Material Name", [""] + names_sg, key="sg_mname")

        material_note_sg = st.text_area("Material Note (opzionale)", height=60, key="sg_matnote")

        if st.button("Genera Output", key="gen_sg"):
            if mtype_sg != "MISCELLANEOUS":
                materiale_sg = f"{mtype_sg} {mprefix_sg} {mname_sg}".strip()
                match_sg     = materials_df[
                    (materials_df["Material Type"] == mtype_sg) &
                    (materials_df["Prefix"] == mprefix_sg) &
                    (materials_df["Name"] == mname_sg)
                ]
            else:
                materiale_sg = mname_sg
                match_sg     = materials_df[
                    (materials_df["Material Type"] == mtype_sg) &
                    (materials_df["Name"] == mname_sg)
                ]
            codice_fpd_sg = match_sg["FPD Code"].values[0] if not match_sg.empty else ""

            descr_sg = f"*SCREW, GRUB - SIZE: {size_sg}, LENGTH: {length_sg}"
            if note1_sg:
                descr_sg += f", {note1_sg}"
            descr_sg += f", {materiale_sg}"
            if material_note_sg:
                descr_sg += f", {material_note_sg}"

            st.session_state["output_data"] = {
                "Item":              "56320…",
                "Description":       descr_sg,
                "Identificativo":    "6806-GRUB SCREW",
                "Classe ricambi":    "",
                "Categories":        "FASCIA ITE 5",
                "Catalog":           "ARTVARI",
                "Disegno":           "",
                "Material":          materiale_sg,
                "FPD material code": codice_fpd_sg,
                "Template":          "FPD_BUY_2",
                "ERP_L1":            "64_HARDWARE",
                "ERP_L2":            "15_SCREWS",
                "To supplier":       "",
                "Quality":           ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"sg_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"sg_{campo}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_sg = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="sg_dl_mode")
        item_code_sg     = st.text_input("Codice item", key="sg_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_sg"):
            if not item_code_sg:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_sg(k):
                    v = data.get(k, "").strip()
                    return v if v else "."

                dataload_fields_sg = [
                    "\\%FN", item_code_sg,
                    "\\%TC", get_val_sg("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_sg("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_sg("Identificativo"), "TAB",
                    get_val_sg("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_sg('ERP_L1')}.{get_val_sg('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_sg("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_sg("Catalog"), "TAB", "TAB", "TAB",
                    get_val_sg("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_sg("FPD material code"), "TAB",
                    get_val_sg("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_sg("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_sg("Quality"), "\\^S",
                    "\\%FN", "TAB",
                    get_val_sg("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_sg("To supplier"), "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_sg = "\t".join(dataload_fields_sg)
                st.text_area("Anteprima (per copia manuale)", dataload_string_sg, height=200)

                csv_buffer_sg = io.StringIO()
                writer_sg = csv.writer(csv_buffer_sg, quoting=csv.QUOTE_MINIMAL)
                for r in dataload_fields_sg:
                    writer_sg.writerow([r])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_sg.getvalue(),
                    file_name=f"dataload_{item_code_sg}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")


# --- Footer (non fisso, subito dopo i contenuti)
footer_html = """
<style>
.footer {
    width: 100%;
    background-color: #f0f2f6;
    color: #444444;
    text-align: center;
    padding: 0.5rem 0;
    font-size: 0.9rem;
    border-top: 1px solid #e1e3e6;
    margin-top: 2rem;
}
</style>
<div class="footer">
    © 2025 Flowserve - Desio Order Engineering – mailto:dzecchinel@flowserve.com
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
