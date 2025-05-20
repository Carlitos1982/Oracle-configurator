
import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
st.title("Oracle Item Setup - Web App")

# Caricamento dati Excel
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
size_df      = data["size_df"]
features_df  = data["features_df"]
materials_df = data["materials_df"]

# Lista delle parti
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
    "Bolt, Hexagonal"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# Dati comuni
pump_models    = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

# Funzione generica per le parti a catalog
def genera_output(parte, item, identificativo, classe, catalog, erp_l2,
                  template_fisso=None, extra_fields=None):
    model = st.selectbox("Product/Pump Model", [""] + pump_models, key=f"model_{parte}")
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list, key=f"size_{parte}")

    # Additional Feature 1
    feature_1 = ""
    special = ["HDO", "DMX", "WXB", "WIK"]
    if not (model in special and parte != "casing"):
        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key=f"f1_{parte}")

    # Additional Feature 2
    feature_2 = ""
    if (model == "HPX" and parte == "casing") or model == "HED":
        f2_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features2")
        ]["Feature"].dropna().tolist()
        feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key=f"f2_{parte}")

    # Campi extra (diameters, baseplate, shaft)
    extra_descr = ""
    if extra_fields == "diameters":
        int_dia = st.number_input("Diametro interno (mm)", min_value=0, step=1, format="%d", key=f"int_dia_{parte}")
        ext_dia = st.number_input("Diametro esterno (mm)", min_value=0, step=1, format="%d", key=f"ext_dia_{parte}")
        extra_descr = f"int. dia.: {int(int_dia)}mm ext. dia.: {int(ext_dia)}mm"
    elif extra_fields == "baseplate":
        length = st.number_input("Length (mm)", min_value=0, step=1, format="%d", key=f"len_{parte}")
        width  = st.number_input("Width (mm)", min_value=0, step=1, format="%d", key=f"wid_{parte}")
        weight = st.number_input("Weight (kg)", min_value=0, step=1, format="%d", key=f"wgt_{parte}")
        sourcing = st.selectbox("Sourcing", ["Europe", "India", "China"], key=f"sourcing_{parte}")
        extra_descr = f"Length: {length}mm Width: {width}mm Weight: {weight}kg Sourcing: {sourcing}"
    elif extra_fields == "shaft":
        brg_type = st.text_input("Brg. type", key=f"brg_type_{parte}")
        brg_size = st.text_input("Brg. size", key=f"brg_size_{parte}")
        max_dia  = st.number_input("Max diameter (mm)", min_value=0, step=1, format="%d", key=f"max_dia_{parte}")
        max_len  = st.number_input("Max length (mm)", min_value=0, step=1, format="%d", key=f"max_len_{parte}")
        extra_descr = (
            f"Brg. type: {brg_type} Brg. size: {brg_size} "
            f"Max dia: {int(max_dia)}mm Max len: {int(max_len)}mm"
        )

    note = st.text_area("Note (opzionale)", height=80, key=f"note_{parte}")
    dwg  = st.text_input("Dwg/doc number", key=f"dwg_{parte}")

    # Scelta del template
    if parte == "cover" and model in ["HPX", "PVML"]:
        mob = st.radio("Make or Buy", ["Make", "Buy"], horizontal=True, key=f"mob_{parte}")
        template = "FPD_MAKE" if mob == "Make" else "FPD_BUY_1"
    elif parte == "cover":
        template = "FPD_MAKE"
    elif parte in ["balance", "drum", "disc"]:
        template = "FPD_BUY_1"
    elif parte == "baseplate":
        template = "FPD_BUY_4"
    else:
        template = template_fisso

    # Selezione materiale
    mtype = st.selectbox("Material Type", [""] + material_types, key=f"mtype_{parte}")
    pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefixes, key=f"mprefix_{parte}")
    if mtype == "MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        names = materials_df[
            (materials_df["Material Type"] == mtype) &
            (materials_df["Prefix"] == mprefix)
        ]["Name"].dropna().tolist()
    mname = st.selectbox("Material Name", [""] + names, key=f"mname_{parte}")

    if st.button("Genera Output", key=f"gen_{parte}"):
        # Costruzione Material / FPD code
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

        descrizione = f"{selected_part} " + " ".join(
            filter(None, [model, size, feature_1, feature_2, extra_descr, note, materiale])
        )

        st.session_state["output_data"] = {
            "Item": item,
            "Description": descrizione,
            "Identificativo": identificativo,
            "Classe ricambi": classe,
            "Categories": "FASCIA ITE 5" if parte == "baseplate" else "FASCIA ITE 4",
            "Catalog": catalog,
            "Disegno": dwg,
            "Material": materiale,
            "FPD material code": codice_fpd,
            "Template": template,
            "ERP_L1": "21_FABRICATIONS_OR_BASEPLATES" if parte == "baseplate" else "20_TURNKEY_MACHINING",
            "ERP_L2": erp_l2,
            "To supplier": "", "Quality": ""
        }

# Sezione Bolt, Eye
elif selected_part == "Bolt, Eye":
    st.subheader("Configurazione - Bolt, Eye")
    thread = st.selectbox("Thread type/size", [
        "#10-24UNC", "5/16\"-18UNC", # ... e le altre
    ], key="bolt_thread")
    length = st.selectbox("Length", ["1/8\"in", "1/4\"in", # ... e le altre
    ], key="bolt_length")
    note1 = st.text_area("Note (opzionale)", height=80, key="bolt_note1")
    mtype_bolt = st.selectbox("Material Type", [""] + material_types, key="mtype_bolt")
    # ... selezione prefisso e nome
    material_note = st.text_area("Material Note (opzionale)", height=80, key="bolt_note2")
    if st.button("Genera Output", key="gen_bolt"):
        # ... costruzione descrizione e output
        st.session_state["output_data"] = {
            "Item": "50150…",
            "Description": # ...,
            "Identificativo": "6583-EYE BOLT",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "", "Material": materiale_bolt,
            "FPD material code": codice_fpd_bolt,
            "Template": "FPD_BUY_2",
            "ERP_L1": "60_FASTENER",
            "ERP_L2": "74_OTHER_FASTENING_COMPONENTS_EYE_NUTS_LOCK_NUTS_ETC"
        }

# Sezione Bolt, Hexagonal
elif selected_part == "Bolt, Hexagonal":
    st.subheader("Configurazione - Bolt, Hexagonal")
    size_hex = st.selectbox("Size", ["#10-24UNC", "5/16\"-18UNC", # ...], key="hex_size")
    length_hex = st.selectbox("Length", ["1/8\"in","1/4\"in", # ...], key="hex_length")
    full_threaded = st.radio("Full threaded?", ["Yes","No"], horizontal=True, key="hex_full_threaded")
    note_hex = st.text_area("Note (opzionale)", height=80, key="hex_note1")
    mtype_hex = st.selectbox("Material Type", [""] + material_types, key="hex_mtype")
    # ... selezione prefisso e nome
    zinc_plated = st.radio("Zinc Plated?", ["Yes","No"], horizontal=True, key="hex_zinc")
    material_note_hex = st.text_area("Material Note (opzionale)", height=80, key="hex_material_note")
    if st.button("Genera Output", key="gen_hex"):
        # ... costruzione descrizione dinamica
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
            "ERP_L2": "10_STANDARD_BOLT_NUT_STUD_SCREW_WASHER"
        }

# Output finale
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100)
        else:
            st.text_input(campo, value=valore)

# FINE
