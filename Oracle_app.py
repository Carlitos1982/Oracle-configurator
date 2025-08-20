from pathlib import Path
import pandas as pd
from PIL import Image
import streamlit as st
from src.utils.dataload import render_dataload_panel
from src.utils.materials import get_fpd_code, select_material
from src.utils.quality import build_quality_tags
from src.utils.data import load_data
from src.parts import casing, impeller
from src.utils.constants import (
    base_series_desc,
    design_desc,
    pairing_desc,
    cage_desc,
    clearance_desc,
    tolerance_desc,
    heat_desc,
    grease_desc,
    vibration_desc,
    dowel_diameters_mm_raw,
    dowel_lengths_mm,
    dowel_diameters_in,
    dowel_lengths_in,
    winding_materials,
    filler_materials,
    color_codes,
)

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
    xls_path = Path(__file__).resolve().with_name("dati_config4.xlsx")
    xls = pd.ExcelFile(xls_path)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(
        subset=["Material Type", "Prefix", "Name"]
    ).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()


# --- Bolt and SKF configuration data loaded from assets
bolts_data = load_data("bolts")
bolt_sizes = bolts_data["sizes"]
bolt_lengths = bolts_data["lengths"]

skf_data = load_data("skf_options")
skf_models = skf_data["models"]
skf_seals = skf_data["seals"]
skf_design = skf_data["design"]
skf_pairing = skf_data["pairing"]
skf_cages = skf_data["cages"]
skf_clearances = skf_data["clearances"]
skf_tolerances = skf_data["tolerances"]
skf_heat = skf_data["heat"]
skf_greases = skf_data["greases"]
skf_vibration = skf_data["vibration"]

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
        "Housing, Bearing",
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
        "Category:",
        [""] + list(categories.keys()),
        index=0
    )
with col2:
    if selected_category:
        part_list = categories[selected_category]
    else:
        part_list = []
    selected_part = st.selectbox(
        "Part:",
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

PART_RENDERERS = {
    "Casing, Pump": casing.render,
    "Impeller, Pump": impeller.render,
}

render_fn = PART_RENDERERS.get(selected_part)
if render_fn:
    render_fn(size_df, features_df, materials_df, material_types)
# --- CASING COVER, PUMP
if selected_part == "Casing Cover, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="ccov_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="ccov_size")

        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="ccov_feat1") if f1_list else ""

        feature_2 = ""


        note = st.text_area("Note", height=80, key="ccov_note")
        dwg = st.text_input("Dwg/doc number", key="ccov_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = select_material(
            materials_df, "ccov"
        )

        make_or_buy = st.radio("Make or Buy?", ["Buy", "Make"], key="ccov_makebuy")
        template = "FPD_BUY_1" if make_or_buy == "Buy" else "FPD_MAKE"

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="ccov_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="ccov_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="ccov_overlay")
        hvof = st.checkbox("HVOF coating?", key="ccov_hvof")
        water = st.checkbox("Water service?", key="ccov_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="ccov_stamicarbon")

        if st.button("Generate Output", key="ccov_gen"):
            tag_string, quality = build_quality_tags(
                {
                    "hf_service": hf_service,
                    "tmt_service": tmt_service,
                    "overlay": overlay,
                    "hvof": hvof,
                    "water": water,
                    "stamicarbon": stamicarbon,
                }
            )

            descr_parts = ["CASING COVER, PUMP"]
            for val in [model, size, feature_1, note]:
                if val:
                    descr_parts.append(val)
            if materiale:
                descr_parts.append(materiale)
            if material_note:
                descr_parts.append(material_note)

            descr = "*" + " - ".join(descr_parts) + " " + tag_string


            st.session_state["output_data"] = {
                "Item": "40205…",
                "Description": descr,
                "Identificativo": "1221-CASING COVER",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "CORPO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": template,
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "17_CASING",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    with col3:
        render_dataload_panel(
            item_code_key="ccov_item_code",
            create_btn_key="gen_dl_ccov",
            update_btn_key="gen_upd_ccov"
        )




# --- BALANCE BUSHING, PUMP
if selected_part == "Balance Bushing, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bbush_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="bbush_size")

        # Menu a tendina Feature 1 (se disponibile)
        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="bbush_feat1") if f1_list else ""

        note = st.text_area("Note", height=80, key="bbush_note")
        dwg = st.text_input("Dwg/doc number", key="bbush_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = select_material(
            materials_df, "bbush"
        )

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bbush_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bbush_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bbush_overlay")
        hvof = st.checkbox("HVOF coating?", key="bbush_hvof")
        water = st.checkbox("Water service?", key="bbush_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bbush_stamicarbon")

        if st.button("Generate Output", key="bbush_gen"):
            tag_string, quality = build_quality_tags(
                {
                    "hf_service": hf_service,
                    "tmt_service": tmt_service,
                    "overlay": overlay,
                    "hvof": hvof,
                    "water": water,
                    "stamicarbon": stamicarbon,
                }
            )

            # Descrizione finale
            descr_parts = ["BALANCE BUSHING, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

            st.session_state["output_data"] = {
                "Item": "40226…",
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
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)


    # COLONNA 3: DataLoad

    with col3:
        render_dataload_panel(
            item_code_key="bbush_item_code",
            create_btn_key="gen_dl_bbush",
            update_btn_key="gen_upd_bbush"
        )




# --- BALANCE DRUM, PUMP
if selected_part == "Balance Drum, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bdrum_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="bdrum_size")

        # Feature 1 come menu a tendina (se presente)
        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="bdrum_feat1") if f1_list else ""

        note = st.text_area("Note", height=80, key="bdrum_note")
        dwg = st.text_input("Dwg/doc number", key="bdrum_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = select_material(
            materials_df, "bdrum"
        )

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bdrum_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bdrum_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bdrum_overlay")
        hvof = st.checkbox("HVOF coating?", key="bdrum_hvof")
        water = st.checkbox("Water service?", key="bdrum_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bdrum_stamicarbon")

        if st.button("Generate Output", key="bdrum_gen"):
            tag_string, quality = build_quality_tags(
                {
                    "hf_service": hf_service,
                    "tmt_service": tmt_service,
                    "overlay": overlay,
                    "hvof": hvof,
                    "water": water,
                    "stamicarbon": stamicarbon,
                }
            )

            # Descrizione finale
            descr_parts = ["BALANCE DRUM, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

            st.session_state["output_data"] = {
                "Item": "40226…",
                "Description": descr,
                "Identificativo": "6230-BALANCE DRUM",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ARTVARI",
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
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    with col3:
        render_dataload_panel(
            item_code_key="bdrum_item_code",
            create_btn_key="gen_dl_bdrum",
            update_btn_key="gen_upd_bdrum"
        )



# --- BALANCE DISC, PUMP
if selected_part == "Balance Disc, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="bdisc_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="bdisc_size")

        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="bdisc_feat1") if f1_list else ""

        note = st.text_area("Note", height=80, key="bdisc_note")
        dwg = st.text_input("Dwg/doc number", key="bdisc_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = select_material(
            materials_df, "bdisc"
        )

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bdisc_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bdisc_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bdisc_overlay")
        hvof = st.checkbox("HVOF coating?", key="bdisc_hvof")
        water = st.checkbox("Water service?", key="bdisc_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bdisc_stamicarbon")

        if st.button("Generate Output", key="bdisc_gen"):
            tag_string, quality = build_quality_tags(
                {
                    "hf_service": hf_service,
                    "tmt_service": tmt_service,
                    "overlay": overlay,
                    "hvof": hvof,
                    "water": water,
                    "stamicarbon": stamicarbon,
                }
            )

            descr_parts = ["BALANCE DISC, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

            st.session_state["output_data"] = {
                "Item": "40226…",
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
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # COLONNA 3: DataLoad
    with col3:
        render_dataload_panel(
            item_code_key="bdisc_item_code",
            create_btn_key="gen_dl_bdisc",
            update_btn_key="gen_upd_bdisc"
        )


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

        materiale, codice_fpd, _, mtype, mprefix, mname = select_material(
            materials_df, "gate"
        )

        # Checkbox solo per HF e Stamicarbon
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="gate_hf")
        stamicarbon = st.checkbox("Stamicarbon?", key="gate_stamicarbon")

        if st.button("Generate Output", key="gate_gen"):
            tag_string, quality = build_quality_tags(
                {
                    "hf_service": hf_service,
                    "stamicarbon": stamicarbon,
                    "include_standard": False,
                }
            )

            descr = f"GATE VALVE - MODEL: {model}, SIZE: {size}, RATING: {rating}"
            if note:
                descr += f", NOTE: {note}"
            descr += f" {tag_string}" if tag_string else ""
            descr = "*" + descr

            st.session_state["output_data"] = {
                "Item": "50186…",
                "Description": descr,
                "Identificativo": "VALVOLA (GLOBO,SARAC,SFERA,NEEDLE,MANIF,CONTR)",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "72_VALVE",
                "ERP_L2": "18_GATE_VALVE",
                "To supplier": "",
                "Quality": quality
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # COLONNA 3: DataLoad
    with col3:
        render_dataload_panel(
            item_code_key="gate_item_code",
            create_btn_key="gen_dl_gate",
            update_btn_key="gen_upd_gate"
        )

if selected_part == "Gasket, Spiral Wound":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
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
            "STANDARD PRESSURE - m=3; y=10000psi (1 stripe)":    ("STANDARD PRESSURE", "m=3; y=10000psi", "1 stripe"),
            "HIGH PRESSURE - m=3; y=17500psi (2 stripes)":       ("HIGH PRESSURE",   "m=3; y=17500psi",   "2 stripes"),
            "ULTRA HIGH PRESSURE - m=3; y=23500psi (3 stripes)": ("ULTRA HIGH PRESSURE", "m=3; y=23500psi", "3 stripes")
        }

        winding_gsw    = st.selectbox("Winding Material", list(winding_options), key="gsw_winding")
        filler_gsw     = st.selectbox("Filler",            list(filler_options),  key="gsw_filler")
        out_dia_gsw    = st.text_input("Outer Diameter (MM)", key="gsw_out_dia")
        in_dia_gsw     = st.text_input("Inner Diameter (MM)", key="gsw_in_dia")
        thickness_gsw  = st.text_input("Thickness (MM)",      key="gsw_thick")
        rating_gsw     = st.selectbox("Rating", list(rating_mapping), key="gsw_rating")
        dwg_gsw        = st.text_input("Dwg/doc number",       key="gsw_dwg")
        note_gsw       = st.text_area("Note", height=80,       key="gsw_note")
        hf_service_gsw = st.checkbox(
            "Is it a hydrofluoric acid (HF) alkylation service?",
            key="gsw_hf"
        )
        water_gsw = st.checkbox("Water service?", key="gsw_water")
        stamicarbon_gsw = st.checkbox("Stamicarbon?", key="gsw_stamicarbon")

        if st.button("Generate Output", key="gsw_gen"):
            color1, ral1      = winding_options[winding_gsw]
            color2, ral2      = filler_options[filler_gsw]
            pressure_label, rating_descr, stripe = rating_mapping[rating_gsw]

            # costruisco la descrizione
            descr_gsw = (
                f"*GASKET, SPIRAL WOUND - WINDING: {winding_gsw}, "
                f"FILLER: {filler_gsw}, "
                f"OD: {out_dia_gsw} MM, ID: {in_dia_gsw} MM, THK: {thickness_gsw} MM, "
                f"RATING: {pressure_label} – {rating_descr}, "
                f"COLOR CODE: {color1} {ral1} / {color2} {ral2} ({stripe})"
            )
            if note_gsw:
                descr_gsw += f", {note_gsw}"

            extras = [
                (
                    "[SQ174]",
                    "SQ 174 - Casing/Cover pump spiral wound gaskets: Specification for Mechanical properties, applicable materials and dimensions",
                )
            ]
            tag_string, quality_field = build_quality_tags(
                {
                    "hf_service": hf_service_gsw,
                    "water": water_gsw,
                    "stamicarbon": stamicarbon_gsw,
                    "include_standard": False,
                    "extra": extras,
                }
            )
            descr_gsw += f" {tag_string}" if tag_string else ""

            st.session_state["output_data"] = {
                "Item":               "50415…",
                "Description":        descr_gsw,
                "Identificativo":     "4510-JOINT",
                "Classe ricambi":     "1-2-3",
                "Categories":         "FASCIA ITE 5",
                "Catalog":            "ARTVARI",
                "Disegno":            dwg_gsw,
                "Material":           "BUY OUT NOT AVAILABLE",
                "FPD material code":  "BO-NA",
                "Template":           "FPD_BUY_1",
                "ERP_L1":             "55_GASKETS_OR_SEAL",
                "ERP_L2":             "16_SPIRAL_WOUND",
                "To supplier":        "",
                "Quality":            quality_field
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            out = st.session_state["output_data"]
            for campo, valore in out.items():
                if campo in ["Description", "Quality"]:
                    st.text_area(campo, value=valore, height=200, key=f"sw_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"sw_{campo}")

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="gsw_item_code",
            create_btn_key="gen_dl_gsw",
            update_btn_key="gen_upd_gsw"
        )



# --- BEARING, HYDROSTATIC/HYDRODYNAMIC
if selected_part == "Bearing, Hydrostatic/Hydrodynamic":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")

        # Dimensioni
        od_bear    = st.text_input("Outside diameter (OD)", key="bear_od")
        id_bear    = st.text_input("Inside diameter (ID)",  key="bear_id")
        width_bear = st.text_input("Width",                 key="bear_width")

        # ex Additional Features -> Note
        note_bear = st.text_area("Note", height=80, key="bear_note")

        materiale_bear, codice_fpd_bear, material_note_bear, mtype_bear, mprefix_bear, mname_bear = select_material(
            materials_df, "bear"
        )

        dwg_bear = st.text_input("Dwg/doc number", key="bear_dwg")

        if st.button("Generate Output", key="bear_gen"):
            materiale_bear = (
                mname_bear if mtype_bear == "MISCELLANEOUS"
                else f"{mtype_bear} {mprefix_bear} {mname_bear}".strip()
            )

            match_bear = materials_df[
                (materials_df["Material Type"] == mtype_bear) &
                (materials_df["Prefix"] == mprefix_bear) &
                (materials_df["Name"] == mname_bear)
            ]
            codice_fpd_bear = match_bear["FPD Code"].values[0] if not match_bear.empty else ""

            # Blocchetto dimensioni
            dim_bear = " - ".join([
                f"OD {od_bear}" if od_bear else "",
                f"ID {id_bear}" if id_bear else "",
                f"W {width_bear}" if width_bear else ""
            ]).strip(" -")

            # Descrizione SENZA etichetta “Material:”
            descr_parts_bear = [
                "BEARING, HYDROSTATIC/HYDRODYNAMIC",
                dim_bear,
                note_bear,
                materiale_bear,
                material_note_bear
            ]
            descr_bear = "*" + " - ".join([p for p in descr_parts_bear if p])

            st.session_state["output_data"] = {
                "Item": "50122…",
                "Description": descr_bear,
                "Identificativo": "3010-ANTI-FRICTION BEARING",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ALBERO",
                "Disegno": dwg_bear,
                "Material": materiale_bear,
                "FPD material code": codice_fpd_bear,
                "Template": "FPD_BUY_1",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "29_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="bear_item_code",
            create_btn_key="gen_dl_bear",
            update_btn_key="gen_upd_bear"
        )
    
# --- BEARING, ROLLING
if selected_part == "Bearing, Rolling":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")

        # Modello SKF base
        skf_choice = st.selectbox("SKF Model", [""] + skf_models + ["Altro..."], key="br_model")
        custom_model = ""
        if skf_choice == "Altro...":
            custom_model = st.text_input("Inserisci modello SKF", key="br_model_custom")

        # Design / pairing / sigilli ecc.
        design_opt     = st.selectbox("Design / Contact angle", skf_design, key="br_design")
        pairing_opt    = st.selectbox("Pairing / Preload",      skf_pairing, key="br_pairing")
        seal_opt       = st.selectbox("Seals/Shields",          skf_seals, key="br_seal")
        cage_opt       = st.selectbox("Cage type",              skf_cages, key="br_cage")
        clearance_opt  = st.selectbox("Clearance",              skf_clearances, key="br_clear")
        tolerance_opt  = st.selectbox("Tolerance class",        skf_tolerances, key="br_tol")
        heat_opt       = st.selectbox("Heat treatment",         skf_heat, key="br_heat")
        grease_opt     = st.selectbox("Grease / Lubricant",     skf_greases, key="br_grease")
        vibration_opt  = st.selectbox("Vibration spec",         skf_vibration, key="br_vibration")

        extra_suffix = st.text_input("Extra suffix (optional)", key="br_extra")

        # Dimensioni (opzionali)
        od_roll    = st.text_input("Outside diameter (OD)", key="br_od")
        id_roll    = st.text_input("Inside diameter (ID)",  key="br_id")
        width_roll = st.text_input("Width",                 key="br_width")

        note_roll = st.text_area("Note", height=80, key="br_note")

        # --- Funzioni/dizionari già definiti in alto ---
        def bearing_type_from_code(code: str) -> str:
            for p in (code[:3], code[:2], code[:1]):
                if p in base_series_desc:
                    return base_series_desc[p]
            return ""

        def short(sigla: str) -> str:
            return sigla.split(" ")[0] if sigla else ""

        if st.button("Generate Output", key="br_gen"):
            model_final = custom_model if skf_choice == "Altro..." else skf_choice

            # Codici
            code_design    = short(design_opt)
            code_pairing   = short(pairing_opt)
            code_seal      = short(seal_opt)
            code_cage      = short(cage_opt)
            code_clear     = short(clearance_opt)
            code_tol       = short(tolerance_opt)
            code_heat      = short(heat_opt)
            code_grease    = short(grease_opt)
            code_vib       = short(vibration_opt)

            # Sigla finale
            parts_no_space = [
                model_final,
                code_seal,
                code_design,
                code_pairing,
                code_cage,
                code_clear,
                code_tol,
                code_heat,
                code_grease,
                code_vib,
                extra_suffix.strip()
            ]
            skf_full_code = "".join([p for p in parts_no_space if p]).upper()

            # Descrizioni
            bearing_type_txt = bearing_type_from_code(model_final)

            desc_bits = [
                design_desc.get(code_design, ""),
                pairing_desc.get(code_pairing, ""),
                cage_desc.get(code_cage, ""),
                clearance_desc.get(code_clear, ""),
                tolerance_desc.get(code_tol, ""),
                heat_desc.get(code_heat, ""),
                grease_desc.get(code_grease, ""),
                vibration_desc.get(code_vib, "")
            ]
            desc_bits = [d for d in desc_bits if d]

            full_desc_list = []
            if bearing_type_txt:
                full_desc_list.append(bearing_type_txt)
            full_desc_list += desc_bits

            human_suffix = f" ({'; '.join(full_desc_list)})" if full_desc_list else ""

            # Dimensioni
            dim_roll = " - ".join([
                f"OD {od_roll}" if od_roll else "",
                f"ID {id_roll}" if id_roll else "",
                f"W {width_roll}" if width_roll else ""
            ]).strip(" -")

            # Descrizione finale
            descr_parts_roll = [
                "BEARING, ROLLING",
                skf_full_code + human_suffix,
                dim_roll,
                note_roll
            ]
            descr_roll = "*" + " - ".join([p for p in descr_parts_roll if p])

            st.session_state["output_data"] = {
                "Item": "50122…",
                "Description": descr_roll,
                "Identificativo": "3010-ANTI-FRICTION BEARING",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": "COMMERCIAL BEARING",
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "31_COMMERCIAL_BEARING",
                "ERP_L2": "18_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="broll_item_code",
            create_btn_key="gen_dl_broll",
            update_btn_key="gen_upd_broll"
        )



# --- BOLT, EYE
if selected_part == "Bolt, Eye":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")
        size   = st.selectbox("Size",   [""] + bolt_sizes,   key="beye_size")
        length = st.selectbox("Length", [""] + bolt_lengths, key="beye_length")

        note = st.text_area("Note", height=80, key="beye_note")
        materiale, codice_fpd, material_note_beye, mtype_beye, mprefix_beye, mname_beye = select_material(
            materials_df, "beye"
        )
        dwg = st.text_input("Dwg/doc number", key="beye_dwg")

        if st.button("Generate Output", key="beye_gen"):
            descr_parts = ["EYE BOLT"]
            for val in [size, length, note, materiale, material_note_beye]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": "55150…",
                "Description": descr,
                "Identificativo": "6583-EYE BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code",
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
        )

# --- BOLT, HEXAGONAL
if selected_part == "Bolt, Hexagonal":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        size_bh   = st.selectbox("Size",   [""] + bolt_sizes,   key="bh_size")
        length_bh = st.selectbox("Length", [""] + bolt_lengths, key="bh_length")

        full_thread_bh = st.radio("Full threaded?", ["No", "Yes"], index=0, key="bh_full_thread")

        note_bh = st.text_area("Note", height=80, key="bh_note")

        materiale_bh, codice_fpd_bh, material_note_bh, mtype_bh, mprefix_bh, mname_bh = select_material(
            materials_df, "bh"
        )

        zinc_plated_bh = st.radio("Zinc plated?", ["No", "Yes"], index=0, key="bh_zinc")
        stamicarbon_bh = st.checkbox("Stamicarbon?", key="bh_stamicarbon")

        if st.button("Generate Output", key="bh_gen"):
            descr_parts_bh = [
                "HEXAGONAL BOLT",
                size_bh,
                length_bh,
                "FULL THREADED" if full_thread_bh == "Yes" else "",
                note_bh,
                materiale_bh,
                "ZINC PLATED" if zinc_plated_bh == "Yes" else "",
                material_note_bh
            ]
            tag_string, quality = build_quality_tags({
                "stamicarbon": stamicarbon_bh,
                "include_standard": False,
            })
            descr_bh = "*" + " - ".join([p for p in descr_parts_bh if p])
            if tag_string:
                descr_bh += f" {tag_string}"

            st.session_state["output_data"] = {
                "Item": "56230…",
                "Description": descr_bh,
                "Identificativo": "6577-HEXAGON HEAD BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_bh,
                "FPD material code": codice_fpd_bh,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": quality,
            }

   

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="bh_item_code",
            create_btn_key="gen_dl_bh",
            update_btn_key="gen_upd_bh"
        )

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
        stamicarbon_rtj = st.checkbox("Stamicarbon?", key="rtj_stamicarbon")

        if st.button("Generate Output", key="rtj_gen"):
            descr_rtj = (
                f"GASKET, RTJ - STYLE: {style_rtj}, SIZE: {size_rtj}, MATERIAL: {material_rtj}"
            )
            if note_rtj:
                descr_rtj += f", NOTE: {note_rtj}"
            tag_string, quality = build_quality_tags(
                {"hf_service": hf_service_rtj, "stamicarbon": stamicarbon_rtj, "include_standard": False}
            )
            descr_rtj += f" {tag_string}" if tag_string else ""
            descr_rtj = "*" + descr_rtj

            st.session_state["output_data"] = {
                "Item": "50158…",
                "Description": descr_rtj,
                "Identificativo": "4595-JOINT RING",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_rtj,
                "Material": material_rtj,
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_1",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "To supplier": "",
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo in ["Description", "Quality"]:
                    st.text_area(campo, value=valore, height=200, key=f"rtj_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"rtj_{campo}")

    # COLONNA 3 – DATALOAD
    with col3:
        render_dataload_panel(
            item_code_key="rtj_item_code",
            create_btn_key="gen_dl_rtj",
            update_btn_key="gen_upd_rtj"
        )



# --- GUSSET, OTHER
elif selected_part == "Gusset, Other":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        width_gusset     = st.number_input("Width", min_value=0, step=1, format="%d", key="gusset_width")
        thickness_gusset = st.number_input("Thickness", min_value=0, step=1, format="%d", key="gusset_thickness")
        uom_gusset       = st.selectbox("Unità di misura", ["mm", "inches"], key="gusset_uom")
        note1_gusset     = st.text_area("Note", height=80, key="gusset_note1")

        materiale_gusset, codice_fpd_gusset, note2_gusset, mtype_gusset, mprefix_gusset, mname_gusset = select_material(
            materials_df, "gusset"
        )

        if st.button("Generate Output", key="gen_gusset"):

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
                    st.text_area(campo, value=valore, height=200, key=f"gusset_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"gusset_{campo}")

    # COLONNA 3: DataLoad
    with col3:
        render_dataload_panel(
            item_code_key="gusset_item_code",
            create_btn_key="gen_dl_gusset",
            update_btn_key="gen_upd_gusset"
        )

# --- STUD, THREADED
if selected_part == "Stud, Threaded":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")

        size_stud   = st.selectbox("Size",   [""] + bolt_sizes,   key="stud_size")
        length_stud = st.selectbox("Length", [""] + bolt_lengths, key="stud_length")

        # Partial / Full threaded
        thread_type = st.radio("Thread type", ["Partial", "Full"], index=0, key="stud_thread_type")

        note_stud = st.text_area("Note", height=80, key="stud_note")

        materiale_stud, codice_fpd_stud, material_note_stud, mtype_stud, mprefix_stud, mname_stud = select_material(
            materials_df, "stud"
        )

        # Disegno
        dwg_stud = st.text_input("Dwg/doc number", key="stud_dwg")

        stamicarbon_stud = st.checkbox("Stamicarbon?", key="stud_stamicarbon")

        if st.button("Generate Output", key="stud_gen"):
            descr_parts_stud = ["THREADED STUD", size_stud, length_stud, thread_type.upper()+" THREADED" if thread_type else "", note_stud, materiale_stud, material_note_stud]
            tag_string, quality = build_quality_tags({
                "stamicarbon": stamicarbon_stud,
                "include_standard": False,
            })
            descr_stud = "*" + " - ".join([p for p in descr_parts_stud if p])
            if tag_string:
                descr_stud += f" {tag_string}"

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
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": quality,
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="stud_item_code",
            create_btn_key="gen_dl_stud",
            update_btn_key="gen_upd_stud"
        )
# --- NUT, HEX
if selected_part == "Nut, Hex":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")

        nut_type = "Heavy"  # fisso
        size_nut = st.selectbox("Size", [""] + bolt_sizes, key="nut_size")

        note_nut = st.text_area("Note", height=80, key="nut_note")

        materiale_nut, codice_fpd_nut, material_note_nut, mtype_nut, mprefix_nut, mname_nut = select_material(
            materials_df, "nut"
        )

        stamicarbon_nut = st.checkbox("Stamicarbon?", key="nut_stamicarbon")

        if st.button("Generate Output", key="nut_gen"):
            descr_parts_nut = ["HEX NUT", nut_type, size_nut, note_nut, materiale_nut, material_note_nut]
            tag_string, quality = build_quality_tags({
                "stamicarbon": stamicarbon_nut,
                "include_standard": False,
            })
            descr_nut = "*" + " - ".join([p for p in descr_parts_nut if p])
            if tag_string:
                descr_nut += f" {tag_string}"

            st.session_state["output_data"] = {
                "Item": "56030…",
                "Description": descr_nut,
                "Identificativo": "6581-HEXAGON NUT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_nut,
                "Material": materiale_nut,
                "FPD material code": codice_fpd_nut,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": quality,
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="nut_item_code",
            create_btn_key="gen_dl_nut",
            update_btn_key="gen_upd_nut"
        )



# --- RING, WEAR
if selected_part == "Ring, Wear":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        ring_type = st.selectbox("Type", ["Stationary", "Rotary"], key="ring_type")
        model = st.selectbox("Pump Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="ring_model")
        int_diam = st.text_input("Internal diameter (mm)", key="ring_id")
        out_diam = st.text_input("Outer diameter (mm)", key="ring_od")
        note = st.text_area("Note", height=80, key="ring_note")
        clearance = st.radio("Increased clearance?", ["No", "Yes"], horizontal=True, key="ring_clr")
        dwg = st.text_input("Dwg/doc number", key="ring_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = select_material(
            materials_df, "ring"
        )

        hf_service = st.checkbox(
            "Is it an hydrofluoric acid alkylation service (lethal)?", key="ring_hf"
        )
        tmt_service = st.checkbox(
            "TMT/HVOF protection requirements?", key="ring_tmt"
        )
        overlay = st.checkbox(
            "DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="ring_overlay"
        )
        hvof = st.checkbox("HVOF coating?", key="ring_hvof")
        stamicarbon = st.checkbox("Stamicarbon?", key="ring_stamicarbon")

        if st.button("Generate Output", key="ring_gen"):
            extra = []
            if clearance == "Yes":
                extra.append(("<SQ173>", "SQ 173 - Increased Clearance for Wear Ring"))
            tag_string, quality = build_quality_tags({
                "hf_service": hf_service,
                "tmt_service": tmt_service,
                "overlay": overlay,
                "hvof": hvof,
                "stamicarbon": stamicarbon,
                "extra": extra,
            })

            # Descrizione
            descr_parts = [f"{ring_type.upper()} WEAR RING"]
            for val in [model, int_diam, out_diam, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + (f" {tag_string}" if tag_string else "")

            # Output
            item = "40224…" if ring_type == "Rotary" else "40223…"
            identificativo = "2300-IMPELLER WEAR RING" if ring_type == "Rotary" else "1500-CASING WEAR RING"

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

    # COLONNA 2: Output
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # COLONNA 3: DataLoad
    with col3:
        render_dataload_panel(
            item_code_key="ring_item_code",
            create_btn_key="gen_dl_ring",
            update_btn_key="gen_upd_ring"
        )



# --- PIN, DOWEL
if selected_part == "Pin, Dowel":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")

        # Unisco mm + inch nelle tendine (aggiungo " mm" ai metrici)
        diam_list = [""] + [f"{d} mm" for d in dowel_diameters_mm_raw] + dowel_diameters_in
        len_list  = [""] + dowel_lengths_mm + dowel_lengths_in

        diameter_pin = st.selectbox("Diameter", diam_list, key="pin_diam")
        length_pin   = st.selectbox("Length",   len_list,  key="pin_len")

        note_pin = st.text_area("Note", height=80, key="pin_note")

        materiale_pin, codice_fpd_pin, material_note_pin, mtype_pin, mprefix_pin, mname_pin = select_material(
            materials_df, "pin"
        )

        stamicarbon_pin = st.checkbox("Stamicarbon?", key="pin_stamicarbon")

        if st.button("Generate Output", key="pin_gen"):
            dim_block = f"{diameter_pin} - L={length_pin}"

            descr_parts_pin = [
                "DOWEL PIN",
                dim_block,
                note_pin,
                materiale_pin,
                material_note_pin
            ]
            tag_string, quality = build_quality_tags({
                "stamicarbon": stamicarbon_pin,
                "include_standard": False,
            })
            descr_pin = "*" + " - ".join([p for p in descr_parts_pin if p])
            if tag_string:
                descr_pin += f" {tag_string}"

            st.session_state["output_data"] = {
                "Item": "56230…",
                "Description": descr_pin,
                "Identificativo": "6810-DOWEL PIN",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_pin,
                "FPD material code": codice_fpd_pin,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": quality,
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="pin_item_code",
            create_btn_key="gen_dl_pin",
            update_btn_key="gen_upd_pin"
        )

# --- SHAFT, PUMP ---
if selected_part == "Shaft, Pump":
    col1, col2, col3 = st.columns(3)

    # Mappa Brg. Sizes per type
    brg_types = ["W", "W-TK", "EC", "ECR", "ESBR", "EKBR", "ECH", "ESH", "EKH"]
    brg_size_options = {
        "W": ["W040", "W050", "W070", "W090", "W091", "W091-N", "W092", "W092-N", "W105", "W105-N"],
        "W-TK": ["W040-TK", "W050-TK", "W070-TK", "W090-TK", "W091-TK", "W091-N-TK", "W092-TK", "W092-N-TK", "W105-TK", "W105-N-TK"],
        "EC": ["EC0", "EC1", "EC2", "EC34", "EC5", "EC6", "EC7", "EC8", "EC85", "EC9"],
        "ECR": ["ECR0", "ECR1", "ECR2", "ECR34", "ECR5", "ECR6", "ECR7", "ECR8", "ECR85", "ECR9"],
        "ESBR": ["ESBR0", "ESBR1", "ESBR2", "ESBR34", "ESBR5", "ESBR6", "ESBR7", "ESBR8", "ESBR85", "ESBR9"],
        "EKBR": ["EKBR0", "EKBR1", "EKBR2", "EKBR34", "EKBR5", "EKBR6", "EKBR7", "EKBR8", "EKBR85", "EKBR9"],
        "ECH": ["EC0-H", "EC2-H", "EC5-H", "EC6-H", "EC7-H", "EC8-H", "EC85-H", "EC9-H", "EC10-H", "EC11-H", "EC12-H", "EC15-H"],
        "ESH": ["ES0-H", "ES2-H", "ES5-H", "ES6-H", "ES7-H", "ES8-H", "ES85-H", "ES9-H", "ES10-H", "ES11-H", "ES12-H"],
        "EKH": ["EK0-H", "EK2-H", "EK5-H", "EK6-H", "EK7-H", "EK8-H", "EK85-H", "EK9-H", "EK10-H", "EK11-H", "EK12-H"]
    }

    # ─── COLONNA 1: INPUT ───
    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox(
            "Product Type",
            ["", "QL", "QLQ"] + [m for m in sorted(size_df["Pump Model"].dropna().unique()) if m not in ["QL","QLQ"]],
            key="shaft_model"
        )
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="shaft_size")

        brg_type = st.selectbox("Bearing Type", [""] + brg_types, key="shaft_brg_type")
        brg_size = st.selectbox("Bearing Size", [""] + brg_size_options.get(brg_type, []), key="shaft_brg_size")

        max_diam = st.text_input("Max diameter (mm)", key="shaft_diam")
        max_len  = st.text_input("Max length (mm)", key="shaft_len")
        dwg      = st.text_input("Drawing number", key="shaft_dwg")
        note     = st.text_area("Note", height=80, key="shaft_note")

        mtype       = st.selectbox("Material Type", ["", "ASTM"] + [t for t in material_types if t != "ASTM"], key="shaft_mtype")
        prefixes    = sorted(materials_df[materials_df["Material Type"] == mtype]["Prefix"].dropna().unique().tolist())
        mprefix     = st.selectbox(
            "Material Prefix",
            ["", "A322_", "A276_", "A473_"] + [p for p in prefixes if p not in ["A322_","A276_","A473_"]],
            key="shaft_mprefix"
        )
        names       = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
        mname       = st.selectbox("Material Name", [""] + names, key="shaft_mname")
        material_note = st.text_area("Material Note", height=60, key="shaft_matnote")

        # Checkboxes qualità aggiuntive
        overlay     = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="shaft_overlay")
        hvof        = st.checkbox("HVOF coating?", key="shaft_hvof")
        water       = st.checkbox("Water service?", key="shaft_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="shaft_stamicarbon")
        hf_service  = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="shaft_hf")

        if st.button("Generate Output", key="shaft_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip()
            df_match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = df_match["FPD Code"].iloc[0] if not df_match.empty else ""

            # ─── Tags di qualità di default per Shaft ───
            sq_tags = [
                "[SQ60]",
                "[DE3513.014]",
                "[CORP-ENG-0115]",
                "[SQ58]",
                "[SQ62]",
            ]
            quality_lines = [
                "SQ 60 - Procedura di Esecuzione del Run-Out per Alberi e Rotori di Pompe",
                "DE 3513.014 - Shaft Demagnetization",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1",
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "SQ 62 - Standard of definition of the Supply Condition and of the Heat Treatment of Stress Relieving in the rough machining condition of shafts from bar or forging",
            ]

            # ─── Logica SQ123 per QL/QLQ e materiali ASTM specifici ───
            astm_names = [
                "4140", "4140 HRC 22 max", "4140 quenched & tempered (with mechanical properties according to ASTM A434 4140 Class BC)",
                "Tp. 410 Quen Temp Cd T", "Tp. 410 - Annealed Condition A", "Tp. 410 BHN 250-300",
                "Tp. 410 DOUBLE TEMPERED HRC 22 MAX NACE", "Tp. 410 - Double-tempered HB 237 max.",
                "Tp. 410 HB 352-400", "Tp. 410 HB 325-375", "Tp. 410 HB 300-350",
                "Tp. 410 Cond A", "Tp. 410 Double Tempered HRC 22 max.", "Tp. 410 Quenched & Tempered - Cond. T"
            ]
            if model in ["QL", "QLQ"] and mtype == "ASTM" and mname in astm_names:
                sq_tags.insert(0, "[SQ123]")
                quality_lines.insert(0, "SQ 123 - Specifica di Trattamento Termico di Stabilizzazione degli Alberi delle Pompe Multistadio")

            # ─── Aggiunte condizionali ───
            if overlay:
                sq_tags.append("[PQ72]")
                quality_lines.append("PQ 72 - Components with overlay applied thru DLD, PTAW + Components with Laser Hardening surface + METCO or Ceramic Chrome overlay")
            if hvof:
                sq_tags.append("[DE2500.002]")
                quality_lines.append("DE 2500.002 - Surface coating by HVOF - High Velocity Oxygen Fuel Thermal Spray System")
            if water:
                sq_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon:
                sq_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")
            if hf_service:
                sq_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")

            tag_string = " ".join(sq_tags)
            quality    = "\n".join(quality_lines)

            # ─── Costruzione Description ───
            descr_parts = ["SHAFT, PUMP"] + [
                v for v in [model, size, brg_type, brg_size, max_diam, max_len, note, materiale, material_note] if v
            ]
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

            st.session_state["output_data"] = {
                "Item":              "40231…",
                "Description":       descr,
                "Identificativo":    "2100-SHAFT",
                "Classe ricambi":    "2-3",
                "Categories":        "FASCIA ITE 4",
                "Catalog":           "ALBERO",
                "Disegno":           dwg,
                "Material":          materiale,
                "FPD material code": codice_fpd,
                "Template":          "FPD_MAKE",
                "ERP_L1":            "20_TURNKEY_MACHINING",
                "ERP_L2":            "25_SHAFTS",
                "To supplier":       "",
                "Quality":           quality
            }

    # ─── COLONNA 2: OUTPUT ───
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Description", "Quality", "To supplier"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # ─── COLONNA 3: DATALOAD ───
    with col3:
        render_dataload_panel(
            item_code_key="shaft_item_code",
            create_btn_key="gen_dl_shaft",
            update_btn_key="gen_upd_shaft"
        )

elif selected_part == "Housing, Bearing":
    col1, col2, col3 = st.columns(3)

    brg_types = ["W", "W-TK", "EC", "ECR", "ESBR", "EKBR", "ECH", "ESH", "EKH"]
    brg_size_options = {
        "W": ["W040", "W050", "W070", "W090", "W091", "W091-N", "W092", "W092-N", "W105", "W105-N"],
        "W-TK": ["W040-TK", "W050-TK", "W070-TK", "W090-TK", "W091-TK", "W091-N-TK", "W092-TK", "W092-N-TK", "W105-TK", "W105-N-TK"],
        "EC": ["EC0", "EC1", "EC2", "EC34", "EC5", "EC6", "EC7", "EC8", "EC85", "EC9"],
        "ECR": ["ECR0", "ECR1", "ECR2", "ECR34", "ECR5", "ECR6", "ECR7", "ECR8", "ECR85", "ECR9"],
        "ESBR": ["ESBR0", "ESBR1", "ESBR2", "ESBR34", "ESBR5", "ESBR6", "ESBR7", "ESBR8", "ESBR85", "ESBR9"],
        "EKBR": ["EKBR0", "EKBR1", "EKBR2", "EKBR34", "EKBR5", "EKBR6", "EKBR7", "EKBR8", "EKBR85", "EKBR9"],
        "ECH": ["EC0-H", "EC2-H", "EC5-H", "EC6-H", "EC7-H", "EC8-H", "EC85-H", "EC9-H", "EC10-H", "EC11-H", "EC12-H", "EC15-H"],
        "ESH": ["ES0-H", "ES2-H", "ES5-H", "ES6-H", "ES7-H", "ES8-H", "ES85-H", "ES9-H", "ES10-H", "ES11-H", "ES12-H"],
        "EKH": ["EK0-H", "EK2-H", "EK5-H", "EK6-H", "EK7-H", "EK8-H", "EK85-H", "EK9-H", "EK10-H", "EK11-H", "EK12-H"],
    }

    with col1:
        st.subheader("✏️ Input")
        brg_type = st.selectbox("Bearing Type", [""] + brg_types, key="bh_brg_type")
        brg_size = st.selectbox(
            "Bearing Size",
            [""] + brg_size_options.get(brg_type, []),
            key="bh_brg_size",
        )
        dwg = st.text_input("Drawing number", key="bh_dwg")
        note = st.text_area("Note", height=80, key="bh_note")

        mtype = st.selectbox(
            "Material Type",
            ["", "ASTM"] + [t for t in material_types if t != "ASTM"],
            key="bh_mtype",
        )
        prefixes = sorted(
            materials_df[materials_df["Material Type"] == mtype]["Prefix"].dropna().unique().tolist()
        )
        mprefix = st.selectbox(
            "Material Prefix",
            ["", "A322_", "A276_", "A473_"]
            + [p for p in prefixes if p not in ["A322_", "A276_", "A473_"]],
            key="bh_mprefix",
        )
        names = materials_df[
            (materials_df["Material Type"] == mtype)
            & (materials_df["Prefix"] == mprefix)
        ]["Name"].dropna().tolist()
        mname = st.selectbox("Material Name", [""] + names, key="bh_mname")
        material_note = st.text_area("Material Note", height=60, key="bh_matnote")

        if st.button("Generate Output", key="bh_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip()
            df_match = materials_df[
                (materials_df["Material Type"] == mtype)
                & (materials_df["Prefix"] == mprefix)
                & (materials_df["Name"] == mname)
            ]
            codice_fpd = df_match["FPD Code"].iloc[0] if not df_match.empty else ""

            descr_parts = ["BEARING HOUSING"] + [
                v for v in [brg_type, brg_size, note, materiale, material_note] if v
            ]
            descr_parts.append("[CORP-ENG-0190]")
            quality_lines = [
                "CORP-ENG-0190 - Coatings Specification for Bearings Housing and Frame Internal Oil Contacting Surfaces D16-1",
            ]
            if brg_type in ["W", "W-TK"]:
                descr_parts.append("[SQ36]")
                quality_lines.append("SQ 36 - HPX Bearing Housing: Requisiti di Qualità")
            quality = "\n".join(quality_lines)
            descr = "*" + " - ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": "40217…",
                "Description": descr,
                "Identificativo": "3200-BEARING HOUSING",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "SUPPORTO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "12_BEARING_HOUSING",
                "To supplier": "",
                "Quality": quality,
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Description", "Quality", "To supplier"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    with col3:
        render_dataload_panel(
            item_code_key="bh_item_code",
            create_btn_key="gen_dl_bh",
            update_btn_key="gen_upd_bh",
        )

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


        if st.button("Generate Output"):
            item = "477..."
            ident = "6110-BASE PLATE"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "ARTVARI"
            drawing_out = drawing
            material = f"{mat_type} {mat_prefix} {mat_name}".strip()
            fpd_code = get_fpd_code(materials_df, mat_type, mat_prefix, mat_name)
            template = "FPD_BUY_4"
            erp1 = "21_FABRICATION_OR_BASEPLATES"
            erp2 = "18_FOUNDATION_PLATE"
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
            st.text_area("Quality", value="\n".join(data["Quality"]), height=200, key="base_out14")

    with col3:
        render_dataload_panel(
            item_code_key="base_item_code",
            create_btn_key="gen_dl_base",
            update_btn_key="gen_upd_base"
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
        stamicarbon_flange = st.checkbox("Stamicarbon?", key="flange_stamicarbon")

        if st.button("Generate Output", key="flange_gen"):
            descr = (
                f"FLANGE, PIPE - TYPE: {pipe_type}, SIZE: {pipe_size}, FACE: {face_type}, "
                f"CLASS: {pressure_class}, MATERIAL: {material_flange}"
            )
            if note_flange:
                descr += f", NOTE: {note_flange}"

            tag_string, quality = build_quality_tags({
                "hf_service": hf_service_flange,
                "stamicarbon": stamicarbon_flange,
                "include_standard": False,
            })

            descr = "*" + descr
            if tag_string:
                descr += f" {tag_string}"

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
                    st.text_area(campo, value=valore, height=200, key=f"fl_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"fl_{campo}")

    # COLONNA 3 – DATALOAD
    with col3:
        render_dataload_panel(
            item_code_key="flange_item_code",
            create_btn_key="gen_dl_flange",
            update_btn_key="gen_upd_flange"
        )

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
        stamicarbon_gf = st.checkbox("Stamicarbon?", key="gf_stamicarbon")

        if st.button("Generate Output", key="gf_gen"):
            descr_gf = (
                f"GASKET, FLAT - THICKNESS: {thickness_gf}{unit_gf.upper()}, MATERIAL: {material_gf}"
            )
            if note_gf:
                descr_gf += f", NOTE: {note_gf}"

            tag_string, quality = build_quality_tags({
                "hf_service": hf_service_gf,
                "stamicarbon": stamicarbon_gf,
                "include_standard": False,
            })

            descr_gf = "*" + descr_gf
            if tag_string:
                descr_gf += f" {tag_string}"

            st.session_state["output_data"] = {
                "Item": "50158…",
                "Description": descr_gf,
                "Identificativo": "4590-GASKET",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_gf,
                "Material": material_gf,
                "FPD material code": "NOT AVAILABLE",
                "Template": "FPD_BUY_2",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "To supplier": "",
                "Quality": quality
            }

    # COLONNA 2 – OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo in ["Description", "Quality"]:
                    st.text_area(campo, value=valore, height=200, key=f"gf_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"gf_{campo}")

    # COLONNA 3 – DATALOAD
    with col3:
        render_dataload_panel(
            item_code_key="gf_item_code",
            create_btn_key="gen_dl_gf",
            update_btn_key="gen_upd_gf"
        )


# --- SCREW, CAP
if selected_part == "Screw, Cap":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")

        size_cap   = st.selectbox("Size",   [""] + bolt_sizes,   key="cap_size")
        length_cap = st.selectbox("Length", [""] + bolt_lengths, key="cap_length")

        full_thread_cap = st.radio("Full threaded?", ["No", "Yes"], index=0, key="cap_full_thread")

        note_cap = st.text_area("Note", height=80, key="cap_note")

        # Materiale
        mtype_cap = st.selectbox("Material Type", [""] + material_types, key="cap_mtype")
        pref_df_cap = materials_df[(materials_df["Material Type"] == mtype_cap) & (materials_df["Prefix"].notna())]
        prefixes_cap = sorted(pref_df_cap["Prefix"].unique()) if mtype_cap != "MISCELLANEOUS" else []
        mprefix_cap = st.selectbox("Material Prefix", [""] + prefixes_cap, key="cap_mprefix")

        if mtype_cap == "MISCELLANEOUS":
            names_cap = materials_df[materials_df["Material Type"] == mtype_cap]["Name"].dropna().tolist()
        else:
            names_cap = materials_df[
                (materials_df["Material Type"] == mtype_cap) &
                (materials_df["Prefix"] == mprefix_cap)
            ]["Name"].dropna().tolist()
        mname_cap = st.selectbox("Material Name", [""] + names_cap, key="cap_mname")

        # 👉 Zinc dopo il materiale
        zinc_plated_cap = st.radio("Zinc plated?", ["No", "Yes"], index=0, key="cap_zinc")
        stamicarbon_cap = st.checkbox("Stamicarbon?", key="cap_stamicarbon")

        material_note_cap = st.text_area("Material note", height=60, key="cap_matnote")

        if st.button("Generate Output", key="cap_gen"):
            materiale_cap = (
                mname_cap if mtype_cap == "MISCELLANEOUS"
                else f"{mtype_cap} {mprefix_cap} {mname_cap}".strip()
            )

            match_cap = materials_df[
                (materials_df["Material Type"] == mtype_cap) &
                (materials_df["Prefix"] == mprefix_cap) &
                (materials_df["Name"] == mname_cap)
            ]
            codice_fpd_cap = match_cap["FPD Code"].values[0] if not match_cap.empty else ""

            descr_parts_cap = [
                "CAP SCREW",
                size_cap,
                length_cap,
                "FULL THREADED" if full_thread_cap == "Yes" else "",
                note_cap,
                materiale_cap,
                "ZINC PLATED" if zinc_plated_cap == "Yes" else "",
                material_note_cap
            ]
            tag_string, quality = build_quality_tags({
                "stamicarbon": stamicarbon_cap,
                "include_standard": False,
            })
            descr_cap = "*" + " - ".join([p for p in descr_parts_cap if p])
            if tag_string:
                descr_cap += f" {tag_string}"

            st.session_state["output_data"] = {
                "Item": "56230…",
                "Description": descr_cap,
                "Identificativo": "6579-SOCKET HEAD CAP SCREW",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_cap,
                "FPD material code": codice_fpd_cap,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": quality,
            }



    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="cap_item_code",
            create_btn_key="gen_dl_cap",
            update_btn_key="gen_upd_cap"
        )




# --- SCREW, GRUB
if selected_part == "Screw, Grub":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")

        size_grub   = st.selectbox("Size",   [""] + bolt_sizes,   key="grub_size")
        length_grub = st.selectbox("Length", [""] + bolt_lengths, key="grub_length")

        note_grub = st.text_area("Note", height=80, key="grub_note")

        # Materiale (Type -> Prefix -> Name)
        mtype_grub = st.selectbox("Material Type", [""] + material_types, key="grub_mtype")
        pref_df_grub = materials_df[
            (materials_df["Material Type"] == mtype_grub) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_grub = sorted(pref_df_grub["Prefix"].unique()) if mtype_grub != "MISCELLANEOUS" else []
        mprefix_grub = st.selectbox("Material Prefix", [""] + prefixes_grub, key="grub_mprefix")

        if mtype_grub == "MISCELLANEOUS":
            names_grub = materials_df[materials_df["Material Type"] == mtype_grub]["Name"].dropna().tolist()
        else:
            names_grub = materials_df[
                (materials_df["Material Type"] == mtype_grub) &
                (materials_df["Prefix"] == mprefix_grub)
            ]["Name"].dropna().tolist()
        mname_grub = st.selectbox("Material Name", [""] + names_grub, key="grub_mname")

        material_note_grub = st.text_area("Material note", height=60, key="grub_matnote")
        stamicarbon_grub = st.checkbox("Stamicarbon?", key="grub_stamicarbon")

        if st.button("Generate Output", key="grub_gen"):
            materiale_grub = (
                mname_grub if mtype_grub == "MISCELLANEOUS"
                else f"{mtype_grub} {mprefix_grub} {mname_grub}".strip()
            )

            match_grub = materials_df[
                (materials_df["Material Type"] == mtype_grub) &
                (materials_df["Prefix"] == mprefix_grub) &
                (materials_df["Name"] == mname_grub)
            ]
            codice_fpd_grub = match_grub["FPD Code"].values[0] if not match_grub.empty else ""

            descr_parts_grub = [
                "GRUB SCREW",
                size_grub,
                length_grub,
                note_grub,
                materiale_grub,
                material_note_grub
            ]
            tag_string, quality = build_quality_tags({
                "stamicarbon": stamicarbon_grub,
                "include_standard": False,
            })
            descr_grub = "*" + " - ".join([p for p in descr_parts_grub if p])
            if tag_string:
                descr_grub += f" {tag_string}"

            st.session_state["output_data"] = {
                "Item": "56310…",
                "Description": descr_grub,
                "Identificativo": "6814-GRUB SCREW",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_grub,
                "FPD material code": codice_fpd_grub,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "74_OTHER_FAST_COMP_EYE_NUTS_LOCK_NUTS",
                "To supplier": "",
                "Quality": quality,
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="grub_item_code",
            create_btn_key="gen_dl_grub",
            update_btn_key="gen_upd_grub"
        )


# --- CASTING PARTS (unico blocco per tutte le voci di casting) ---
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

    # Inizializza flag
    if "cast_generated" not in st.session_state:
        st.session_state.cast_generated = False

    # ─── COLONNA 1: INPUT ───
    with col_input:
        st.markdown("### 📥 Input")
        # Pump type for DMX/HPX logic
        if selected_part == "Impeller casting":
            imp_pump_type = st.selectbox(
                "Impeller Pump Type", ["Other", "DMX"], key="cast_imp_pump_type"
            )
        if selected_part == "Bearing housing casting":
            pump_type = st.selectbox(
                "Pump Type", ["Other", "HPX"], key="cast_pump_type"
            )
        base_pattern    = st.text_input("Base pattern", key="cast_base_pattern")
        mod1            = st.text_input("Pattern modification 1", key="cast_mod1")
        mod2            = st.text_input("Pattern modification 2", key="cast_mod2")
        mod3            = st.text_input("Pattern modification 3", key="cast_mod3")
        mod4            = st.text_input("Pattern modification 4", key="cast_mod4")
        mod5            = st.text_input("Pattern modification 5", key="cast_mod5")
        note            = st.text_input("Note", key="cast_note")
        casting_drawing = st.text_input("Casting drawing", key="cast_input_drawing")
        pattern_item    = st.text_input("Pattern item", key="cast_input_pattern")

        st.markdown("**Material selection**")
        material_type = st.selectbox("Material Type", [""] + material_types, key="cast_mat_type")
        prefixes      = sorted(materials_df[
            materials_df["Material Type"] == material_type
        ]["Prefix"].dropna().unique().tolist())
        prefix        = st.selectbox("Prefix", [""] + prefixes, key="cast_prefix")
        names         = sorted(materials_df[
            (materials_df["Material Type"] == material_type) &
            (materials_df["Prefix"] == prefix)
        ]["Name"].dropna().unique().tolist())
        name          = st.selectbox("Name", [""] + names, key="cast_name")
        material_note = st.text_input("Material Note", key="cast_mat_note")

        water_casting = False
        hf_service_casting = False
        stamicarbon_casting = False
        if selected_part not in [
            "Bearing housing casting",
            "Bearing bracket casting",
            "Bearing cover casting",
        ]:
            water_casting = st.checkbox("Water service?", key="cast_water")
            hf_service_casting = st.checkbox(
                "Is it an hydrofluoric acid alkylation service (lethal)?",
                key="cast_hf"
            )
            stamicarbon_casting = st.checkbox("Stamicarbon?", key="cast_stamicarbon")

        if st.button("Generate Output", key="cast_gen"):
            st.session_state.cast_generated = True

    # ─── COLONNA 2: OUTPUT ───
    if st.session_state.cast_generated:
        with col_output:
            st.markdown("### 📤 Output")
            dfm = materials_df[
                (materials_df["Material Type"] == material_type) &
                (materials_df["Prefix"] == prefix) &
                (materials_df["Name"] == name)
            ]
            casting_code      = dfm["Casting code"].iloc[0][-2:] if not dfm.empty else "XX"
            fpd_material_code = dfm["FPD Code"].iloc[0]       if not dfm.empty else "NA"
            item_number       = "7" + casting_code
            pattern_parts     = [m for m in [mod1, mod2, mod3, mod4, mod5] if m.strip()]
            pattern_full      = "/".join(pattern_parts)

            parts = [f"*{identificativo.upper()}"]
            if base_pattern: parts.append(f"BASE PATTERN: {base_pattern}")
            if pattern_full: parts.append(f"MODS: {pattern_full}")
            if note: parts.append(note)
            parts.append(f"{prefix} {name}".strip())
            if material_note: parts.append(material_note)

            qual_tags     = ["[SQ58]", "[CORP-ENG-0115]", "[DE2390.002]"]
            quality_lines = [
                "DE 2390.002 - Procurement and Quality Specification for Ferrous Castings",
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]
            if hf_service_casting:
                qual_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if water_casting:
                qual_tags.append("<PI23>")
                quality_lines.append("PI 23 - Pompe per Acqua Potabile")
            if stamicarbon_casting:
                qual_tags.append("<SQ172>")
                quality_lines.append("SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION")

            if selected_part == "Impeller casting" and st.session_state.get("cast_imp_pump_type") == "DMX":
                qual_tags.insert(0, "[CORP-ENG-0229]")
                quality_lines.insert(0, "CORP-ENG-0229 - Inspection Procedures and Requirements for DMX Impeller Castings J4-6")
            if selected_part == "Impeller casting":
                qual_tags.append("[DE2920.025]")
                quality_lines.append("DE2920.025 - Impellers' Allowable Tip Speed and Related N.D.E.")
            # ✔️ Qualità DE2980.001 per Impeller casting in 17-4 PH
            if selected_part == "Impeller casting" and prefix == "A747_" and name == "Tp. CB7Cu-1 (H1150 DBL)":
                qual_tags.append("[DE2980.001]")
                quality_lines.append("DE2980.001 - Progettazione e Produzione giranti in 17-4 PH")


            if selected_part == "Bearing housing casting" and st.session_state.get("cast_pump_type") == "HPX":
                qual_tags.insert(0, "[SQ36]")
                quality_lines.insert(0, "SQ 36 - HPX Bearing Housing: Requisiti di Qualità")

            hydraulic = [
                "Casing cover casting", "Casing casting", "Impeller casting",
                "Pump bowl casting", "Diffuser casting", "Inducer casting", "Wear plate casting"
            ]
            if selected_part in hydraulic:
                extra = ["[DE2390.001]", "[CORP-ENG-0523]", "[CORP-ENG-0090]"]
                qual_tags.extend(extra)
                quality_lines.extend([
                    "DE 2390.001 - Procurement and Cleaning Requirements for Hydraulic Castings-API, Vertical, Submersible and Specially Pumps",
                    "CORP-ENG-0523 - As-Cast Surface Finish and Cleaning Requirements for Hydraulic Castings",
                    "CORP-ENG-0090 - Procurement and Cleaning Requirement for Hydraulic Castings - API, Vertical, Submersible, and Specialty Pumps P-5"
                ])

            cg_materials = {
                ("A351_","CG3M"),("A351_","CG8M"),("A743_","CG3M"),("A743_","CG8M"),
                ("A351_","CG8M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY"),
                ("A351_","CG3M + HVOF TUNGS. CARBIDE 86-10-4 (WC-Co-Cr) OVERLAY + PTA STELLITE 6 OVERLAY"),
                ("A743_","CG8M + PTA STELLITE 12 OVERLAY"),("A743_","CG3M + PTA STELLITE 6 OVERLAY"),
                ("A743_","CG3M + DLD WC-Ni 60-40"),("A744_","CG3M")
            }
            if (prefix, name) in cg_materials:
                qual_tags.append("[SQ95]")
                quality_lines.append("SQ 95 - Ciclo di Lavorazione CG3M e CG8M (fuso AISI 317L e AISI 317)")

            quality_field = "\n".join(quality_lines)
            description   = ", ".join(parts) + " " + " ".join(qual_tags)

            st.text_input("Item", value=item_number, key="cast_out_item")
            st.text_area ("Description", value=description, height=120, key="cast_out_desc")
            st.text_input("Identificativo", value=identificativo, key="cast_out_id")
            st.text_input("Classe ricambi", value="", key="cast_out_class")
            st.text_input("Categories", value="FASCIA ITE 7", key="cast_out_cat")
            st.text_input("Catalog", value="FUSIONI", key="cast_out_catalog")
            st.text_input("Casting drawing", value=casting_drawing, key="cast_out_drawing")
            st.text_input("Pattern item", value=pattern_full, key="cast_out_pattern")
            st.text_input("Material", value=f"{prefix} {name}", key="cast_out_material")
            st.text_input("FPD Material Code", value=fpd_material_code, key="cast_out_fpd")
            st.text_input("Template", value="FPD_BUY_CASTING", key="cast_out_template")
            st.text_input("ERP L1", value="10_CASTING", key="cast_out_erp1")
            st.text_input("ERP L2", value="", key="cast_out_erp2")
            st.text_input("To Supplier", value="", key="cast_out_supplier")
            st.text_area ("Quality", value=quality_field, height=300, key="cast_out_quality")

    # --- COLONNA 3: DATALOAD ---
       # --- COLONNA 3: DATALOAD ---
    with col_dataload:
        st.markdown("### 🧾 DataLoad")
        mode         = st.radio(
            "Operation type:",
            ["Create new item", "Update item"],
            key="cast_mode"
        )
        item_code_dl = st.text_input("Item code", key="cast_dl_code")

        if mode == "Create new item":
            if st.button("Generate DataLoad string", key="cast_dl_create"):
                if not item_code_dl:
                    st.error("❌ Please enter the item code first.")
                else:
                    st.success("✅ DataLoad string successfully generated. Download the CSV below.")
        else:
            if st.button("Generate Update string", key="cast_dl_update"):
                if not item_code_dl:
                    st.error("❌ Please enter the item code first.")
                else:
                    st.success("✅ Update string successfully generated.")

# --- Footer (mostrato sempre) ---
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
.footer a {
    color: inherit;
    text-decoration: underline;
}
</style>
<div class="footer">
    © 2025 Flowserve – Desio Order Engineering – 
    <a href="mailto:dzecchinel@flowserve.com">dzecchinel@flowserve.com</a>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
