import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

import io

def export_all_fields_to_excel(input_data, output_data, dataload_info, categoria="", parte=""):
    export_dict = {}

    # Intestazione con categoria e parte
    export_dict["Categoria"] = categoria
    export_dict["Parte"] = parte

    # Input
    for k, v in input_data.items():
        export_dict[f"Input - {k}"] = v

    # Output
    for k, v in output_data.items():
        if isinstance(v, list):
            export_dict[f"Output - {k}"] = "\n".join(v)
        else:
            export_dict[f"Output - {k}"] = v

    # DataLoad
    for k, v in dataload_info.items():
        export_dict[f"DataLoad - {k}"] = v

    df = pd.DataFrame(export_dict.items(), columns=["Campo", "Valore"])

    # Scrive su file Excel in memoria
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Oracle Item")
    buffer.seek(0)
    return buffer


# Caricamento dati materiali da file Excel
material_df = pd.read_excel("dati_config4.xlsx", sheet_name="Materials")

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
@st.cache_data
def get_fpd_code(mat_type, mat_prefix, mat_name):
    row = materials_df[
        (materials_df["Material Type"] == mat_type) &
        (materials_df["Prefix"] == mat_prefix) &
        (materials_df["Name"] == mat_name)
    ]
    if not row.empty and "FPD Code" in row.columns:
        return row.iloc[0]["FPD Code"]
    return "NOT AVAILABLE"


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
    ],
      "Casting": [
        "Casing cover casting",
        "Casing casting",
        "Bearing housing casting",
        "Impeller casting",
        "Impeller nut casting",
        "Shaft casting",
        "Throttling bush casting",
        "Pump bowl casting",
        "Bearing bracket casting",
        "Discharge elbow casting",
        "Bearing cover casting",
        "Diffuser casting",
        "Inducer casting",
        "Wear plate casting",
        "Shaft wear sleeve casting"
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

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="casing_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="casing_size")

        feature_1 = ""
        special = ["HDO", "DMX", "WXB", "WIK"]
        if model not in special:
            f1_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="casing_f1")

        feature_2 = ""
        if model in ["HPX", "HED"]:
            f2_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key="casing_f2")

        note = st.text_area("Note (opzionale)", height=80, key="casing_note")
        dwg = st.text_input("Dwg/doc number", key="casing_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="casing_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="casing_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="casing_mname")

        # ✅ Checkbox qualità extra
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="casing_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="casing_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="casing_overlay")
        hvof = st.checkbox("HVOF coating?", key="casing_hvof")
        water = st.checkbox("Water service?", key="casing_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="casing_stamicarbon")

        if st.button("Genera Output", key="casing_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            tag_string = " ".join(sq_tags)
            quality = "\n".join(quality_lines)

            descr = f"CASING, PUMP - MODEL: {model}, SIZE: {size}, FEATURES: {feature_1}, {feature_2}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "40201…",
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
                "ERP_L2": "15_CASING",
                "To supplier": "",
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
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

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="ccov_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="ccov_size")
        feature_1 = st.text_input("Additional Feature 1", key="ccov_feat1")
        feature_2 = st.text_input("Additional Feature 2", key="ccov_feat2")
        note = st.text_area("Note", height=80, key="ccov_note")
        dwg = st.text_input("Dwg/doc number", key="ccov_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="ccov_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="ccov_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="ccov_mname")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="ccov_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="ccov_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="ccov_overlay")
        hvof = st.checkbox("HVOF coating?", key="ccov_hvof")
        water = st.checkbox("Water service?", key="ccov_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="ccov_stamicarbon")

        if st.button("Genera Output", key="ccov_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"CASING COVER, PUMP - MODEL: {model}, SIZE: {size}, FEATURES: {feature_1} {feature_2}".strip()
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "1111…",
                "Description": descr,
                "Identificativo": "1200-CASING COVER",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "21_CASING",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
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
if selected_part == "Impeller, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="imp_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="imp_size")
        feature_1 = st.text_input("Additional Feature 1", key="imp_feat1")
        feature_2 = st.text_input("Additional Feature 2", key="imp_feat2")
        note = st.text_area("Note", height=80, key="imp_note")
        dwg = st.text_input("Dwg/doc number", key="imp_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="imp_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="imp_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="imp_mname")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="imp_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="imp_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="imp_overlay")
        hvof = st.checkbox("HVOF coating?", key="imp_hvof")
        water = st.checkbox("Water service?", key="imp_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="imp_stamicarbon")

        if st.button("Genera Output", key="imp_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"IMPELLER, PUMP - MODEL: {model}, SIZE: {size}, FEATURES: {feature_1} {feature_2}".strip()
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "3110…",
                "Description": descr,
                "Identificativo": "3110-IMPELLER",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "22_IMPELLERS",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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
if selected_part == "Balance Bushing, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bbush_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="bbush_size")
        note = st.text_area("Note", height=80, key="bbush_note")
        dwg = st.text_input("Dwg/doc number", key="bbush_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="bbush_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="bbush_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="bbush_mname")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bbush_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bbush_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bbush_overlay")
        hvof = st.checkbox("HVOF coating?", key="bbush_hvof")
        water = st.checkbox("Water service?", key="bbush_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bbush_stamicarbon")

        if st.button("Genera Output", key="bbush_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"BALANCE BUSHING, PUMP - MODEL: {model}, SIZE: {size}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "6231…",
                "Description": descr,
                "Identificativo": "6231-BALANCE DRUM BUSH",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "16_BUSHING",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)


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
if selected_part == "Balance Drum, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bdrum_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="bdrum_size")
        note = st.text_area("Note", height=80, key="bdrum_note")
        dwg = st.text_input("Dwg/doc number", key="bdrum_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="bdrum_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="bdrum_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="bdrum_mname")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bdrum_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bdrum_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bdrum_overlay")
        hvof = st.checkbox("HVOF coating?", key="bdrum_hvof")
        water = st.checkbox("Water service?", key="bdrum_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bdrum_stamicarbon")

        if st.button("Genera Output", key="bdrum_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"BALANCE DRUM, PUMP - MODEL: {model}, SIZE: {size}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "6231…",
                "Description": descr,
                "Identificativo": "6231-BALANCE DRUM BUSH",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "16_BUSHING",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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
if selected_part == "Balance Disc, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bdisc_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="bdisc_size")
        note = st.text_area("Note", height=80, key="bdisc_note")
        dwg = st.text_input("Dwg/doc number", key="bdisc_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="bdisc_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="bdisc_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="bdisc_mname")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bdisc_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bdisc_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bdisc_overlay")
        hvof = st.checkbox("HVOF coating?", key="bdisc_hvof")
        water = st.checkbox("Water service?", key="bdisc_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bdisc_stamicarbon")

        if st.button("Genera Output", key="bdisc_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"BALANCE DISC, PUMP - MODEL: {model}, SIZE: {size}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "6210…",
                "Description": descr,
                "Identificativo": "6210-BALANCE DISC",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "30_DISK",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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
if selected_part == "Gate, Valve":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.text_input("Valve Model", key="gate_model")
        size = st.text_input("Valve Size", key="gate_size")
        rating = st.text_input("Rating/Class", key="gate_rating")
        note = st.text_area("Note", height=80, key="gate_note")
        dwg = st.text_input("Dwg/doc number", key="gate_dwg")

        mtype = st.selectbox("Material Type", [""] + material_types, key="gate_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="gate_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="gate_mname")

        # Checkbox solo per HF e Stamicarbon
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="gate_hf")
        stamicarbon = st.checkbox("Stamicarbon?", key="gate_stamicarbon")

        if st.button("Genera Output", key="gate_gen"):
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
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"GATE VALVE - MODEL: {model}, SIZE: {size}, RATING: {rating}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "70222…",
                "Description": descr,
                "Identificativo": "7100-GATE VALVE",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "VALVOLA",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "40_VALVES",
                "ERP_L2": "41_GATE_VALVES",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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

    with col1:
        st.subheader("✏️ Input")

        winding_options = {
            "304 stainless steel": ("Yellow", "RAL1021"),
            "316L stainless steel": ("Green", "RAL6005"),
            "317L stainless steel": ("Maroon", "RAL3003"),
            "321 stainless steel": ("Turquoise", "RAL5018"),
            "347 stainless steel": ("Blue", "RAL5017"),
            "MONEL": ("Orange", "RAL2003"),
            "Nickel": ("Red", "RAL3024"),
            "Titanium": ("Purple", "RAL4003"),
            "Alloy 20": ("Black", "RAL9005"),
            "INCONEL 600": ("Gold", "RAL1004"),
            "HASTELLOY B": ("Brown", "RAL8003"),
            "HASTELLOY C": ("Beige", "RAL1011"),
            "INCOLOY 800": ("White", "RAL9010"),
            "DUPLEX": ("Yellow+Blue", "RAL1021+5017"),
            "SUPERDUPLEX": ("Red+Black", "RAL3020+9005"),
            "ALLOY 825": ("Orange+Green", "RAL2003+6005"),
            "UNS S31254": ("Orange+Blue", "RAL2003+5017"),
            "ZYRCONIUM 702": ("Gold+Green", "RAL1004+6005"),
            "INCONEL X750HT": ("Gold+Black", "RAL1004+9005")
        }

        filler_options = {
            "Graphite": ("Gray", "RAL7011"),
            "PTFE": ("White", "RAL9010"),
            "Ceramic": ("Light Green", "RAL6021"),
            "Verdicarb (Mica Graphite)": ("Pink", "RAL3015")
        }

        rating_mapping = {
            "STANDARD PRESSURE - m=3; y=10000psi (1 stripe)": ("STANDARD PRESSURE", "m=3; y=10000psi", "1 stripe"),
            "HIGH PRESSURE - m=3; y=17500psi (2 stripes)": ("HIGH PRESSURE", "m=3; y=17500psi", "2 stripes"),
            "ULTRA HIGH PRESSURE - m=3; y=23500psi (3 stripes)": ("ULTRA HIGH PRESSURE", "m=3; y=23500psi", "3 stripes")
        }

        winding_gsw = st.selectbox("Winding Material", list(winding_options.keys()), key="gsw_winding")
        filler_gsw = st.selectbox("Filler", list(filler_options.keys()), key="gsw_filler")
        out_dia_gsw = st.text_input("Outer Diameter (MM)", key="gsw_out_dia")
        in_dia_gsw = st.text_input("Inner Diameter (MM)", key="gsw_in_dia")
        thickness_gsw = st.text_input("Thickness (MM)", key="gsw_thick")
        rating_gsw = st.selectbox("Rating", list(rating_mapping.keys()), key="gsw_rating")
        dwg_gsw = st.text_input("Dwg/doc number", key="gsw_dwg")
        note_gsw = st.text_area("Note (opzionale)", height=80, key="gsw_note")
        hf_service_gsw = st.checkbox("Is it a hydrofluoric acid (HF) alkylation service?", key="gsw_hf")

        if st.button("Genera Output", key="gsw_gen"):
            color1, ral1 = winding_options[winding_gsw]
            color2, ral2 = filler_options[filler_gsw]
            pressure_label, rating_descr, stripe = rating_mapping[rating_gsw]

            descr_gsw = (
                f"*GASKET, SPIRAL WOUND - WINDING: {winding_gsw}, FILLER: {filler_gsw}, "
                f"OD: {out_dia_gsw} (MM), ID: {in_dia_gsw} (MM), THK: {thickness_gsw} (MM), "
                f"RATING: {pressure_label} - {rating_descr}, "
                f"COLOR CODE: {color1} {ral1} / {color2} {ral2} ({stripe}) [SQ174]"
            )
            if hf_service_gsw:
                descr_gsw += " <SQ113>"
            if note_gsw:
                descr_gsw += f", NOTE: {note_gsw}"

            quality = "SQ 174 - Casing/Cover pump spiral wound gaskets: Specification for Mechanical properties, applicable materials and dimensions"
            if hf_service_gsw:
                quality += "\nSQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)"

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
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            output_data = st.session_state["output_data"]
            for campo, valore in output_data.items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=100, key=f"sw_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"sw_{campo}")

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
if selected_part == "Bolt, Eye":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        size = st.text_input("Size", key="beye_size")
        length = st.text_input("Length", key="beye_length")
        material = st.text_input("Material", key="beye_material")
        note = st.text_area("Note", height=80, key="beye_note")
        dwg = st.text_input("Dwg/doc number", key="beye_dwg")

        # Stamicarbon checkbox
        stamicarbon = st.checkbox("Stamicarbon?", key="beye_stamicarbon")

        if st.button("Genera Output", key="beye_gen"):
            sq_tags = []
            quality_lines = []

            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"EYE BOLT - SIZE: {size}, LENGTH: {length}, MATERIAL: {material}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "56120…",
                "Description": descr,
                "Identificativo": "6540-EYE BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": material,
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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
# --- GASKET, RING TYPE JOINT
if selected_part == "Gasket, Ring Type Joint":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        style_rtj = st.text_input("Style (e.g. R, RX, BX)", key="rtj_style")
        size_rtj = st.text_input("Size (e.g. 2”, 3-1/16”)", key="rtj_size")
        material_rtj = st.text_input("Material", key="rtj_material")
        note_rtj = st.text_area("Note (opzionale)", height=80, key="rtj_note")
        dwg_rtj = st.text_input("Dwg/doc number", key="rtj_dwg")
        hf_service_rtj = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="rtj_hf")

        if st.button("Genera Output", key="rtj_gen"):
            descr_rtj = (
                f"GASKET, RTJ - STYLE: {style_rtj}, SIZE: {size_rtj}, MATERIAL: {material_rtj}"
            )
            if note_rtj:
                descr_rtj += f", NOTE: {note_rtj}"
            if hf_service_rtj:
                descr_rtj += " <SQ113>"
                quality = "SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)"
            else:
                quality = ""

            descr_rtj = "*" + descr_rtj

            st.session_state["output_data"] = {
                "Item": "50413…",
                "Description": descr_rtj,
                "Identificativo": "4510-GASKET RTJ",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_rtj,
                "Material": material_rtj,
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_1",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "17_RTJ",
                "To supplier": "",
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo in ["Description", "Quality"]:
                    st.text_area(campo, value=valore, height=120, key=f"rtj_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"rtj_{campo}")

    # COLONNA 3 – DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_rtj = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="rtj_dl_mode")
        item_code_rtj = st.text_input("Codice item", key="rtj_item_code")
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
        hf_service_stu = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="stu_hf")

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
                descr_stu += " <SQ113>"
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
        hf_service_nut = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="nut_hf")

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
                descr_nut += " <SQ113>"
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

    with col1:
        st.subheader("✏️ Input")
        wear_type = st.selectbox("Type", ["Stationary", "Rotary"], key="ring_type")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="ring_model")
        internal_dia = st.text_input("Internal diameter (mm)", key="ring_id")
        outer_dia = st.text_input("Outer diameter (mm)", key="ring_od")
        increased_clearance = st.selectbox("Increased clearance", ["No", "Yes"], key="ring_clearance")
        note = st.text_area("Note", height=80, key="ring_note")
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

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="ring_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="ring_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="ring_overlay")
        hvof = st.checkbox("HVOF coating?", key="ring_hvof")
        water = st.checkbox("Water service?", key="ring_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="ring_stamicarbon")

        if st.button("Genera Output", key="ring_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]

            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if tmt_service:
                sq_tags.append("[SQ137]")
                quality_lines.append("SQ 137 - Pompe di Processo con Rivestimento Protettivo (TMT/HVOF)")
            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            identificativo = "2300-IMPELLER WEAR RING" if wear_type == "Rotary" else "1500-CASING WEAR RING"
            item_code = "40224…" if wear_type == "Rotary" else "40223…"

            descr = f"{wear_type.upper()} WEAR RING, PUMP - MODEL: {model}, ID: {internal_dia}, OD: {outer_dia}"
            if increased_clearance == "Yes":
                descr += ", INCREASED CLEARANCE"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": item_code,
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

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
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
if selected_part == "Pin, Dowel":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        size = st.text_input("Size", key="pdowel_size")
        length = st.text_input("Length", key="pdowel_length")
        material = st.text_input("Material", key="pdowel_material")
        note = st.text_area("Note", height=80, key="pdowel_note")
        dwg = st.text_input("Dwg/doc number", key="pdowel_dwg")

        # Stamicarbon checkbox
        stamicarbon = st.checkbox("Stamicarbon?", key="pdowel_stamicarbon")

        if st.button("Genera Output", key="pdowel_gen"):
            sq_tags = []
            quality_lines = []

            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"DOWEL PIN - SIZE: {size}, LENGTH: {length}, MATERIAL: {material}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "56300…",
                "Description": descr,
                "Identificativo": "6560-DOWEL PIN",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": material,
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "13_STANDARD_PIN",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product/Pump Model", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="sh_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Product/Pump Size", [""] + size_list, key="sh_size")

        feature_1 = st.text_input("Additional feature 1", key="sh_f1")
        feature_2 = st.text_input("Additional feature 2", key="sh_f2")
        brg_type = st.text_input("Brg. type", key="sh_brg_type")
        brg_size = st.text_input("Brg. Size", key="sh_brg_size")
        diameter = st.text_input("Max diameter (mm)", key="sh_diam")
        length = st.text_input("Max length (mm)", key="sh_len")
        dwg = st.text_input("Dwg/doc number", key="sh_dwg")
        note = st.text_area("Note", height=80, key="sh_note")

        mtype = st.selectbox("Material Type", [""] + material_types, key="sh_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="sh_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="sh_mname")

        # ✅ Checkbox aggiuntive
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="sh_overlay")
        hvof = st.checkbox("HVOF coating?", key="sh_hvof")
        water = st.checkbox("Water service?", key="sh_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="sh_stamicarbon")

        if st.button("Genera Output", key="sh_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            quality_lines = [
                "SQ 60 - Procedura di Esecuzione del Run-Out per Alberi e Rotori di Pompe",
                "DE 3513.014 - Shaft Demagnetization",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]
            sq_tags = ["[SQ60]", "[DE3513.014]", "[CORP-ENG-0115]"]

            if overlay:
                sq_tags.append("<PQ72>")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"SHAFT, PUMP - MODEL: {model}, SIZE: {size}, BRG TYPE: {brg_type}, BRG SIZE: {brg_size}, DIAM: {diameter}, LENGTH: {length}, FEATURES: {feature_1}, {feature_2}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "40231…",
                "Description": descr,
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
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)


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
elif selected_part == "Baseplate, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Pump Type", size_df["Pump Model"].dropna().unique())
        size = st.selectbox("Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique())

        length = st.number_input("Length (mm)", min_value=0)
        width = st.number_input("Width (mm)", min_value=0)
        weight = st.number_input("Weight (kg)", min_value=0)

        sourcing = st.selectbox("Sourcing", ["EUROPEAN", "INDIAN", "CHINESE"])

        drawing = st.text_input("DWG/Doc")
        note = st.text_area("Note")
        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="base_mat_type")

        filtered_prefix = materials_df[materials_df["Material Type"] == mat_type]["Prefix"].dropna().unique()
        mat_prefix = st.selectbox("Material Prefix", filtered_prefix, key="base_mat_prefix")
        filtered_names = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]["Name"].dropna().drop_duplicates()
        mat_name = st.selectbox("Material Name", filtered_names, key="base_mat_name")
        mat_note = st.text_input("Material Note")

        if st.button("Genera Output"):
            item = "477..."
            ident = "BASE"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            drawing_out = drawing
            material = f"{mat_type} {mat_prefix} {mat_name}".strip()
            fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
            template = "FPD_BUY_4"
            erp1 = "21_FABRICATION_OR_BASEPLATES"
            erp2 = "22_BASEPLATE"
            to_supplier = sourcing

            descr_parts = [
                f"*{ident}",
                f"{model}-{size}",
                f"{length}x{width} mm",
                f"{weight} kg",
                note,
                material,
                mat_note,
                "[SQ53]",
                "[CORP-ENG-0234]"
            ]

            descr = " ".join([d for d in descr_parts if d])

            quality = [
                "SQ 53 - HORIZONTAL PUMP BASEPLATES CHECKING PROCEDURE",
                "CORP-ENG-0234 - Procedure for Baseplate Inspection J4-11"
            ]


            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": drawing_out,
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": to_supplier,
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")

        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="base_out1")
            st.text_area("Description", value=data["Description"], height=120, key="base_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="base_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="base_out4")
            st.text_input("Categories", value=data["Categories"], key="base_out5")
            st.text_input("Catalog", value=data["Catalog"], key="base_out6")
            st.text_input("Disegno", value=data["Disegno"], key="base_out7")
            st.text_input("Material", value=data["Material"], key="base_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="base_out9")
            st.text_input("Template", value=data["Template"], key="base_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="base_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="base_out12")
            st.text_input("To Supplier", value=data["To Supplier"], key="base_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=100, key="base_out14")

    with col3:
        st.subheader("🧾 DataLoad")

        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="base_op")
        item_code_input = st.text_input("Codice item", key="base_item_code")

        if "output_data" in st.session_state and item_code_input:
            dataload_string = generate_dataload_string(
                operation,
                item_code_input,
                st.session_state["output_data"]["Description"],
                st.session_state["output_data"]["Catalog"],
                st.session_state["output_data"]["Template"],
                st.session_state["output_data"]["ERP L1"],
                st.session_state["output_data"]["ERP L2"],
                st.session_state["output_data"]["Disegno"],
                st.session_state["output_data"]["Material"],
                st.session_state["output_data"]["FPD material code"]
            )
            st.text_area("📋 Copia stringa per DataLoad", dataload_string, height=200)

    if "output_data" in st.session_state:
        input_data = {
            "Pump Type": model,
            "Pump Size": size,
            "Length (mm)": length,
            "Width (mm)": width,
            "Weight (kg)": weight,
            "Sourcing": sourcing,
            "DWG/Doc": drawing,
            "Note": note,
            "Material Type": mat_type,
            "Material Prefix": mat_prefix,
            "Material Name": mat_name,
            "Material Note": mat_note
        }

        dataload_info = {
            "Item code": item_code_input if item_code_input else "(non specificato)",
            "Operazione": operation if operation else "(non specificata)",
            "Stringa DataLoad": dataload_string if 'dataload_string' in locals() else "(non generata)"
        }

        excel_filexcel_file = export_all_fields_to_excel(
    input_data,
    st.session_state["output_data"],
    dataload_info,
    categoria="Machined",
    parte="Baseplate, Pump"
)
e = export_all_fields_to_excel(input_data, st.session_state["output_data"], dataload_info)

        st.download_button(
            label="📥 Scarica tutto in Excel",
            data=excel_file,
            file_name=f"oracle_export_{item_code_input or 'item'}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )



# --- FLANGE, PIPE
if selected_part == "Flange, Pipe":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        pipe_type = st.selectbox("Pipe Type", ["SW", "WN"], key="flange_type")
        pipe_size = st.selectbox("Size", [
            "1/8”", "1/4”", "3/8”", "1/2”", "3/4”", "1”", "1-1/4”", "1-1/2”", "2”",
            "2-1/2”", "3”", "4”"
        ], key="flange_size")
        face_type = st.selectbox("Face Type", ["RF", "FF", "RJ"], key="flange_face")
        pressure_class = st.text_input("Class (e.g. 150 Sch)", key="flange_class")
        material_flange = st.text_input("Material", key="flange_material")
        note_flange = st.text_input("Additional Features (optional)", key="flange_note")
        hf_service_flange = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="flange_hf")

        if st.button("Genera Output", key="flange_gen"):
            descr = (
                f"FLANGE, PIPE - TYPE: {pipe_type}, SIZE: {pipe_size}, FACE: {face_type}, "
                f"CLASS: {pressure_class}, MATERIAL: {material_flange}"
            )
            if note_flange:
                descr += f", NOTE: {note_flange}"
            if hf_service_flange:
                descr += " <SQ113>"
                quality = "SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)"
            else:
                quality = ""

            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "50155…",
                "Description": descr,
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
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo in ["Description", "Quality"]:
                    st.text_area(campo, value=valore, height=120, key=f"fl_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"fl_{campo}")

    # COLONNA 3 – DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_fl = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="fl_dl_mode")
        item_code_fl = st.text_input("Codice item", key="fl_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_fl"):
            if not item_code_fl:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]

                def get_val_fl(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_fl = [
                    "\\%FN", item_code_fl,
                    "\\%TC", get_val_fl("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_fl("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_fl("Identificativo"), "TAB",
                    get_val_fl("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_fl('ERP_L1')}.{get_val_fl('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_fl("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_fl("Catalog"), "TAB", "TAB", "TAB",
                    get_val_fl("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_fl("FPD material code"), "TAB",
                    get_val_fl("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_fl("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_fl("Quality") if get_val_fl("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_fl("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_fl("To supplier") if get_val_fl("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_fl = "\t".join(dataload_fields_fl)
                st.text_area("Anteprima (per copia manuale)", dataload_string_fl, height=200)

                csv_buffer_fl = io.StringIO()
                writer_fl = csv.writer(csv_buffer_fl, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_fl:
                    writer_fl.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_fl.getvalue(),
                    file_name=f"dataload_{item_code_fl}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- GASKET, FLAT
if selected_part == "Gasket, Flat":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        thickness_gf = st.text_input("Thickness", key="gf_thickness")
        unit_gf = st.selectbox("Unit of Measure", ["mm", "inch"], key="gf_unit")
        dwg_gf = st.text_input("Dwg/doc number", key="gf_dwg")
        material_gf = st.text_input("Material", key="gf_material")
        note_gf = st.text_area("Note (opzionale)", height=80, key="gf_note")
        hf_service_gf = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="gf_hf")

        if st.button("Genera Output", key="gf_gen"):
            descr_gf = (
                f"GASKET, FLAT - THICKNESS: {thickness_gf}{unit_gf.upper()}, MATERIAL: {material_gf}"
            )
            if note_gf:
                descr_gf += f", NOTE: {note_gf}"
            if hf_service_gf:
                descr_gf += " <SQ113>"
                quality = "SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)"
            else:
                quality = ""

            descr_gf = "*" + descr_gf

            st.session_state["output_data"] = {
                "Item": "50412…",
                "Description": descr_gf,
                "Identificativo": "4510-GASKET FLAT",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_gf,
                "Material": material_gf,
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_1",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "18_FLAT",
                "To supplier": "",
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo in ["Description", "Quality"]:
                    st.text_area(campo, value=valore, height=120, key=f"gf_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"gf_{campo}")

    # COLONNA 3 – DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_gf = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="gf_dl_mode")
        item_code_gf = st.text_input("Codice item", key="gf_item_code")
        if st.button("Genera stringa DataLoad", key="gen_dl_gf"):
            if not item_code_gf:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]

                def get_val_gf(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

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
                    get_val_gf("Quality") if get_val_gf("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_gf("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_gf("To supplier") if get_val_gf("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]
                dataload_string_gf = "\t".join(dataload_fields_gf)
                st.text_area("Anteprima (per copia manuale)", dataload_string_gf, height=200)

                csv_buffer_gf = io.StringIO()
                writer_gf = csv.writer(csv_buffer_gf, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_gf:
                    writer_gf.writerow([riga])
                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_gf.getvalue(),
                    file_name=f"dataload_{item_code_gf}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

if selected_part == "Screw, Cap":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        size = st.text_input("Size", key="scap_size")
        length = st.text_input("Length", key="scap_length")
        material = st.text_input("Material", key="scap_material")
        note = st.text_area("Note", height=80, key="scap_note")
        dwg = st.text_input("Dwg/doc number", key="scap_dwg")

        # Stamicarbon checkbox
        stamicarbon = st.checkbox("Stamicarbon?", key="scap_stamicarbon")

        if st.button("Genera Output", key="scap_gen"):
            sq_tags = []
            quality_lines = []

            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"CAP SCREW - SIZE: {size}, LENGTH: {length}, MATERIAL: {material}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "56200…",
                "Description": descr,
                "Identificativo": "6530-CAP SCREW",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": material,
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

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
if selected_part == "Screw, Grub":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        size = st.text_input("Size", key="sgrub_size")
        length = st.text_input("Length", key="sgrub_length")
        material = st.text_input("Material", key="sgrub_material")
        note = st.text_area("Note", height=80, key="sgrub_note")
        dwg = st.text_input("Dwg/doc number", key="sgrub_dwg")

        # Stamicarbon checkbox
        stamicarbon = st.checkbox("Stamicarbon?", key="sgrub_stamicarbon")

        if st.button("Genera Output", key="sgrub_gen"):
            sq_tags = []
            quality_lines = []

            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            quality = "\n".join(quality_lines)
            tag_string = " ".join(sq_tags)

            descr = f"GRUB SCREW - SIZE: {size}, LENGTH: {length}, MATERIAL: {material}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}"
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "56210…",
                "Description": descr,
                "Identificativo": "6520-GRUB SCREW",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": material,
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)


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



if selected_part in [
    "Casing cover casting",
    "Casing casting",
    "Bearing housing casting",
    "Impeller casting",
    "Impeller nut casting",
    "Shaft casting",
    "Throttling bush casting",
    "Pump bowl casting",
    "Bearing bracket casting",
    "Discharge elbow casting",
    "Bearing cover casting",
    "Diffuser casting",
    "Inducer casting",
    "Wear plate casting",
    "Shaft wear sleeve casting"
]:
    identificativo = selected_part
    col_input, col_output, col_dataload = st.columns(3, gap="small")

    with col_input:
        st.markdown("### 📥 Input")
        base_pattern = st.text_input("Base pattern")
        mod1 = st.text_input("Pattern modification 1")
        mod2 = st.text_input("Pattern modification 2")
        mod3 = st.text_input("Pattern modification 3")
        mod4 = st.text_input("Pattern modification 4")
        mod5 = st.text_input("Pattern modification 5")
        note = st.text_input("Note")
        casting_drawing = st.text_input("Casting Drawing")

        st.markdown("**Material selection**")
        material_type = st.selectbox("Material Type", [""] + material_types)
        prefix_options = materials_df[materials_df["Material Type"] == material_type]["Prefix"].dropna().unique().tolist()
        prefix = st.selectbox("Prefix", [""] + prefix_options)
        name_options = materials_df[
            (materials_df["Material Type"] == material_type) & (materials_df["Prefix"] == prefix)
        ]["Name"].dropna().unique().tolist()
        name = st.selectbox("Name", [""] + name_options)
        material_note = st.text_input("Material Note")

        hf_service_casting = False
        if selected_part != "Bearing housing casting":
            hf_service_casting = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?")

        generate_output = st.button("Genera Output")

    if generate_output:
        with col_output:
            st.markdown("### 📤 Output")

            casting_code = "XX"
            fpd_material_code = "NA"
            if material_type and prefix and name:
                casting_code_lookup = materials_df[
                    (materials_df["Material Type"] == material_type) &
                    (materials_df["Prefix"] == prefix) &
                    (materials_df["Name"] == name)
                ]
                if not casting_code_lookup.empty:
                    raw_code = str(casting_code_lookup["Casting code"].values[0])
                    casting_code = raw_code[-2:] if len(raw_code) >= 2 else raw_code
                    fpd_material_code = casting_code_lookup["FPD Code"].values[0]

            item_number = "7" + casting_code if casting_code != "XX" else "7XX"
            pattern_parts = [mod for mod in [mod1, mod2, mod3, mod4, mod5] if mod.strip()]
            pattern_full = "/".join(pattern_parts)

            # SQ95 trigger
            trigger_materials = [
                ("ASTM", "A351_", "CG8M"),
                ("ASTM", "A351_", "CG3M"),
                ("ASTM", "A351_", "CG8M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY"),
                ("ASTM", "A351_", "CG3M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY + PTA STELLITE 6 OVERLAY"),
                ("ASTM", "A743_", "CG3M"),
                ("ASTM", "A743_", "CG8M"),
                ("ASTM", "A743_", "CG3M + PTA STELLITE 12 OVERLAY"),
                ("ASTM", "A743_", "CG3M + PTA STELLITE 6 OVERLAY"),
                ("ASTM", "A743_", "CG3M + DLD WC-Ni 60-40"),
                ("ASTM", "A744_", "CG3M"),
            ]
            apply_sq95 = (material_type, prefix, name) in trigger_materials

            # Description
            description_parts = [f"*{identificativo.upper()}", "[SQ58]"]
            if base_pattern:
                description_parts.append(f"BASE PATTERN: {base_pattern}")
            if pattern_full:
                description_parts.append(f"MODS: {pattern_full}")
            if note:
                description_parts.append(note)
            description_parts.append(f"{prefix} {name}".strip())
            if material_note:
                description_parts.append(material_note)
            description_parts.append("[DE2390.002]")
            if apply_sq95:
                description_parts.append("[SQ95]")
            if hf_service_casting:
                description_parts.append("<SQ113>")
            if selected_part == "Impeller casting":
                description_parts.append("[DE2920.025]")

            description = ", ".join(description_parts)

            # Quality
            quality_lines = [
                "DE 2390.002 - Procurement and Quality Specification for Ferrous Castings",
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche"
            ]
            if apply_sq95:
                quality_lines.append("SQ 95 - Ciclo di Lavorazione CG3M e CG8M (fuso AISI 317L e AISI 317)")
            if hf_service_casting:
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if selected_part == "Impeller casting":
                quality_lines.append("DE2920.025 - Impellers' Allowable Tip Speed and Related N.D.E. (Non Destructive Examination)")

            quality_field = "\n".join(quality_lines)

            # Mostra Output
            st.text_input("Item", value=item_number)
            st.text_area("Description", value=description, height=100)
            st.text_input("Identificativo", value=identificativo)
            st.text_input("Classe ricambi", value="")
            st.text_input("Categories", value="FASCIA ITE 7")
            st.text_input("Catalog", value="FUSIONI")
            st.text_input("Disegno", value=casting_drawing)
            st.text_input("Material", value=f"{prefix} {name}")
            st.text_input("FPD Material Code", value=fpd_material_code)
            st.text_input("Template", value="FPD_BUY_CASTING")
            st.text_input("ERP L1", value="10_CASTING")
            st.text_input("ERP L2", value="")
            st.text_input("To Supplier", value="")
            st.text_area("Quality", value=quality_field, height=100)

        with col_dataload:
            st.markdown("### ⚙️ Dataload")
            st.write("Coming soon...")

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

