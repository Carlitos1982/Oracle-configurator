
import streamlit as st

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

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
    "Gasket, Spiral Wound"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# === GASKET LOGIC ===
if selected_part == "Gasket, Spiral Wound":
    st.subheader("Configurazione - Gasket, Spiral Wound")

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

    winding = st.selectbox("Winding material", list(winding_colors.keys()))
    filler = st.selectbox("Filler", list(filler_colors.keys()))
    inner_dia = st.number_input("Diametro interno (mm)", min_value=0.0, step=0.1, format="%.1f")
    outer_dia = st.number_input("Diametro esterno (mm)", min_value=0.0, step=0.1, format="%.1f")
    thickness = st.number_input("Spessore (mm)", min_value=0.0, step=0.1, format="%.1f")
    rating = st.selectbox("Rating", list(rating_stripes.keys()))
    dwg = st.text_input("Dwg/doc number")
    note = st.text_area("Note (opzionale)", height=80)

    if st.button("Genera Output"):
        color_code_1 = winding_colors.get(winding, "")
        color_code_2 = filler_colors.get(filler, "")
        stripe = rating_stripes.get(rating, "")

        descrizione = (
            f"GASKET, SPIRAL WOUND - WINDING: {winding}, FILLER: {filler}, "
            f"ID: {inner_dia}mm, OD: {outer_dia}mm, THK: {thickness}mm, "
            f"RATING: {rating}, COLOR CODE: {color_code_1}/{color_code_2}, {stripe}"
        )

        if note:
            descrizione += f", NOTE: {note}"

        st.session_state["output_data"] = {
            "Item": "50415…",
            "Description": descrizione,
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

# === OUTPUT ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100)
        else:
            st.text_input(campo, value=valore)
