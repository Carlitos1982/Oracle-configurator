import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    return {
        "size_df": pd.read_excel(xls, sheet_name="Pump Size"),
        "features_df": pd.read_excel(xls, sheet_name="Features"),
        "materials_df": pd.read_excel(xls, sheet_name="Materials")
    }

data = load_config_data()
size_df = data["size_df"]
features_df = data["features_df"]
materials_df = data["materials_df"]

def copy_to_clipboard_button(value):
    st.text_input("Output", value=value, key=value)
    st.markdown("---")

# === BASEPLATE ===
def genera_output_baseplate():
    st.header("Baseplate, Pump")
    model = st.text_input("Pump model")
    size = st.text_input("Pump size")
    dimensions = st.text_input("Dimensions")
    weight = st.text_input("Weight (kg)")
    drawing = st.text_input("Drawing")
    note = st.text_area("Note (optional)")
    material = st.selectbox("Material", materials_df["Material"].unique())

    description = f"BASEPLATE FOR PUMP MODEL {model} SIZE {size}, DIMENSIONS {dimensions}, WEIGHT {weight}kg"
    if note:
        description += f" - {note}"

    output = {
        "Item": "30331…",
        "Description": description,
        "Identificativo": "3110-BASEPLATE",
        "Classe ricambi": "2-3",
        "Categories": "FASCIA ITE 4",
        "Catalog": "BASE",
        "Template": "FPD_BUY_4",
        "ERP_L1": "24_STRUCTURE",
        "ERP_L2": "20_BASEPLATE",
        "Disegno": drawing,
        "Material": material,
        "FPD material code": "NOT AVAILABLE"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === IMPELLER ===
def genera_output_impeller():
    st.header("Impeller, Pump")
    model = st.text_input("Pump model")
    size = st.text_input("Pump size")
    trim = st.text_input("Impeller trim")
    drawing = st.text_input("Drawing")
    material = st.selectbox("Material", materials_df["Material"].unique())

    description = f"IMPELLER FOR MODEL {model} SIZE {size}, TRIM {trim}"

    output = {
        "Item": "20111…",
        "Description": description,
        "Identificativo": "1100-IMPELLER",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 1",
        "Catalog": "IDRAULICA",
        "Template": "FPD_MAKE",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "10_IMPELLERS",
        "Disegno": drawing,
        "Material": material,
        "FPD material code": "NOT AVAILABLE"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === CASING ===
def genera_output_casing():
    st.header("Casing, Pump")
    model = st.text_input("Pump model")
    size = st.text_input("Pump size")
    pressure = st.text_input("Max pressure (bar)")
    drawing = st.text_input("Drawing")
    material = st.selectbox("Material", materials_df["Material"].unique())

    description = f"PUMP CASING FOR MODEL {model} SIZE {size}, PRESSURE {pressure} bar"

    output = {
        "Item": "10101…",
        "Description": description,
        "Identificativo": "1000-CASING",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 1",
        "Catalog": "IDRAULICA",
        "Template": "FPD_MAKE",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "05_CASING",
        "Disegno": drawing,
        "Material": material,
        "FPD material code": "NOT AVAILABLE"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === CASING COVER ===
def genera_output_casing_cover():
    st.header("Casing Cover, Pump")
    model = st.text_input("Pump model")
    size = st.text_input("Pump size")
    type_cover = st.text_input("Cover type")
    drawing = st.text_input("Drawing")
    material = st.selectbox("Material", materials_df["Material"].unique())

    description = f"COVER FOR PUMP MODEL {model} SIZE {size}, TYPE {type_cover}"

    output = {
        "Item": "10105…",
        "Description": description,
        "Identificativo": "1005-CASING COVER",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 1",
        "Catalog": "IDRAULICA",
        "Template": "FPD_MAKE",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "06_COVER",
        "Disegno": drawing,
        "Material": material,
        "FPD material code": "NOT AVAILABLE"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === BALANCE BUSHING ===
def genera_output_balance_bushing():
    st.header("Balance Bushing, Pump")
    description = "BALANCE BUSHING FOR PUMP"
    output = {
        "Item": "6231…",
        "Description": description,
        "Identificativo": "6231-BALANCE DRUM BUSH",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 3",
        "Catalog": "ALBERO",
        "Template": "FPD_BUY_1",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "16_BUSHING",
        "Disegno": "",
        "Material": "NOT AVAILABLE",
        "FPD material code": "NA"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === BALANCE DRUM ===
def genera_output_balance_drum():
    st.header("Balance Drum, Pump")
    description = "BALANCE DRUM FOR PUMP"
    output = {
        "Item": "6232…",
        "Description": description,
        "Identificativo": "6232-BALANCE DRUM",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 3",
        "Catalog": "ALBERO",
        "Template": "FPD_BUY_1",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "16_BUSHING",
        "Disegno": "",
        "Material": "NOT AVAILABLE",
        "FPD material code": "NA"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === BALANCE DISC ===
def genera_output_balance_disc():
    st.header("Balance Disc, Pump")
    description = "BALANCE DISC FOR PUMP"
    output = {
        "Item": "6210…",
        "Description": description,
        "Identificativo": "6210-BALANCE DISC",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 3",
        "Catalog": "ARTVARI",
        "Template": "FPD_BUY_1",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "30_DISK",
        "Disegno": "",
        "Material": "NOT AVAILABLE",
        "FPD material code": "NA"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))
# === FLANGE ===
def genera_output_flange():
    st.header("Flange, Pipe")
    pipe_type = st.selectbox("Pipe type", ["SW", "WN"])
    size = st.selectbox("Size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    face_type = st.selectbox("Face type", ["RF", "FF", "RJ"])
    class_rating = st.text_input("Class (e.g. 150 Sch)")
    material = st.text_input("Material (e.g. A106-GR.B)")
    additional_features = st.text_input("Additional features (optional)")

    description = f"FLANGE {pipe_type}, SIZE {size}, FACE {face_type}, CLASS {class_rating}, MATERIAL {material}"
    if additional_features:
        description += f", FEATURES {additional_features}"

    output = {
        "Item": "50155…",
        "Description": description,
        "Identificativo": "1245-FLANGE",
        "Classe ricambi": "",
        "Categories": "FASCIA ITE 5",
        "Catalog": "",
        "Disegno": "",
        "Material": "NOT AVAILABLE",
        "FPD material code": "NA",
        "Template": "FPD_BUY_2",
        "ERP_L1": "23_FLANGE",
        "ERP_L2": "13_OTHER"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === SHAFT ===
def genera_output_shaft():
    st.header("Shaft, Pump")
    model = st.text_input("Product pump model")
    size = st.text_input("Product pump size")
    feature1 = st.text_input("Additional features 1")
    feature2 = st.text_input("Additional features 2")
    brg_type = st.text_input("Brg. type")
    brg_size = st.text_input("Brg. size")
    max_diam = st.text_input("Max diameter (mm)")
    max_len = st.text_input("Max length (mm)")
    drawing = st.text_input("DWG/doc")
    note = st.text_area("Note (optional)")
    material = st.selectbox("Material", materials_df["Material"].unique())

    description = f"SHAFT FOR PUMP MODEL {model} SIZE {size}, FEATURES {feature1}/{feature2}, BRG {brg_type} {brg_size}, Ø{max_diam}x{max_len}mm"
    if note:
        description += f" - {note}"

    output = {
        "Item": "40231…",
        "Description": description,
        "Identificativo": "2100-SHAFT",
        "Classe ricambi": "2-3",
        "Categories": "Fascia ite 4",
        "Catalog": "ALBERO",
        "Template": "FPD_MAKE",
        "ERP_L1": "20_TURNKEY_MACHINING",
        "ERP_L2": "25_SHAFTS",
        "Disegno": drawing,
        "Material": material,
        "FPD material code": "NOT AVAILABLE"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === GASKET ===
def genera_output_gasket():
    st.header("Gasket, Spiral Wound")
    style = st.text_input("Style")
    size = st.text_input("Size")
    rating = st.text_input("Rating")
    winding = st.selectbox("Winding material", [
        "SS316L-GREEN RAL6005",
        "SS304L-YELLOW RAL1004",
        "MONEL-ORANGE RAL2000",
        "TITANIUM-LIGHT BLUE RAL5012"
    ])
    filler = st.selectbox("Filler material", [
        "GRAPHITE-GRAY RAL7024",
        "PTFE-WHITE RAL9003"
    ])
    inner_ring = st.selectbox("Inner ring", ["YES", "NO"])
    outer_ring = st.selectbox("Outer ring", ["YES", "NO"])
    drawing = st.text_input("Drawing")
    note = st.text_area("Note (optional)")

    color_code_1 = winding.split("-")[-1]
    color_code_2 = filler.split("-")[-1]

    description = f"GASKET SPIRAL WOUND, STYLE {style}, SIZE {size}, RATING {rating}, WINDING {winding}, FILLER {filler}, INNER RING {inner_ring}, OUTER RING {outer_ring}, COLOR CODE 1: {color_code_1}, COLOR CODE 2: {color_code_2}"
    if rating:
        if rating.startswith("150"):
            description += " (ASME B16.20)"
        elif rating.startswith("300"):
            description += " (ASME B16.47 SER. A)"
        elif rating.startswith("600"):
            description += " (ASME B16.5)"
        elif rating.startswith("900"):
            description += " (ASME B16.47 SER. B)"
    if note:
        description += f" - {note}"

    output = {
        "Item": "50415…",
        "Description": description,
        "Identificativo": "4510-JOINT",
        "Classe ricambi": "1-2-3",
        "Categories": "FASCIA ITE 5",
        "Catalog": "ARTVARI",
        "Disegno": drawing,
        "Material": "NA",
        "FPD material code": "NOT AVAILABLE",
        "Template": "FPD_BUY_1",
        "ERP L1": "55_GASKETS_OR_SEAL",
        "ERP L2": "16_SPIRAL_WOUND"
    }

    for k, v in output.items():
        st.write(f"**{k}**: {v}")
        copy_to_clipboard_button(str(v))

# === SELEZIONE PARTE ===
part_options = [
    "Baseplate, Pump",
    "Casing, Pump",
    "Casing Cover, Pump",
    "Impeller, Pump",
    "Balance Bushing, Pump",
    "Balance Drum, Pump",
    "Balance Disc, Pump",
    "Flange, Pipe",
    "Shaft, Pump",
    "Gasket, Spiral Wound"
]

selected_part = st.selectbox("Seleziona la parte da configurare", part_options)

if selected_part == "Baseplate, Pump":
    genera_output_baseplate()
elif selected_part == "Casing, Pump":
    genera_output_casing()
elif selected_part == "Casing Cover, Pump":
    genera_output_casing_cover()
elif selected_part == "Impeller, Pump":
    genera_output_impeller()
elif selected_part == "Balance Bushing, Pump":
    genera_output_balance_bushing()
elif selected_part == "Balance Drum, Pump":
    genera_output_balance_drum()
elif selected_part == "Balance Disc, Pump":
    genera_output_balance_disc()
elif selected_part == "Flange, Pipe":
    genera_output_flange()
elif selected_part == "Shaft, Pump":
    genera_output_shaft()
elif selected_part == "Gasket, Spiral Wound":
    genera_output_gasket()
