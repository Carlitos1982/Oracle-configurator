import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

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

elif selected_part == "Casing, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Pump Type", size_df["Pump Model"].dropna().unique())
        size = st.selectbox(
            "Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique()
        )

        drawing = st.text_input("DWG/Doc")
        note = st.text_area("Note")
        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="cas_mat_type")

        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="cas_mat_prefix"
        )

        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="cas_mat_name"
        )
        mat_note = st.text_input("Material Note")

        overlay = st.multiselect(
            "Overlay/Trattamenti",
            ["DLD", "PTAW", "Laser Hardening", "METCO", "Ceramic Chrome"],
            key="cas_overlay"
        )
        hvof = st.checkbox("HVOF Coating", key="cas_hvof")
        water = st.checkbox("Water Service", key="cas_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="cas_stami")

        if st.button("Genera Output"):
            item = "40101..."
            ident = "1100-CASING"
            desc_label = "CASING, PUMP"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ARTVARI"

            drawing_out = drawing
            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # Logica FPD Material Code aggiornata
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            template = "FPD_MAKE"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "10_CASING"

            # Costruzione descrizione
            descr_parts = [f"*{desc_label}", f"{model}-{size}"]
            if note:
                descr_parts.append(note)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr_parts.append("[SQ58]")
            descr_parts.append("[CORP-ENG-0115]")
            if overlay:
                descr_parts.append("[PQ72]")
            if hvof:
                descr_parts.append("[DE2500.002]")
            if water:
                descr_parts.append("[PI23]")
            if stamicarbon:
                descr_parts.append("[SQ172]")
            descr = " ".join(descr_parts)

            # Campo Quality
            quality = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]
            if overlay:
                quality.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + Components with METCO or Ceramic Chrome (cr2o3) overlay")
            if hvof:
                quality.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                quality.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                quality.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="cas_out1")
            st.text_area("Description", value=data["Description"], height=120, key="cas_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="cas_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="cas_out4")
            st.text_input("Categories", value=data["Categories"], key="cas_out5")
            st.text_input("Catalog", value=data["Catalog"], key="cas_out6")
            st.text_input("Disegno", value=data["Disegno"], key="cas_out7")
            st.text_input("Material", value=data["Material"], key="cas_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="cas_out9")
            st.text_input("Template", value=data["Template"], key="cas_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="cas_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="cas_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="cas_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="cas_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="cas_op")
        item_code_input = st.text_input("Codice item", key="cas_item_code")

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


elif selected_part == "Ring, Wear":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        ring_type = st.selectbox("Type", ["Stationary", "Rotary"], key="wear_type")
        model = st.selectbox("Pump Type", size_df["Pump Model"].dropna().unique(), key="wear_model")
        size = st.selectbox(
            "Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique(),
            key="wear_size"
        )
        dia_int = st.number_input("Internal Diameter (mm)", min_value=0, key="wear_dia_int")
        dia_out = st.number_input("Outer Diameter (mm)", min_value=0, key="wear_dia_out")

        clearance = st.radio("Increased clearance?", ["No", "Yes"], horizontal=True, key="wear_clear")
        drawing = st.text_input("DWG/Doc", key="wear_drawing")
        note = st.text_area("Note", key="wear_note")

        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="wear_mat_type")
        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="wear_mat_prefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="wear_mat_name"
        )
        mat_note = st.text_input("Material Note", key="wear_mat_note")

        if st.button("Genera Output"):
            # Item e identificativo
            item = "40223..." if ring_type == "Stationary" else "40224..."
            ident = "1500-CASING WEAR RING" if ring_type == "Stationary" else "2300-IMPELLER WEAR RING"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ALBERO"
            template = "FPD_BUY_1"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "24_RINGS"

            # Materiale e FPD code
            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    possible = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(possible) == 1:
                        fpd_code = possible[0]

            # Descrizione
            descr_parts = [
                f"*{ident}",
                f"{model}-{size}",
                f"{dia_int}/{dia_out} mm"
            ]
            if clearance == "Yes":
                descr_parts.append("[PI23]")
            if note:
                descr_parts.append(note)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr = " ".join(descr_parts)

            # Qualità
            quality = ["SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche"]
            if clearance == "Yes":
                quality.insert(0, "PI 23 - Pompe per Acqua Potabile")
            quality.append("CORP-ENG-0115 - General Surface Quality Requirements G1-1")

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": drawing,
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="wear_out1")
            st.text_area("Description", value=data["Description"], height=120, key="wear_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="wear_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="wear_out4")
            st.text_input("Categories", value=data["Categories"], key="wear_out5")
            st.text_input("Catalog", value=data["Catalog"], key="wear_out6")
            st.text_input("Disegno", value=data["Disegno"], key="wear_out7")
            st.text_input("Material", value=data["Material"], key="wear_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="wear_out9")
            st.text_input("Template", value=data["Template"], key="wear_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="wear_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="wear_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="wear_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="wear_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="wear_op")
        item_code_input = st.text_input("Codice item", key="wear_item_code")

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

elif selected_part == "Casing cover, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Pump Type", size_df["Pump Model"].dropna().unique())
        size = st.selectbox(
            "Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique()
        )

        drawing = st.text_input("DWG/Doc")
        note = st.text_area("Note")
        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="cc_mat_type")

        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox(
            "Material Prefix",
            [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()),
            key="cc_mat_prefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name",
            [""] + sorted(name_options["Name"].dropna().unique().tolist()),
            key="cc_mat_name"
        )
        mat_note = st.text_input("Material Note")

        if st.button("Genera Output"):
            item = "40210..."
            ident = "1100-CASING COVER"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ALBERO"
            template = "FPD_MAKE"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "10_CASING_COVER"

            drawing_out = drawing
            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # FPD material code logic
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            # Descrizione
            descr_parts = [f"*CASING COVER, PUMP", f"{model}-{size}"]
            if note:
                descr_parts.append(note)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr_parts += ["[SQ58]", "[CORP-ENG-0115]"]
            descr = " ".join(descr_parts)

            quality = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="cc_out1")
            st.text_area("Description", value=data["Description"], height=120, key="cc_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="cc_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="cc_out4")
            st.text_input("Categories", value=data["Categories"], key="cc_out5")
            st.text_input("Catalog", value=data["Catalog"], key="cc_out6")
            st.text_input("Disegno", value=data["Disegno"], key="cc_out7")
            st.text_input("Material", value=data["Material"], key="cc_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="cc_out9")
            st.text_input("Template", value=data["Template"], key="cc_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="cc_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="cc_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="cc_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="cc_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="cc_op")
        item_code_input = st.text_input("Codice item", key="cc_item_code")

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

elif selected_part == "Impeller, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Pump Model", size_df["Pump Model"].dropna().unique(), key="imp_model")
        size = st.selectbox(
            "Pump Size",
            size_df[size_df["Pump Model"] == model]["Size"].dropna().unique(),
            key="imp_size"
        )

        note = st.text_area("Note")
        drawing = st.text_input("DWG/Doc")
        
        mtype = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="imp_mtype")

        prefix_options = materials_df[materials_df["Material Type"] == mtype]
        mprefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="imp_mprefix"
        )

        name_options = materials_df[
            (materials_df["Material Type"] == mtype) &
            (materials_df["Prefix"] == mprefix)
        ]
        mname = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="imp_mname"
        )

        mnote = st.text_input("Material Note")

        if st.button("Genera Output"):
            item = "40211…"
            ident = "2200-IMPELLER"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ARTVARI"
            template = "FPD_MAKE"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "22_IMPELLER"

            material = " ".join(x for x in [mtype, mprefix, mname] if x)
            drawing_out = drawing

            # FPD material code logica
            fpd_code = ""
            if mprefix:
                if mname:
                    fpd_code = get_fpd_code(mtype, mprefix, mname)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mtype) &
                        (materials_df["Prefix"] == mprefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            # Qualità
            quality = ["CORP-ENG-0115 - General Surface Quality Requirements G1-1", "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche"]
            descr_parts = [
                "*IMPELLER, PUMP",
                f"{model}-{size}",
                note if note else "",
                material,
                mnote if mnote else "",
                "[CORP-ENG-0115]",
                "[SQ58]"
            ]
            descr = " ".join(p for p in descr_parts if p)

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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="imp_out1")
            st.text_area("Description", value=data["Description"], height=120, key="imp_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="imp_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="imp_out4")
            st.text_input("Categories", value=data["Categories"], key="imp_out5")
            st.text_input("Catalog", value=data["Catalog"], key="imp_out6")
            st.text_input("Disegno", value=data["Disegno"], key="imp_out7")
            st.text_input("Material", value=data["Material"], key="imp_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="imp_out9")
            st.text_input("Template", value=data["Template"], key="imp_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="imp_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="imp_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="imp_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="imp_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="imp_op")
        item_code_input = st.text_input("Codice item", key="imp_item_code")

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
elif selected_part == "Balance Bushing, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Pump Type", size_df["Pump Model"].dropna().unique(), key="bb_model")
        size = st.selectbox(
            "Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique(), key="bb_size"
        )

        drawing = st.text_input("DWG/Doc", key="bb_drawing")
        note = st.text_area("Note", key="bb_note")

        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="bb_mat_type")
        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="bb_mat_prefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="bb_mat_name"
        )
        mat_note = st.text_input("Material Note", key="bb_mat_note")

        if st.button("Genera Output", key="bb_generate"):
            item = "6231..."
            ident = "6231-BALANCE DRUM BUSH"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ALBERO"
            template = "FPD_BUY_1"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "16_BUSHING"
            drawing_out = drawing

            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [
                "*BALANCE BUSHING, PUMP",
                f"{model}-{size}"
            ]
            if note:
                descr_parts.append(note)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr_parts.append("[SQ58]")
            descr = " ".join(descr_parts)

            quality = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="bb_out1")
            st.text_area("Description", value=data["Description"], height=120, key="bb_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="bb_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="bb_out4")
            st.text_input("Categories", value=data["Categories"], key="bb_out5")
            st.text_input("Catalog", value=data["Catalog"], key="bb_out6")
            st.text_input("Disegno", value=data["Disegno"], key="bb_out7")
            st.text_input("Material", value=data["Material"], key="bb_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="bb_out9")
            st.text_input("Template", value=data["Template"], key="bb_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="bb_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="bb_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="bb_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="bb_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bb_op")
        item_code_input = st.text_input("Codice item", key="bb_item_code")

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
elif selected_part == "Balance Drum, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Product pump model", size_df["Pump Model"].dropna().unique(), key="bd_model")
        size = st.selectbox("Product pump size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique(), key="bd_size")

        add_feat1 = st.text_input("Additional features 1", key="bd_feat1")
        add_feat2 = st.text_input("Additional features 2", key="bd_feat2")

        brg_type = st.text_input("Brg. type", key="bd_brg_type")
        brg_size = st.text_input("Brg. size", key="bd_brg_size")
        max_diam = st.number_input("Max diameter (mm)", min_value=0, key="bd_max_diam")
        max_len = st.number_input("Max length (mm)", min_value=0, key="bd_max_len")

        drawing = st.text_input("DWG/doc", key="bd_dwg")
        note = st.text_area("Note", key="bd_note")

        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="bd_mat_type")
        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox("Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="bd_mat_prefix")
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox("Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="bd_mat_name")
        mat_note = st.text_input("Material Note", key="bd_mat_note")

        if st.button("Genera Output", key="bd_generate"):
            item = "6231..."
            ident = "BALANCE DRUM"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ALBERO"
            template = "FPD_BUY_1"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "16_BUSHING"
            drawing_out = drawing

            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # Logica FPD code
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [
                "*BALANCE DRUM",
                f"{model}-{size}",
                add_feat1,
                add_feat2,
                f"Brg.Type: {brg_type}" if brg_type else "",
                f"Brg.Size: {brg_size}" if brg_size else "",
                f"Ø{max_diam} x {max_len} mm" if max_diam and max_len else "",
                note,
                material,
                mat_note,
                "[SQ58]",
                "[CORP-ENG-0115]"
            ]
            descr = " ".join(part for part in descr_parts if part)

            quality = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="bd_out1")
            st.text_area("Description", value=data["Description"], height=120, key="bd_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="bd_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="bd_out4")
            st.text_input("Categories", value=data["Categories"], key="bd_out5")
            st.text_input("Catalog", value=data["Catalog"], key="bd_out6")
            st.text_input("Disegno", value=data["Disegno"], key="bd_out7")
            st.text_input("Material", value=data["Material"], key="bd_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="bd_out9")
            st.text_input("Template", value=data["Template"], key="bd_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="bd_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="bd_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="bd_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="bd_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bd_op")
        item_code_input = st.text_input("Codice item", key="bd_item_code")

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
elif selected_part == "Balance Disc, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Product pump model", size_df["Pump Model"].dropna().unique(), key="bdisc_model")
        size = st.selectbox("Product pump size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique(), key="bdisc_size")

        add_feat1 = st.text_input("Additional features 1", key="bdisc_feat1")
        add_feat2 = st.text_input("Additional features 2", key="bdisc_feat2")

        brg_type = st.text_input("Brg. type", key="bdisc_brg_type")
        brg_size = st.text_input("Brg. size", key="bdisc_brg_size")
        max_diam = st.number_input("Max diameter (mm)", min_value=0, key="bdisc_max_diam")
        max_len = st.number_input("Max length (mm)", min_value=0, key="bdisc_max_len")

        drawing = st.text_input("DWG/doc", key="bdisc_dwg")
        note = st.text_area("Note", key="bdisc_note")

        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="bdisc_mat_type")
        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox("Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="bdisc_mat_prefix")
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox("Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="bdisc_mat_name")
        mat_note = st.text_input("Material Note", key="bdisc_mat_note")

        if st.button("Genera Output", key="bdisc_generate"):
            item = "6210..."
            ident = "BALANCE DISC"
            classe = "1-2-3"
            cat = "FASCIA ITE 4"
            catalog = "ARTVARI"
            template = "FPD_BUY_1"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "30_DISK"
            drawing_out = drawing

            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # Logica FPD code
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [
                "*BALANCE DISC",
                f"{model}-{size}",
                add_feat1,
                add_feat2,
                f"Brg.Type: {brg_type}" if brg_type else "",
                f"Brg.Size: {brg_size}" if brg_size else "",
                f"Ø{max_diam} x {max_len} mm" if max_diam and max_len else "",
                note,
                material,
                mat_note,
                "[SQ58]",
                "[CORP-ENG-0115]"
            ]
            descr = " ".join(part for part in descr_parts if part)

            quality = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="bdisc_out1")
            st.text_area("Description", value=data["Description"], height=120, key="bdisc_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="bdisc_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="bdisc_out4")
            st.text_input("Categories", value=data["Categories"], key="bdisc_out5")
            st.text_input("Catalog", value=data["Catalog"], key="bdisc_out6")
            st.text_input("Disegno", value=data["Disegno"], key="bdisc_out7")
            st.text_input("Material", value=data["Material"], key="bdisc_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="bdisc_out9")
            st.text_input("Template", value=data["Template"], key="bdisc_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="bdisc_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="bdisc_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="bdisc_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="bdisc_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="bdisc_op")
        item_code_input = st.text_input("Codice item", key="bdisc_item_code")

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
elif selected_part == "Bolt, Hexagonal":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        size_hex   = st.selectbox("Size", bolt_sizes, key="hex_size")
        length_hex = st.selectbox("Length", bolt_lengths, key="hex_length")
        full_thd   = st.radio("Full threaded?", ["Yes", "No"], horizontal=True, key="hex_fullthread")
        zinc       = st.radio("Zinc Plated?", ["Yes", "No"], horizontal=True, key="hex_zinc")
        note1_hex  = st.text_area("Note (opzionale)", height=80, key="hex_note1")

        # Materiali
        mtype_hex = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="hex_mtype")
        prefix_options = materials_df[materials_df["Material Type"] == mtype_hex]
        mprefix_hex = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()),
            key="hex_mprefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mtype_hex) &
            (materials_df["Prefix"] == mprefix_hex)
        ]
        mname_hex = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique()),
            key="hex_mname"
        )
        mnote_hex = st.text_input("Material Note", key="hex_mnote")

        if st.button("Genera Output", key="hex_button"):
            item = "56020..."
            ident = "6562-HEXAGONAL BOLT"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_1"
            erp1 = "60_FASTENER"
            erp2 = "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"

            material = " ".join(x for x in [mtype_hex, mprefix_hex, mname_hex] if x)

            # Logica FPD Code
            fpd_code = ""
            if mprefix_hex:
                if mname_hex:
                    fpd_code = get_fpd_code(mtype_hex, mprefix_hex, mname_hex)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mtype_hex) &
                        (materials_df["Prefix"] == mprefix_hex)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [f"*BOLT HEX {size_hex}x{length_hex}"]
            if full_thd == "Yes":
                descr_parts.append("FULL THD")
            if zinc == "Yes":
                descr_parts.append("ZINC PLATED")
            if note1_hex:
                descr_parts.append(note1_hex)
            if material:
                descr_parts.append(material)
            if mnote_hex:
                descr_parts.append(mnote_hex)
            descr = " ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": "",
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": []
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="hex_out1")
            st.text_area("Description", value=data["Description"], height=120, key="hex_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="hex_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="hex_out4")
            st.text_input("Categories", value=data["Categories"], key="hex_out5")
            st.text_input("Catalog", value=data["Catalog"], key="hex_out6")
            st.text_input("Disegno", value=data["Disegno"], key="hex_out7")
            st.text_input("Material", value=data["Material"], key="hex_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="hex_out9")
            st.text_input("Template", value=data["Template"], key="hex_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="hex_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="hex_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="hex_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="hex_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="hex_op")
        item_code_input = st.text_input("Codice item", key="hex_item_code")

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

elif selected_part == "Stud, Threaded":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        thread_type = st.selectbox("Threaded", ["Partial", "Full"], key="stud_threaded")
        stud_size = st.selectbox("Size", nut_sizes, key="stud_size")
        stud_length = st.selectbox("Length", bolt_lengths, key="stud_length")
        note_stud = st.text_area("Note", height=80, key="stud_note")

        dwg_stud = st.text_input("DWG/Doc", key="stud_dwg")

        # Materiali
        mtype_stud = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="stud_mtype")
        prefix_options = materials_df[materials_df["Material Type"] == mtype_stud]
        mprefix_stud = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()),
            key="stud_mprefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mtype_stud) &
            (materials_df["Prefix"] == mprefix_stud)
        ]
        mname_stud = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique()),
            key="stud_mname"
        )
        mnote_stud = st.text_input("Material Note", key="stud_mnote")

        if st.button("Genera Output", key="stud_button"):
            item = "56146..."
            ident = "6572-STUD"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_2"
            erp1 = "60_FASTENER"
            erp2 = "12_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"

            material = " ".join(x for x in [mtype_stud, mprefix_stud, mname_stud] if x)

            # FPD Material Code
            fpd_code = ""
            if mprefix_stud:
                if mname_stud:
                    fpd_code = get_fpd_code(mtype_stud, mprefix_stud, mname_stud)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mtype_stud) &
                        (materials_df["Prefix"] == mprefix_stud)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [f"*STUD {thread_type} {stud_size}x{stud_length}"]
            if note_stud:
                descr_parts.append(note_stud)
            if material:
                descr_parts.append(material)
            if mnote_stud:
                descr_parts.append(mnote_stud)
            descr = " ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": dwg_stud,
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": []
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="stud_out1")
            st.text_area("Description", value=data["Description"], height=120, key="stud_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="stud_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="stud_out4")
            st.text_input("Categories", value=data["Categories"], key="stud_out5")
            st.text_input("Catalog", value=data["Catalog"], key="stud_out6")
            st.text_input("Disegno", value=data["Disegno"], key="stud_out7")
            st.text_input("Material", value=data["Material"], key="stud_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="stud_out9")
            st.text_input("Template", value=data["Template"], key="stud_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="stud_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="stud_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="stud_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="stud_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="stud_op")
        item_code_input = st.text_input("Codice item", key="stud_item_code")

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


elif selected_part == "Nut, Hex":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        nut_type = "Heavy"
        nut_size = st.selectbox("Size", nut_sizes, key="nut_size")
        note1_nut = st.text_area("Note", height=80, key="nut_note1")

        # Materiali
        mtype_nut = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="nut_mtype")
        prefix_options = materials_df[materials_df["Material Type"] == mtype_nut]
        mprefix_nut = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()),
            key="nut_mprefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mtype_nut) &
            (materials_df["Prefix"] == mprefix_nut)
        ]
        mname_nut = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique()),
            key="nut_mname"
        )
        mnote_nut = st.text_input("Material Note", key="nut_mnote")

        if st.button("Genera Output", key="nut_button"):
            item = "56030..."
            ident = "6581-HEXAGON NUT"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_2"
            erp1 = "60_FASTENER"
            erp2 = "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"

            material = " ".join(x for x in [mtype_nut, mprefix_nut, mname_nut] if x)

            # Logica FPD Code
            fpd_code = ""
            if mprefix_nut:
                if mname_nut:
                    fpd_code = get_fpd_code(mtype_nut, mprefix_nut, mname_nut)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mtype_nut) &
                        (materials_df["Prefix"] == mprefix_nut)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [f"*NUT HEX {nut_type} {nut_size}"]
            if note1_nut:
                descr_parts.append(note1_nut)
            if material:
                descr_parts.append(material)
            if mnote_nut:
                descr_parts.append(mnote_nut)
            descr = " ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": "",
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": []
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="nut_out1")
            st.text_area("Description", value=data["Description"], height=120, key="nut_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="nut_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="nut_out4")
            st.text_input("Categories", value=data["Categories"], key="nut_out5")
            st.text_input("Catalog", value=data["Catalog"], key="nut_out6")
            st.text_input("Disegno", value=data["Disegno"], key="nut_out7")
            st.text_input("Material", value=data["Material"], key="nut_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="nut_out9")
            st.text_input("Template", value=data["Template"], key="nut_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="nut_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="nut_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="nut_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="nut_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="nut_op")
        item_code_input = st.text_input("Codice item", key="nut_item_code")

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
elif selected_part == "Stud, Threaded":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        thread_type = st.selectbox("Threaded", ["Partial", "Full"], key="stud_threaded")
        stud_size = st.selectbox("Size", nut_sizes, key="stud_size")
        stud_length = st.selectbox("Length", bolt_lengths, key="stud_length")
        note_stud = st.text_area("Note", height=80, key="stud_note")

        dwg_stud = st.text_input("DWG/Doc", key="stud_dwg")

        # Materiali
        mtype_stud = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="stud_mtype")
        prefix_options = materials_df[materials_df["Material Type"] == mtype_stud]
        mprefix_stud = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()),
            key="stud_mprefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mtype_stud) &
            (materials_df["Prefix"] == mprefix_stud)
        ]
        mname_stud = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique()),
            key="stud_mname"
        )
        mnote_stud = st.text_input("Material Note", key="stud_mnote")

        if st.button("Genera Output", key="stud_button"):
            item = "56146..."
            ident = "6572-STUD"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_2"
            erp1 = "60_FASTENER"
            erp2 = "12_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"

            material = " ".join(x for x in [mtype_stud, mprefix_stud, mname_stud] if x)

            # FPD Material Code
            fpd_code = ""
            if mprefix_stud:
                if mname_stud:
                    fpd_code = get_fpd_code(mtype_stud, mprefix_stud, mname_stud)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mtype_stud) &
                        (materials_df["Prefix"] == mprefix_stud)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [f"*STUD {thread_type} {stud_size}x{stud_length}"]
            if note_stud:
                descr_parts.append(note_stud)
            if material:
                descr_parts.append(material)
            if mnote_stud:
                descr_parts.append(mnote_stud)
            descr = " ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": dwg_stud,
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": []
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="stud_out1")
            st.text_area("Description", value=data["Description"], height=120, key="stud_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="stud_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="stud_out4")
            st.text_input("Categories", value=data["Categories"], key="stud_out5")
            st.text_input("Catalog", value=data["Catalog"], key="stud_out6")
            st.text_input("Disegno", value=data["Disegno"], key="stud_out7")
            st.text_input("Material", value=data["Material"], key="stud_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="stud_out9")
            st.text_input("Template", value=data["Template"], key="stud_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="stud_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="stud_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="stud_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="stud_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="stud_op")
        item_code_input = st.text_input("Codice item", key="stud_item_code")

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
elif selected_part == "Shaft, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        model = st.selectbox("Product Pump Model", size_df["Pump Model"].dropna().unique())
        size = st.selectbox(
            "Product Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique()
        )

        add1 = st.text_area("Additional features 1")
        add2 = st.text_area("Additional features 2")
        brg_type = st.text_input("Brg. type")
        brg_size = st.text_input("Brg. size")
        diameter = st.number_input("Max diameter (mm)", min_value=0)
        length = st.number_input("Max length (mm)", min_value=0)

        drawing = st.text_input("DWG/Doc")
        note = st.text_area("Note")
        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="sh_mat_type")

        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()),
            key="sh_mat_prefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()),
            key="sh_mat_name"
        )
        mat_note = st.text_input("Material Note")

        if st.button("Genera Output"):
            item = "40231..."
            ident = "2100-SHAFT"
            classe = "2-3"
            cat = "FASCIA ITE 4"
            catalog = "ALBERO"
            template = "FPD_MAKE"
            erp1 = "20_TURNKEY_MACHINING"
            erp2 = "25_SHAFTS"

            drawing_out = drawing
            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # FPD material code logic
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            descr_parts = [
                "*SHAFT, PUMP",
                f"{model}-{size}",
                add1,
                add2,
                brg_type,
                brg_size,
                f"Ø{diameter} x {length} mm"
            ]
            if note:
                descr_parts.append(note)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr_parts += ["[SQ58]", "[CORP-ENG-0115]", "[SQ60]", "[DE3513.014]"]
            descr = " ".join(descr_parts)

            quality = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1",
                "SQ 60 - Procedura di Esecuzione del Run-Out per Alberi e Rotori di Pompe",
                "DE 3513.014 - Shaft Demagnetization"
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
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="sh_out1")
            st.text_area("Description", value=data["Description"], height=120, key="sh_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="sh_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="sh_out4")
            st.text_input("Categories", value=data["Categories"], key="sh_out5")
            st.text_input("Catalog", value=data["Catalog"], key="sh_out6")
            st.text_input("Disegno", value=data["Disegno"], key="sh_out7")
            st.text_input("Material", value=data["Material"], key="sh_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="sh_out9")
            st.text_input("Template", value=data["Template"], key="sh_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="sh_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="sh_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="sh_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="sh_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="sh_op")
        item_code_input = st.text_input("Codice item", key="sh_item_code")

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
        size = st.selectbox(
            "Pump Size", size_df[size_df["Pump Model"] == model]["Size"].dropna().unique()
        )

        length = st.number_input("Length (mm)", min_value=0)
        width = st.number_input("Width (mm)", min_value=0)
        weight = st.number_input("Weight (kg)", min_value=0)

        sourcing = st.selectbox("Sourcing", ["EUROPEAN", "INDIAN", "CHINESE"])

        drawing = st.text_input("DWG/Doc")
        note = st.text_area("Note")
        mat_type = st.selectbox(
            "Material Type", materials_df["Material Type"].dropna().unique(),
            key="base_mat_type"
        )

        prefix_options = materials_df[
            materials_df["Material Type"] == mat_type
        ]
        mat_prefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()),
            key="base_mat_prefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()),
            key="base_mat_name"
        )
        mat_note = st.text_input("Material Note")

        if st.button("Genera Output"):
            # Fissi
            item = "477..."
            ident = "BASE"
            desc_label = "BASEPLATE, PUMP"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"

            drawing_out = drawing
            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # Logica FPD Code
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            template = "FPD_BUY_4"
            erp1 = "21_FABRICATION_OR_BASEPLATES"
            erp2 = "22_BASEPLATE"

            # Build descrizione
            descr_parts = [
                f"*{desc_label}",
                f"{model}-{size}",
                f"({sourcing})",
                f"{length}x{width} mm",
                f"{weight} kg"
            ]
            if note:
                descr_parts.append(note)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr_parts += ["[SQ53]", "[CORP-ENG-0234]"]
            descr = " ".join(descr_parts)

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
                "To Supplier": "",
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
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="base_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="base_out14")
    
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
elif selected_part == "Flange, Pipe":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        pipe_type = st.selectbox("Pipe Type", ["SW", "WN"])
        size = st.selectbox("Size", ["1/8”", "1/4”", "3/8”", "1/2”", "3/4”", "1”", "1 1/4”", "1 1/2”", "2”", "2 1/2”", "3”", "4”"])
        face_type = st.selectbox("Face Type", ["RF", "FF", "RJ"])
        pipe_class = st.text_input("Class (e.g., 150 Sch)")
        additional_features = st.text_input("Additional features (optional)")

        # Material section
        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="flange_mat_type")

        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique().tolist()), key="flange_mat_prefix"
        )

        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) & (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique().tolist()), key="flange_mat_name"
        )

        mat_note = st.text_input("Material Note")

        if st.button("Genera Output"):
            item = "50155..."
            ident = "1245-FLANGE"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = ""
            template = "FPD_BUY_2"
            erp1 = "23_FLANGE"
            erp2 = "13_OTHER"

            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # FPD material code logic
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            # Build description
            descr_parts = [
                "*FLANGE, PIPE",
                f"TYPE: {pipe_type}",
                f"SIZE: {size}",
                f"FACE: {face_type}",
                f"CLASS: {pipe_class}"
            ]
            if additional_features:
                descr_parts.append(f"FEATURES: {additional_features}")
            if material:
                descr_parts.append(f"MATERIAL: {material}")
            if mat_note:
                descr_parts.append(f"NOTE: {mat_note}")
            descr = " ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": "",
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": []
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="flange_out1")
            st.text_area("Description", value=data["Description"], height=120, key="flange_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="flange_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="flange_out4")
            st.text_input("Categories", value=data["Categories"], key="flange_out5")
            st.text_input("Catalog", value=data["Catalog"], key="flange_out6")
            st.text_input("Disegno", value=data["Disegno"], key="flange_out7")
            st.text_input("Material", value=data["Material"], key="flange_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="flange_out9")
            st.text_input("Template", value=data["Template"], key="flange_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="flange_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="flange_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="flange_out13")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="flange_op")
        item_code_input = st.text_input("Codice item", key="flange_item_code")

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

elif selected_part == "Gasket, Flat":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        thickness = st.text_input("Thickness")
        unit = st.selectbox("Unit", ["mm", "inch"], key="gflat_unit")
        drawing = st.text_input("DWG/Doc number")
        
        # Materiali
        mtype = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="gflat_mtype")
        prefix_options = materials_df[materials_df["Material Type"] == mtype]
        mprefix = st.selectbox(
            "Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()),
            key="gflat_mprefix"
        )
        name_options = materials_df[
            (materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)
        ]
        mname = st.selectbox(
            "Material Name", [""] + sorted(name_options["Name"].dropna().unique()),
            key="gflat_mname"
        )
        mnote = st.text_input("Material Note", key="gflat_mnote")

        if st.button("Genera Output", key="gflat_button"):
            item = "50405..."
            ident = "4511-JOINT"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_1"
            erp1 = "55_GASKETS_OR_SEAL"
            erp2 = "15_FLAT"
            drawing_out = drawing

            material = " ".join(x for x in [mtype, mprefix, mname] if x)

            # Logica FPD Code
            fpd_code = ""
            if mprefix:
                if mname:
                    fpd_code = get_fpd_code(mtype, mprefix, mname)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mtype) &
                        (materials_df["Prefix"] == mprefix)
                    ]["FPD Code"].dropna().unique().tolist()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            # Description
            desc_parts = [f"*GASKET, FLAT {thickness} {unit}"]
            if drawing:
                desc_parts.append(f"(DWG: {drawing})")
            if material:
                desc_parts.append(material)
            if mnote:
                desc_parts.append(mnote)
            descr = " ".join(desc_parts)

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
                "To Supplier": "",
                "Quality": []
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="gflat_out1")
            st.text_area("Description", value=data["Description"], height=120, key="gflat_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="gflat_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="gflat_out4")
            st.text_input("Categories", value=data["Categories"], key="gflat_out5")
            st.text_input("Catalog", value=data["Catalog"], key="gflat_out6")
            st.text_input("Disegno", value=data["Disegno"], key="gflat_out7")
            st.text_input("Material", value=data["Material"], key="gflat_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="gflat_out9")
            st.text_input("Template", value=data["Template"], key="gflat_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="gflat_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="gflat_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="gflat_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="gflat_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="gflat_op")
        item_code_input = st.text_input("Codice item", key="gflat_item_code")

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
elif selected_part == "Screw, Cap":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        screw_size = st.selectbox("Size", screw_sizes, key="cap_size")
        screw_length = st.selectbox("Length", screw_lengths, key="cap_length")
        note1 = st.text_area("Note", height=80, key="cap_note1")

        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="cap_mat_type")
        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox("Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()), key="cap_mat_prefix")
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox("Material Name", [""] + sorted(name_options["Name"].dropna().unique()), key="cap_mat_name")
        mat_note = st.text_input("Material Note", key="cap_mat_note")

        if st.button("Genera Output"):
            item = "56102..."
            ident = "6583-CAP SCREW"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_2"
            erp1 = "60_FASTENER"
            erp2 = "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"

            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # Logica FPD Code
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            # Descrizione
            descr_parts = [
                "*CAP SCREW",
                screw_size,
                screw_length
            ]
            if note1:
                descr_parts.append(note1)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr = " ".join(descr_parts)

            quality = []

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": "",
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="cap_out1")
            st.text_area("Description", value=data["Description"], height=120, key="cap_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="cap_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="cap_out4")
            st.text_input("Categories", value=data["Categories"], key="cap_out5")
            st.text_input("Catalog", value=data["Catalog"], key="cap_out6")
            st.text_input("Disegno", value=data["Disegno"], key="cap_out7")
            st.text_input("Material", value=data["Material"], key="cap_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="cap_out9")
            st.text_input("Template", value=data["Template"], key="cap_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="cap_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="cap_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="cap_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="cap_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="cap_op")
        item_code_input = st.text_input("Codice item", key="cap_item_code")

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

elif selected_part == "Screw, Grub":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        grub_size = st.selectbox("Size", screw_sizes, key="grub_size")
        grub_length = st.selectbox("Length", screw_lengths, key="grub_length")
        note1 = st.text_area("Note", height=80, key="grub_note1")

        mat_type = st.selectbox("Material Type", materials_df["Material Type"].dropna().unique(), key="grub_mat_type")
        prefix_options = materials_df[materials_df["Material Type"] == mat_type]
        mat_prefix = st.selectbox("Material Prefix", [""] + sorted(prefix_options["Prefix"].dropna().unique()), key="grub_mat_prefix")
        name_options = materials_df[
            (materials_df["Material Type"] == mat_type) &
            (materials_df["Prefix"] == mat_prefix)
        ]
        mat_name = st.selectbox("Material Name", [""] + sorted(name_options["Name"].dropna().unique()), key="grub_mat_name")
        mat_note = st.text_input("Material Note", key="grub_mat_note")

        if st.button("Genera Output"):
            item = "56103..."
            ident = "6582-GRUB SCREW"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            template = "FPD_BUY_2"
            erp1 = "60_FASTENER"
            erp2 = "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"

            material = " ".join(x for x in [mat_type, mat_prefix, mat_name] if x)

            # Logica FPD Code
            fpd_code = ""
            if mat_prefix:
                if mat_name:
                    fpd_code = get_fpd_code(mat_type, mat_prefix, mat_name)
                else:
                    codes = materials_df[
                        (materials_df["Material Type"] == mat_type) &
                        (materials_df["Prefix"] == mat_prefix)
                    ]["FPD Code"].dropna().unique()
                    if len(codes) == 1:
                        fpd_code = codes[0]

            # Descrizione
            descr_parts = [
                "*GRUB SCREW",
                grub_size,
                grub_length
            ]
            if note1:
                descr_parts.append(note1)
            if material:
                descr_parts.append(material)
            if mat_note:
                descr_parts.append(mat_note)
            descr = " ".join(descr_parts)

            quality = []

            st.session_state["output_data"] = {
                "Item": item,
                "Description": descr,
                "Identificativo": ident,
                "Classe ricambi": classe,
                "Categories": cat,
                "Catalog": catalog,
                "Disegno": "",
                "Material": material,
                "FPD material code": fpd_code,
                "Template": template,
                "ERP L1": erp1,
                "ERP L2": erp2,
                "To Supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            data = st.session_state["output_data"]
            st.text_input("Item", value=data["Item"], key="grub_out1")
            st.text_area("Description", value=data["Description"], height=120, key="grub_out2")
            st.text_input("Identificativo", value=data["Identificativo"], key="grub_out3")
            st.text_input("Classe ricambi", value=data["Classe ricambi"], key="grub_out4")
            st.text_input("Categories", value=data["Categories"], key="grub_out5")
            st.text_input("Catalog", value=data["Catalog"], key="grub_out6")
            st.text_input("Disegno", value=data["Disegno"], key="grub_out7")
            st.text_input("Material", value=data["Material"], key="grub_out8")
            st.text_input("FPD material code", value=data["FPD material code"], key="grub_out9")
            st.text_input("Template", value=data["Template"], key="grub_out10")
            st.text_input("ERP L1", value=data["ERP L1"], key="grub_out11")
            st.text_input("ERP L2", value=data["ERP L2"], key="grub_out12")
            st.text_input("To Supplier", value=data.get("To Supplier", ""), key="grub_out13")
            st.text_area("Quality", value="\n".join(data["Quality"]), height=160, key="grub_out14")

    with col3:
        st.subheader("🧾 DataLoad")
        operation = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="grub_op")
        item_code_input = st.text_input("Codice item", key="grub_item_code")

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
