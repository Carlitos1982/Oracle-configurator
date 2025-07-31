import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

import io, csv, streamlit as st

def render_dataload_panel(item_code_key: str,
                          create_btn_key: str,
                          update_btn_key: str,
                          state_key: str = "output_data"):
    st.subheader("🧾 DataLoad")
    mode = st.radio(
        "Operation type:",
        ["Create new item", "Update existing item"],
        key=f"{item_code_key}_mode"
    )

    item_code = st.text_input("Item Code", key=item_code_key)
    data = st.session_state.get(state_key, {})

    raw_q = data.get("Quality", "").strip()
    if not raw_q:
        quality_tokens = ["NA"]
    else:
        quality_tokens = []
        for line in raw_q.splitlines():
            quality_tokens.append(line)
            quality_tokens.append("\\{NUMPAD ENTER}")
        if quality_tokens and quality_tokens[-1] == "\\{NUMPAD ENTER}":
            quality_tokens.pop()

    def get_val(k, default="."):
        v = data.get(k, "").strip()
        return v if v else default

    if mode == "Create new item":
        if st.button("Generate DataLoad string", key=create_btn_key):
            if not item_code:
                st.error("❌ Please enter the item code first.")
            else:
                fields = [
                    "\\%FN",            item_code,
                    "\\%TC",            get_val("Template"),
                    "TAB",
                    "\\%D", "\\%O",
                    "TAB",
                    get_val("Description"),
                    *["TAB"]*6,
                    get_val("Identificativo"),
                    "TAB",
                    get_val("Classe ricambi"),
                    "TAB",
                    "\\%O", "\\^S", "\\%TA",
                    "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}",
                    "TAB", "FASCIA ITE", "TAB",
                    item_code[:1], "TAB",
                    "\\^S", "\\^{F4}", "\\%TG",
                    get_val("Catalog"),
                    *["TAB"]*4,
                    get_val("Disegno"), "TAB",
                    "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", *["TAB"]*2,
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\\^S", "\\^S", "\\^{F4}", "\\%VA",
                    "TAB", "Quality", *["TAB"]*4,
                    *quality_tokens,
                    "\\^S", "\\^{F4}", "\\^S"
                ]

                st.success("✅ DataLoad string successfully generated. Download the CSV file below.")
                buf = io.StringIO()
                writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
                for tok in fields:
                    writer.writerow([tok])
                st.download_button(
                    "💾 Download CSV for Import",
                    data=buf.getvalue(),
                    file_name=f"dataload_{item_code}.csv",
                    mime="text/csv"
                )

    else:
        if st.button("Generate Update string", key=update_btn_key):
            if not item_code:
                st.error("❌ Please enter the item code first.")
            else:
                fields = [
                    "\\%VF",            item_code,
                    "\\{NUMPAD ENTER}", "TAB",
                    get_val("Description", "*?"),
                    *["TAB"]*6,
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\\%O", "\\^S", "\\%TA",
                    "\\%VF",            "FASCIA ITE", "\\{NUMPAD ENTER}", "TAB",
                    item_code[:1],     "\\^S",
                    "\\%VF",           "TIPO ARTICOLO", "\\{NUMPAD ENTER}", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "\\^S", "\\^{F4}",
                    "\\%TG",           get_val("Catalog"),
                    *["TAB"]*3,        get_val("Disegno"), "TAB",
                    "\\^S", "\\^{F4}", "\\^S",
                    "\\%VA",           "TAB", "Quality", *["TAB"]*4,
                    *quality_tokens,
                    "\\^S", "\\^{F4}", "\\^S"
                ]

                st.success("✅ Update string successfully generated. Download the CSV file below.")
                buf = io.StringIO()
                writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
                for tok in fields:
                    writer.writerow([tok])
                st.download_button(
                    "💾 Download CSV for Update",
                    data=buf.getvalue(),
                    file_name=f"update_{item_code}.csv",
                    mime="text/csv"
                )


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

# --- SKF MODELS (serie principali – aggiungi/rimuovi a piacere)
skf_models = [
    "6000","6001","6002","6003","6004","6005","6006","6007","6008","6009","6010",
    "6200","6201","6202","6203","6204","6205","6206","6207","6208","6209","6210","6211","6212",
    "6300","6301","6302","6303","6304","6305","6306","6307","6308","6309","6310","6311","6312",
    "3200","3201","3202","3203","3204","3205","3206","3207","3208","3209","3210",
    "7200","7201","7202","7203","7204","7205","7206","7207","7208","7209","7210","7211","7212",
    "7300","7301","7302","7303","7304","7305","7306","7307","7308","7309","7310","7311","7312",
    "1200","1201","1202","1203","1204","1205","1206","1207","1208","1209","1210",
    "2200","2201","2202","2203","2204","2205","2206","2207","2208","2209","2210",
    "NU202","NU203","NU204","NU205","NU206","NU207","NU208","NU209","NU210",
    "NUP202","NUP203","NUP204","NUP205","NUP206","NUP207","NUP208","NUP209","NUP210",
    "NJ202","NJ203","NJ204","NJ205","NJ206","NJ207","NJ208","NJ209","NJ210",
    "22205","22206","22207","22208","22209","22210","22211","22212",
    "22308","22309","22310","22311","22312",
    "23022","23024","23026","23120","23122","23124",
    "30205","30206","30207","30208","30209","30210","30211","30212",
    "30305","30306","30307","30308","30309","30310",
    "32005","32006","32007","32008","32009","32010","32011","32012",
]

# --- Seals / Shields
skf_seals = ["", "2RS1", "2RSH", "2RSL", "RS1", "RS", "Z", "ZZ", "2Z"]

# --- Design / angolo di contatto / capacità
skf_design = ["", "BE (40° AC, paired)", "B (40° AC)", "AC (25° AC)", "A (30° AC)",
              "E (high capacity)", "EC (high capacity)"]

# --- Pairing / Preload
skf_pairing = ["", "CB (light preload)", "CC (medium preload)", "CD (heavy preload)",
               "GA (paired)", "GB (paired)", "GC (paired)"]

# --- Cage
skf_cages = ["", "TN9 (polyamide)", "J (pressed steel)", "M (machined brass)",
             "MA (brass)", "CA (brass)", "CC (polyamide)"]

# --- Clearance
skf_clearances = ["", "C2", "CN (normal)", "C3", "C4", "C5"]

# --- Tolerance class
skf_tolerances = ["", "P0 (normal)", "P6", "P5", "P4"]

# --- Heat treatment / Stabilization
skf_heat = ["", "S0", "S1", "S2", "S3"]

# --- Grease / Lubricant
skf_greases = ["", "VT143", "VT378", "MT33", "GJN"]

# --- Vibration
skf_vibration = ["", "V1", "V2", "V3", "V4", "VA201", "VA208", "VA228"]

# ------------------ DIZIONARI DESCRITTIVI ------------------
base_series_desc = {
    "60":  "Deep groove ball bearing – light series",
    "62":  "Deep groove ball bearing – medium series",
    "63":  "Deep groove ball bearing – heavy series",
    "72":  "Angular contact ball bearing – 15°",
    "73":  "Angular contact ball bearing – 40°",
    "32":  "Double-row angular contact ball bearing",
    "12":  "Self-aligning ball bearing – light series",
    "22":  "Self-aligning ball bearing – medium series",
    "NU":  "Cylindrical roller bearing (NU)",
    "NUP": "Cylindrical roller bearing (NUP)",
    "NJ":  "Cylindrical roller bearing (NJ)",
    "222": "Spherical roller bearing – 222 series",
    "223": "Spherical roller bearing – 223 series",
    "230": "Spherical roller bearing – 230 series",
    "231": "Spherical roller bearing – 231 series",
    "302": "Tapered roller bearing – 302 series",
    "303": "Tapered roller bearing – 303 series",
    "320": "Tapered roller bearing – 320 series",
}

design_desc = {
    "BE": "40° AC, paired",
    "B" : "40° AC",
    "AC": "25° AC",
    "A" : "30° AC",
    "E" : "high capacity",
    "EC": "high capacity"
}
pairing_desc = {
    "CB": "light preload",
    "CC": "medium preload",
    "CD": "heavy preload",
    "GA": "paired",
    "GB": "paired",
    "GC": "paired"
}
cage_desc = {
    "TN9": "polyamide cage",
    "J"  : "pressed steel cage",
    "M"  : "machined brass cage",
    "MA" : "brass cage",
    "CA" : "brass cage",
    "CC" : "polyamide cage"
}
clearance_desc = {
    "C2": "reduced clearance",
    "CN": "normal clearance",
    "C3": "increased clearance",
    "C4": "large clearance",
    "C5": "very large clearance"
}
tolerance_desc = {"P0": "normal tol.", "P6": "P6 tol.", "P5": "P5 tol.", "P4": "P4 tol."}
heat_desc      = {"S0": "stabilized S0", "S1": "S1", "S2": "S2", "S3": "S3"}
grease_desc    = {"VT143": "grease VT143", "VT378": "grease VT378", "MT33": "grease MT33", "GJN": "grease GJN"}
vibration_desc = {"V1": "V1 vib.", "V2": "V2 vib.", "V3": "V3 vib.", "V4": "V4 vib.",
                  "VA201": "VA201 vib.", "VA208": "VA208 vib.", "VA228": "VA228 vib."}

# --- Liste spine cilindriche
dowel_diameters_mm_raw = ["Ø1","Ø1.5","Ø2","Ø2.5","Ø3","Ø4","Ø5","Ø6","Ø8","Ø10",
                          "Ø12","Ø14","Ø16","Ø18","Ø20","Ø22","Ø25","Ø30"]
dowel_lengths_mm       = ["4mm","5mm","6mm","8mm","10mm","12mm","16mm","20mm","25mm","30mm",
                          "35mm","40mm","45mm","50mm","60mm","70mm","80mm","90mm","100mm"]

dowel_diameters_in = ['1/16"', '3/32"', '1/8"', '5/32"', '3/16"', '7/32"', '1/4"', '9/32"',
                      '5/16"', '3/8"', '7/16"', '1/2"', '9/16"', '5/8"', '3/4"', '7/8"', '1"']
dowel_lengths_in   = ['1/4"', '3/8"', '1/2"', '5/8"', '3/4"', '1"', '1-1/4"', '1-1/2"',
                      '1-3/4"', '2"', '2-1/4"', '2-1/2"', '3"', '3-1/2"', '4"']



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

# --- CASING, PUMP
if selected_part == "Casing, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1 – INPUT
    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="casing_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="casing_size")

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

        note = st.text_area("Note", height=80, key="casing_note")
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
        material_note = st.text_area("Material note", height=60, key="casing_matnote")

        # ✅ Checkbox qualità extra
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="casing_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="casing_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="casing_overlay")
        hvof = st.checkbox("HVOF coating?", key="casing_hvof")
        water = st.checkbox("Water service?", key="casing_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="casing_stamicarbon")
        if st.button("Generate Output", key="casing_gen"):
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
                sq_tags.append("[PQ72]")
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

            # --- DESCRIZIONE
            descr_parts = ["CASING, PUMP"]
            for val in [model, size, feature_1, feature_2, note]:
                if val:
                    descr_parts.append(val)
            if mtype or mprefix or mname:
                descr_parts.append(" ".join([mtype, mprefix, mname]).strip())
            if material_note:
                descr_parts.append(material_note)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
        )

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
        material_note = st.text_area("Material note", height=60, key="ccov_matnote")

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
                sq_tags.append("[PQ72]")
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

            descr_parts = ["CASING COVER, PUMP"]
            for val in [model, size, feature_1, note]:
                if val:
                    descr_parts.append(val)
            if mtype or mprefix or mname:
                descr_parts.append(" ".join([mtype, mprefix, mname]).strip())
            if material_note:
                descr_parts.append(material_note)

            descr = "*" + " - ".join(descr_parts) + " " + tag_string


            st.session_state["output_data"] = {
                "Item": "40205…",
                "Description": descr,
                "Identificativo": "1200-CASING COVER",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "CORPO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": template,
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

    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
        )




# --- IMPELLER, PUMP
if selected_part == "Impeller, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="imp_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="imp_size")

        # Feature 1 come menu a tendina
        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="imp_feat1") if f1_list else ""

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
        material_note = st.text_area("Material note", height=60, key="imp_matnote")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="imp_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="imp_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="imp_overlay")
        hvof = st.checkbox("HVOF coating?", key="imp_hvof")
        water = st.checkbox("Water service?", key="imp_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="imp_stamicarbon")

        if st.button("Generate Output", key="imp_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            # Qualità
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

            # Descrizione finale
            descr_parts = ["IMPELLER, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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

    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
        material_note = st.text_area("Material note", height=60, key="bbush_matnote")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bbush_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bbush_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bbush_overlay")
        hvof = st.checkbox("HVOF coating?", key="bbush_hvof")
        water = st.checkbox("Water service?", key="bbush_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bbush_stamicarbon")

        if st.button("Generate Output", key="bbush_gen"):
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

            # Descrizione finale
            descr_parts = ["BALANCE BUSHING, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
        material_note = st.text_area("Material note", height=60, key="bdrum_matnote")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bdrum_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bdrum_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bdrum_overlay")
        hvof = st.checkbox("HVOF coating?", key="bdrum_hvof")
        water = st.checkbox("Water service?", key="bdrum_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bdrum_stamicarbon")

        if st.button("Generate Output", key="bdrum_gen"):
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

            # Descrizione finale
            descr_parts = ["BALANCE DRUM, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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

    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
        material_note = st.text_area("Material note", height=60, key="bdisc_matnote")

        # Checkbox qualità
        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="bdisc_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="bdisc_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="bdisc_overlay")
        hvof = st.checkbox("HVOF coating?", key="bdisc_hvof")
        water = st.checkbox("Water service?", key="bdisc_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="bdisc_stamicarbon")

        if st.button("Generate Output", key="bdisc_gen"):
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

            descr_parts = ["BALANCE DISC, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        if st.button("Generate Output", key="gate_gen"):
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

            # tag di qualità in coda
            qual_tags = ["[SQ174]"]
            quality_lines = [
                "SQ 174 - Casing/Cover pump spiral wound gaskets: Specification for Mechanical properties, applicable materials and dimensions"
            ]
            if hf_service_gsw:
                qual_tags.append("<SQ113>")
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")

            descr_gsw += " " + " ".join(qual_tags)
            quality_field = "\n".join(quality_lines)

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
                    st.text_area(campo, value=valore, height=120, key=f"sw_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"sw_{campo}")

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code",
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        # Materiale (Type -> Prefix -> Name)
        mtype_bear = st.selectbox("Material Type", [""] + material_types, key="bear_mtype")
        pref_df_bear = materials_df[
            (materials_df["Material Type"] == mtype_bear) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_bear = sorted(pref_df_bear["Prefix"].unique()) if mtype_bear != "MISCELLANEOUS" else []
        mprefix_bear = st.selectbox("Material Prefix", [""] + prefixes_bear, key="bear_mprefix")

        if mtype_bear == "MISCELLANEOUS":
            names_bear = materials_df[materials_df["Material Type"] == mtype_bear]["Name"].dropna().tolist()
        else:
            names_bear = materials_df[
                (materials_df["Material Type"] == mtype_bear) &
                (materials_df["Prefix"] == mprefix_bear)
            ]["Name"].dropna().tolist()
        mname_bear = st.selectbox("Material Name", [""] + names_bear, key="bear_mname")

        # ex Material add. features -> Material note
        material_note_bear = st.text_area("Material note", height=60, key="bear_matnote")

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
                "Item": "50XXX…",                 # mantieni il tuo valore originale
                "Description": descr_bear,
                "Identificativo": "XXXX-BEARING", # idem
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "CUSCINETTO",
                "Disegno": dwg_bear,
                "Material": materiale_bear,
                "FPD material code": codice_fpd_bear,
                "Template": "FPD_BUY_2",
                "ERP_L1": "50_BEARING",
                "ERP_L2": "10_HYDROSTATIC_HYDRODYNAMIC",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
                "Item": "50YYY…",
                "Description": descr_roll,
                "Identificativo": "XXXX-ROLLING BEARING",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "CUSCINETTO",
                "Disegno": ".",                      # <-- nessun input, lo mettiamo a punto
                "Material": "COMMERCIAL BEARING",
                "FPD material code": "NA",
                "Template": "FPD_BUY_2",
                "ERP_L1": "50_BEARING",
                "ERP_L2": "20_ROLLING",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
        )



# --- BOLT, EYE
if selected_part == "Bolt, Eye":
    col1, col2, col3 = st.columns(3)

    # --------------------- COLONNA 1: INPUT ---------------------
    with col1:
        st.subheader("✏️ Input")
        size   = st.selectbox("Size",   [""] + bolt_sizes,   key="beye_size")
        length = st.selectbox("Length", [""] + bolt_lengths, key="beye_length")

        note                 = st.text_area("Note", height=80, key="beye_note")
        mtype_beye           = st.selectbox("Material Type", [""] + material_types, key="beye_mtype")
        pref_df_beye         = materials_df[(materials_df["Material Type"] == mtype_beye) & (materials_df["Prefix"].notna())]
        prefixes_beye        = sorted(pref_df_beye["Prefix"].unique()) if mtype_beye != "MISCELLANEOUS" else []
        mprefix_beye         = st.selectbox("Material Prefix", [""] + prefixes_beye, key="beye_mprefix")
        names_beye = (
            materials_df[materials_df["Material Type"] == mtype_beye]["Name"].dropna().tolist()
            if mtype_beye == "MISCELLANEOUS"
            else materials_df[
                (materials_df["Material Type"] == mtype_beye) &
                (materials_df["Prefix"] == mprefix_beye)
            ]["Name"].dropna().tolist()
        )
        mname_beye           = st.selectbox("Material Name", [""] + names_beye, key="beye_mname")
        material_note_beye   = st.text_area("Material note", height=60, key="beye_matnote")
        dwg                  = st.text_input("Dwg/doc number", key="beye_dwg")

        if st.button("Generate Output", key="beye_gen"):
            # costruisco il materiale e il codice FPD
            if mtype_beye == "MISCELLANEOUS":
                materiale = mname_beye
            else:
                materiale = f"{mtype_beye} {mprefix_beye} {mname_beye}".strip()

            match = materials_df[
                (materials_df["Material Type"] == mtype_beye) &
                (materials_df["Prefix"] == mprefix_beye) &
                (materials_df["Name"] == mname_beye)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            # descrizione: Size → Length → Note → Materiale → Material note
            descr_parts = ["EYE BOLT"]
            for val in [size, length, note, materiale, material_note_beye]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts)

            st.session_state["output_data"] = {
                "Item": "56120…",
                "Description": descr,
                "Identificativo": "6540-EYE BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
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

        # Materiale
        mtype_bh = st.selectbox("Material Type", [""] + material_types, key="bh_mtype")
        pref_df_bh = materials_df[(materials_df["Material Type"] == mtype_bh) & (materials_df["Prefix"].notna())]
        prefixes_bh = sorted(pref_df_bh["Prefix"].unique()) if mtype_bh != "MISCELLANEOUS" else []
        mprefix_bh = st.selectbox("Material Prefix", [""] + prefixes_bh, key="bh_mprefix")

        if mtype_bh == "MISCELLANEOUS":
            names_bh = materials_df[materials_df["Material Type"] == mtype_bh]["Name"].dropna().tolist()
        else:
            names_bh = materials_df[
                (materials_df["Material Type"] == mtype_bh) &
                (materials_df["Prefix"] == mprefix_bh)
            ]["Name"].dropna().tolist()
        mname_bh = st.selectbox("Material Name", [""] + names_bh, key="bh_mname")

        # 👉 Zinc dopo il materiale
        zinc_plated_bh = st.radio("Zinc plated?", ["No", "Yes"], index=0, key="bh_zinc")

        material_note_bh = st.text_area("Material note", height=60, key="bh_matnote")

        if st.button("Generate Output", key="bh_gen"):
            materiale_bh = (
                mname_bh if mtype_bh == "MISCELLANEOUS"
                else f"{mtype_bh} {mprefix_bh} {mname_bh}".strip()
            )

            match_bh = materials_df[
                (materials_df["Material Type"] == mtype_bh) &
                (materials_df["Prefix"] == mprefix_bh) &
                (materials_df["Name"] == mname_bh)
            ]
            codice_fpd_bh = match_bh["FPD Code"].values[0] if not match_bh.empty else ""

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
            descr_bh = "*" + " - ".join([p for p in descr_parts_bh if p])

            st.session_state["output_data"] = {
                "Item": "56020…",
                "Description": descr_bh,
                "Identificativo": "6520-HEXAGONAL BOLT",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_bh,
                "FPD material code": codice_fpd_bh,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # (col2 e col3 restano invariati)


    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        if st.button("Generate Output", key="rtj_gen"):
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        note2_gusset = st.text_area("Material Note", height=80, key="gusset_note2")

        if st.button("Generate Output", key="gen_gusset"):
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        # Selezione materiale (Type -> Prefix -> Name)
        mtype_stud = st.selectbox("Material Type", [""] + material_types, key="stud_mtype")
        pref_df_stud = materials_df[
            (materials_df["Material Type"] == mtype_stud) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_stud = sorted(pref_df_stud["Prefix"].unique()) if mtype_stud != "MISCELLANEOUS" else []
        mprefix_stud = st.selectbox("Material Prefix", [""] + prefixes_stud, key="stud_mprefix")

        if mtype_stud == "MISCELLANEOUS":
            names_stud = materials_df[materials_df["Material Type"] == mtype_stud]["Name"].dropna().tolist()
        else:
            names_stud = materials_df[
                (materials_df["Material Type"] == mtype_stud) &
                (materials_df["Prefix"] == mprefix_stud)
            ]["Name"].dropna().tolist()
        mname_stud = st.selectbox("Material Name", [""] + names_stud, key="stud_mname")

        material_note_stud = st.text_area("Material note", height=60, key="stud_matnote")

        # Disegno
        dwg_stud = st.text_input("Dwg/doc number", key="stud_dwg")

        if st.button("Generate Output", key="stud_gen"):
            materiale_stud = (
                mname_stud if mtype_stud == "MISCELLANEOUS"
                else f"{mtype_stud} {mprefix_stud} {mname_stud}".strip()
            )

            match_stud = materials_df[
                (materials_df["Material Type"] == mtype_stud) &
                (materials_df["Prefix"] == mprefix_stud) &
                (materials_df["Name"] == mname_stud)
            ]
            codice_fpd_stud = match_stud["FPD Code"].values[0] if not match_stud.empty else ""

            # Descrizione: Size → Length → Thread type → Note → Material → Material note
            descr_parts_stud = ["THREADED STUD", size_stud, length_stud, thread_type.upper()+" THREADED" if thread_type else "", note_stud, materiale_stud, material_note_stud]
            descr_stud = "*" + " - ".join([p for p in descr_parts_stud if p])

            st.session_state["output_data"] = {
                "Item": "56110…",
                "Description": descr_stud,
                "Identificativo": "6535-STUD THREADED",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_stud,
                "Material": materiale_stud,
                "FPD material code": codice_fpd_stud,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        # Selezione materiale (Type -> Prefix -> Name)
        mtype_nut = st.selectbox("Material Type", [""] + material_types, key="nut_mtype")
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

        material_note_nut = st.text_area("Material note", height=60, key="nut_matnote")

        # dwg non usato
        dwg_nut = ""

        if st.button("Generate Output", key="nut_gen"):
            materiale_nut = (
                mname_nut if mtype_nut == "MISCELLANEOUS"
                else f"{mtype_nut} {mprefix_nut} {mname_nut}".strip()
            )

            match_nut = materials_df[
                (materials_df["Material Type"] == mtype_nut) &
                (materials_df["Prefix"] == mprefix_nut) &
                (materials_df["Name"] == mname_nut)
            ]
            codice_fpd_nut = match_nut["FPD Code"].values[0] if not match_nut.empty else ""

            # Descrizione: Type -> Size -> Note -> Material -> Material note
            descr_parts_nut = ["HEX NUT", nut_type, size_nut, note_nut, materiale_nut, material_note_nut]
            descr_nut = "*" + " - ".join([p for p in descr_parts_nut if p])

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
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
        material_note = st.text_area("Material note", height=60, key="ring_matnote")

        if st.button("Generate Output", key="ring_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname

            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            # SQ logiche
            sq_tags = ["[SQ58]", "[CORP-ENG-0115]"]
            quality_lines = [
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]
            if clearance == "Yes":
                sq_tags.append("<SQ173>")
                quality_lines.append("SQ 173 - Increased Clearance for Wear Ring")

            tag_string = " ".join(sq_tags)
            quality = "\n".join(quality_lines)

            # Descrizione
            descr_parts = [f"{ring_type.upper()} WEAR RING"]
            for val in [model, int_diam, out_diam, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # COLONNA 3: DataLoad
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        # Materiale (Type -> Prefix -> Name)
        mtype_pin = st.selectbox("Material Type", [""] + material_types, key="pin_mtype")
        pref_df_pin = materials_df[
            (materials_df["Material Type"] == mtype_pin) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_pin = sorted(pref_df_pin["Prefix"].unique()) if mtype_pin != "MISCELLANEOUS" else []
        mprefix_pin = st.selectbox("Material Prefix", [""] + prefixes_pin, key="pin_mprefix")

        if mtype_pin == "MISCELLANEOUS":
            names_pin = materials_df[materials_df["Material Type"] == mtype_pin]["Name"].dropna().tolist()
        else:
            names_pin = materials_df[
                (materials_df["Material Type"] == mtype_pin) &
                (materials_df["Prefix"] == mprefix_pin)
            ]["Name"].dropna().tolist()
        mname_pin = st.selectbox("Material Name", [""] + names_pin, key="pin_mname")

        material_note_pin = st.text_area("Material note", height=60, key="pin_matnote")

        if st.button("Generate Output", key="pin_gen"):
            materiale_pin = (
                mname_pin if mtype_pin == "MISCELLANEOUS"
                else f"{mtype_pin} {mprefix_pin} {mname_pin}".strip()
            )

            match_pin = materials_df[
                (materials_df["Material Type"] == mtype_pin) &
                (materials_df["Prefix"] == mprefix_pin) &
                (materials_df["Name"] == mname_pin)
            ]
            codice_fpd_pin = match_pin["FPD Code"].values[0] if not match_pin.empty else ""

            # Diametro e lunghezza in un unico blocco con L=
            dim_block = f"{diameter_pin} - L={length_pin}"

            descr_parts_pin = [
                "DOWEL PIN",
                dim_block,
                note_pin,
                materiale_pin,
                material_note_pin
            ]
            descr_pin = "*" + " - ".join([p for p in descr_parts_pin if p])

            st.session_state["output_data"] = {
                "Item": "56200…",
                "Description": descr_pin,
                "Identificativo": "6550-DOWEL PIN",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_pin,
                "FPD material code": codice_fpd_pin,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
        )



# --- SHAFT, PUMP
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

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="shaft_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="shaft_size")

        # 🔧 RIMOSSO Additional Feature 1

        brg_type = st.selectbox("Brg. Type", [""] + brg_types, key="shaft_brg_type")
        brg_size = st.selectbox("Brg. Size", [""] + brg_size_options.get(brg_type, []), key="shaft_brg_size")

        max_diam = st.text_input("Max diameter (mm)", key="shaft_diam")
        max_len = st.text_input("Max length (mm)", key="shaft_len")
        dwg = st.text_input("Dwg/doc number", key="shaft_dwg")
        note = st.text_area("Note", height=80, key="shaft_note")

        mtype = st.selectbox("Material Type", [""] + material_types, key="shaft_mtype")
        pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="shaft_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix)
            ]["Name"].dropna().tolist()

        mname = st.selectbox("Material Name", [""] + names, key="shaft_mname")
        material_note = st.text_area("Material note", height=60, key="shaft_matnote")

        # Checkbox qualità
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="shaft_overlay")
        hvof = st.checkbox("HVOF coating?", key="shaft_hvof")
        water = st.checkbox("Water service?", key="shaft_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="shaft_stamicarbon")

        if st.button("Generate Output", key="shaft_gen"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""

            # Tag qualità
            sq_tags = ["[SQ60]", "[DE3513.014]", "[CORP-ENG-0115]", "[SQ58]"]
            quality_lines = [
                "SQ 60 - Procedura di Esecuzione del Run-Out per Alberi e Rotori di Pompe",
                "DE 3513.014 - Shaft Demagnetization",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1",
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche"
            ]
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

            descr_parts = ["SHAFT, PUMP"]
            for val in [model, size, brg_type, max_diam, max_len, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string

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


    # COLONNA 2: Output
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
            ident = "BASEPLATE"
            classe = ""
            cat = "FASCIA ITE 5"
            catalog = "BASE"
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        if st.button("Generate Output", key="flange_gen"):
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

        if st.button("Generate Output", key="gf_gen"):
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
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
            descr_cap = "*" + " - ".join([p for p in descr_parts_cap if p])

            st.session_state["output_data"] = {
                "Item": "56090…",
                "Description": descr_cap,
                "Identificativo": "6590-CAP SCREW",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_cap,
                "FPD material code": codice_fpd_cap,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }



    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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
            descr_grub = "*" + " - ".join([p for p in descr_parts_grub if p])

            st.session_state["output_data"] = {
                "Item": "56095…",
                "Description": descr_grub,
                "Identificativo": "6595-GRUB SCREW",
                "Classe ricambi": "",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": "",
                "Material": materiale_grub,
                "FPD material code": codice_fpd_grub,
                "Template": "FPD_BUY_2",
                "ERP_L1": "60_FASTENER",
                "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
                "To supplier": "",
                "Quality": ""
            }

    # --------------------- COLONNA 2: OUTPUT ---------------------
    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=160)
                else:
                    st.text_input(k, value=v)

    # --------------------- COLONNA 3: DATALOAD ---------------------
    with col3:
        render_dataload_panel(
            item_code_key="beye_item_code", 
            create_btn_key="gen_dl_beye",
            update_btn_key="gen_upd_beye"
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

    if "cast_generated" not in st.session_state:
        st.session_state.cast_generated = False

    # ─── COLONNA 1: INPUT ───
    with col_input:
        st.markdown("### 📥 Input")
        base_pattern     = st.text_input("Base pattern", key="cast_base_pattern")
        mod1             = st.text_input("Pattern modification 1", key="cast_mod1")
        mod2             = st.text_input("Pattern modification 2", key="cast_mod2")
        mod3             = st.text_input("Pattern modification 3", key="cast_mod3")
        mod4             = st.text_input("Pattern modification 4", key="cast_mod4")
        mod5             = st.text_input("Pattern modification 5", key="cast_mod5")
        note             = st.text_input("Note", key="cast_note")
        casting_drawing  = st.text_input("Casting drawing", key="cast_input_drawing")
        pattern_item     = st.text_input("Pattern item", key="cast_input_pattern")

        st.markdown("**Material selection**")
        material_type = st.selectbox("Material Type", [""] + material_types, key="cast_mat_type")

        prefixes = sorted(
            materials_df[materials_df["Material Type"] == material_type]["Prefix"]
            .dropna().unique().tolist()
        )
        prefix = st.selectbox("Prefix", [""] + prefixes, key="cast_prefix")

        names = materials_df[
            (materials_df["Material Type"] == material_type) &
            (materials_df["Prefix"] == prefix)
        ]["Name"].dropna().unique().tolist()
        name = st.selectbox("Name", [""] + names, key="cast_name")

        material_note = st.text_input("Material Note", key="cast_mat_note")

        hf_service_casting = False
        if selected_part != "Bearing housing casting":
            hf_service_casting = st.checkbox(
                "Is it an hydrofluoric acid alkylation service (lethal)?",
                key="cast_hf"
            )

        if st.button("Generate Output", key="cast_gen"):
            st.session_state.cast_generated = True

    # ─── COLONNA 2: OUTPUT ───
    if st.session_state.cast_generated:
        with col_output:
            st.markdown("### 📤 Output")

            casting_code      = "XX"
            fpd_material_code = "NA"
            if material_type and prefix and name:
                dfm = materials_df[
                    (materials_df["Material Type"] == material_type) &
                    (materials_df["Prefix"] == prefix) &
                    (materials_df["Name"] == name)
                ]
                if not dfm.empty:
                    raw = str(dfm["Casting code"].values[0])
                    casting_code = raw[-2:] if len(raw) >= 2 else raw
                    fpd_material_code = dfm["FPD Code"].values[0]

            item_number   = "7" + casting_code
            pattern_parts = [m for m in [mod1, mod2, mod3, mod4, mod5] if m.strip()]
            pattern_full  = "/".join(pattern_parts)

            parts = [f"*{identificativo.upper()}"]
            if base_pattern:
                parts.append(f"BASE PATTERN: {base_pattern}")
            if pattern_full:
                parts.append(f"MODS: {pattern_full}")
            if note:
                parts.append(note)
            parts.append(f"{prefix} {name}".strip())
            if material_note:
                parts.append(material_note)

            qual_tags = ["[SQ58]", "[CORP-ENG-0115]", "[DE2390.002]"]
            if hf_service_casting:
                qual_tags.append("<SQ113>")
            if selected_part == "Impeller casting":
                qual_tags.append("[DE2920.025]")

            base_description = ", ".join(parts)
            description = base_description + " " + " ".join(qual_tags)

            quality_lines = [
                "DE 2390.002 - Procurement and Quality Specification for Ferrous Castings",
                "SQ 58 - Controllo Visivo e Dimensionale delle Lavorazioni Meccaniche",
                "CORP-ENG-0115 - General Surface Quality Requirements G1-1"
            ]
            if hf_service_casting:
                quality_lines.append("SQ 113 - Material Requirements for Pumps in Hydrofluoric Acid Service (HF)")
            if selected_part == "Impeller casting":
                quality_lines.append("DE2920.025 - Impellers' Allowable Tip Speed and Related N.D.E.")
            quality_field = "\n".join(quality_lines)

            st.text_input("Item", value=item_number, key="cast_out_item")
            st.text_area("Description", value=description, height=100, key="cast_out_desc")
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
            st.text_area("Quality", value=quality_field, height=100, key="cast_out_quality")

    # ─── COLONNA 3: DATALOAD ───
    with col_dataload:
        st.markdown("### 🧾 DataLoad")
        mode = st.radio("Operation type:", ["Create new item", "Update item"], key="cast_mode")
        item_code_dl = st.text_input("Item code", key="cast_dl_code")

        if mode == "Create new item":
            if st.button("Generate DataLoad string", key="cast_dl_create"):
                if not item_code_dl:
                    st.error("❌ Please enter the item code first.")
                else:
                    st.success("✅ DataLoad string successfully generated. Download the CSV file below.")
        else:
            if st.button("Generate Update string", key="cast_dl_update"):
                if not item_code_dl:
                    st.error("❌ Please enter the item code first.")
                else:
                    st.success("✅ Update string successfully generated. Download the CSV file below.")


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
