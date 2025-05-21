==#=import streamlit as st
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
size_df = data["size_df"]
features_df = data["features_df"]
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
    "Bolt, Hexagonal",
    "Gasket, Ring Type Joint",
    "Gusset, Other",
    "Nut, Hex",
    "Stud, Threaded",
    "Ring, Wear"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# Dati comuni
pump_models = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

# Funzione generica
def genera_output(parte, item, identificativo, classe, catalog, erp_l2, template_fisso=None, extra_fields=None):
    model = st.selectbox("Product/Pump Model", [""] + pump_models, key=f"model_{parte}")
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list, key=f"size_{parte}")

    feature_1 = ""
    special = ["HDO", "DMX", "WXB", "WIK"]
    if not (model in special and parte != "casing"):
        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key=f"f1_{parte}")

    feature_2 = ""
    if (model == "HPX" and parte == "casing") or model == "HED":
        f2_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features2")
        ]["Feature"].dropna().tolist()
        feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key=f"f2_{parte}")

    extra_descr = ""
    if extra_fields == "diameters":
        int_dia = st.number_input("Diametro interno (mm)", min_value=0, step=1, format="%d", key=f"int_dia_{parte}")
        ext_dia = st.number_input("Diametro esterno (mm)", min_value=0, step=1, format="%d", key=f"ext_dia_{parte}")
        extra_descr = f"int. dia.: {int(int_dia)}mm ext. dia.: {int(ext_dia)}mm"
    elif extra_fields == "baseplate":
        length = st.number_input("Length (mm)", min_value=0, step=1, format="%d", key=f"len_{parte}")
        width = st.number_input("Width (mm)", min_value=0, step=1, format="%d", key=f"wid_{parte}")
        weight = st.number_input("Weight (kg)", min_value=0, step=1, format="%d", key=f"wgt_{parte}")
        sourcing = st.selectbox("Sourcing", ["Europe", "India", "China"], key=f"sourcing_{parte}")
        extra_descr = f"Length: {length}mm Width: {width}mm Weight: {weight}kg Sourcing: {sourcing}"
    elif extra_fields == "shaft":
        brg_type = st.text_input("Brg. type", key=f"brg_type_{parte}")
        brg_size = st.text_input("Brg. size", key=f"brg_size_{parte}")
        max_dia = st.number_input("Max diameter (mm)", min_value=0, step=1, format="%d", key=f"max_dia_{parte}")
        max_len = st.number_input("Max length (mm)", min_value=0, step=1, format="%d", key=f"max_len_{parte}")
        extra_descr = f"Brg. type: {brg_type} Brg. size: {brg_size} Max dia: {int(max_dia)}mm Max len: {int(max_len)}mm"

    note = st.text_area("Note (opzionale)", height=80, key=f"note_{parte}")
    dwg = st.text_input("Dwg/doc number", key=f"dwg_{parte}")

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

    mtype = st.selectbox("Material Type", [""] + material_types, key=f"mtype_{parte}")
    pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefixes, key=f"mprefix_{parte}")
    if mtype == "MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().drop_duplicates().tolist()
    else:
        names = materials_df[
            (materials_df["Material Type"] == mtype) &
            (materials_df["Prefix"] == mprefix)
        ]["Name"].dropna().drop_duplicates().tolist()
    mname = st.selectbox("Material Name", [""] + names, key=f"mname_{parte}")

    if st.button("Genera Output", key=f"gen_{parte}"):
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
            "To supplier": "",
            "Quality": ""
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
            
    # --- ROUTING DELLE PARTI --- #

if selected_part == "Baseplate, Pump":
    st.subheader("Configurazione - Baseplate, Pump")
    genera_output("baseplate", "477…", "6110-BASE PLATE", "", "ARTVARI", "18_FOUNDATION_PLATE", extra_fields="baseplate")

elif selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")
    genera_output("casing", "40202…", "1100-CASING", "3", "CORPO", "17_CASING", template_fisso="FPD_MAKE")

elif selected_part == "Casing Cover, Pump":
    st.subheader("Configurazione - Casing Cover, Pump")
    genera_output("cover", "40205…", "1221-CASING COVER", "3", "COPERCHIO", "13_OTHER")

elif selected_part == "Impeller, Pump":
    st.subheader("Configurazione - Impeller, Pump")
    genera_output("imp", "40229…", "2200-IMPELLER", "2-3", "GIRANTE", "20_IMPELLER_DIFFUSER", template_fisso="FPD_MAKE")

elif selected_part == "Balance Bushing, Pump":
    st.subheader("Configurazione - Balance Bushing, Pump")
    genera_output("balance", "40226…", "6231-BALANCE DRUM BUSH", "1-2-3", "ALBERO", "16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Drum, Pump":
    st.subheader("Configurazione - Balance Drum, Pump")
    genera_output("drum", "40227…", "6231-BALANCE DRUM BUSH", "1-2-3", "ARTVARI", "16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Disc, Pump":
    st.subheader("Configurazione - Balance Disc, Pump")
    genera_output("disc", "40228…", "6210-BALANCE DISC", "1-2-3", "ARTVARI", "30_DISK", extra_fields="diameters")

elif selected_part == "Shaft, Pump":
    st.subheader("Configurazione - Shaft, Pump")
    genera_output("shaft", "40231…", "2100-SHAFT", "2-3", "ALBERO", "25_SHAFTS", template_fisso="FPD_MAKE", extra_fields="shaft")

# Qui puoi continuare aggiungendo i blocchi personalizzati come:
# - Flange, Pipe
# - Gate, Valve
# - Gasket, Spiral Wound
# - Gasket, Flat
# - Bearing, Rolling
# - Bearing, Hydrostatic/Hydrodynamic
# - Bolt, Eye
# - Bolt, Hexagonal
# - Gasket, Ring Type Joint
# - Gusset, Other
# - Nut, Hex
# - Stud, Threaded
# - Ring, Wear

# Se vuoi, posso continuare incollando direttamente anche tutti questi.

elif selected_part == "Flange, Pipe":
    st.subheader("Configurazione - Flange, Pipe")
    pipe_type = st.selectbox("Pipe type", ["SW", "WN"])
    size = st.selectbox("Size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    face_type = st.selectbox("Face type", ["RF", "FF", "RJ"])
    flange_class = st.selectbox("Class", ["150", "300", "600", "1500", "2500"])
    schedule = st.selectbox("Schedule", ["5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160"])
    material = st.text_input("Material")
    features = st.text_area("Additional features (opzionale)", height=80)
    if st.button("Genera Output", key="gen_flange_pipe"):
        descr = (
            f"FLANGE, PIPE - TYPE: {pipe_type}, SIZE: {size}, "
            f"FACE TYPE: {face_type}, CLASS: {flange_class}, SCHEDULE: {schedule}, MATERIAL: {material}"
        )
        if features:
            descr += f", NOTE: {features}"
        st.session_state["output_data"] = {
            "Item": "50155…",
            "Description": descr,
            "Identificativo": "1245-FLANGE",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": "NOT AVAILABLE",
            "FPD material code": "NA",
            "Template": "FPD_BUY_2",
            "ERP_L1": "23_FLANGE",
            "ERP_L2": "13_OTHER",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Gate, Valve":
    st.subheader("Configurazione - Gate, Valve")
    size = st.selectbox("Size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    pressure_class = st.selectbox("Pressure class", ["150", "300", "600", "1500", "2500"])
    inlet_size = st.selectbox("Inlet connection size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    inlet_type = st.selectbox("Inlet connection type", ["SW", "WN"])
    outlet_size = st.selectbox("Outlet connection size", ['1/8”', '1/4”', '3/8”', '1/2”', '3/4”', '1”', '1-1/4”', '1-1/2”', '2”', '2-1/2”', '3”', '4”'])
    outlet_type = st.selectbox("Outlet connection type", ["SW", "WN"])
    material = st.selectbox("Valve material", [
        "A105", "A106-GR B", "UNS-S31803", "UNS-S32760", "A350 LF2", "A182-F316L",
        "ALLOY 825", "GALVANIZED CARBON STEEL"
    ])
    schedule = st.selectbox("Schedule", ["5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160"])
    note = st.text_area("Note (opzionale)", height=80)
    if st.button("Genera Output", key="gen_gate_valve"):
        descr = (
            f"GATE, VALVE - SIZE: {size}, CLASS: {pressure_class}, "
            f"INLET: {inlet_type} {inlet_size}, OUTLET: {outlet_type} {outlet_size}, "
            f"MATERIAL: {material}, SCHEDULE: {schedule}"
        )
        if note:
            descr += f", NOTE: {note}"
        st.session_state["output_data"] = {
            "Item": "50186…",
            "Description": descr,
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
        
        elif selected_part == "Gasket, Spiral Wound":
    st.subheader("Configurazione - Gasket, Spiral Wound")

    winding = st.text_input("Winding material")
    filler = st.text_input("Filler")
    inner_dia = st.number_input("Diametro interno (mm)", min_value=0.0, step=0.1, format="%.1f")
    outer_dia = st.number_input("Diametro esterno (mm)", min_value=0.0, step=0.1, format="%.1f")
    thickness = st.number_input("Spessore (mm)", min_value=0.0, step=0.1, format="%.1f")
    rating = st.text_input("Rating")
    color_code_1 = st.text_input("COLOR CODE 1 (winding)")
    color_code_2 = st.text_input("COLOR CODE 2 (filler)")
    dwg = st.text_input("Disegno")
    note = st.text_area("Note (opzionale)", height=80)

    if st.button("Genera Output", key="gen_gasket_spiral"):
        descr = (
            f"GASKET, SPIRAL WOUND - WINDING: {winding}, FILLER: {filler}, "
            f"ID: {inner_dia}mm, OD: {outer_dia}mm, THK: {thickness}mm, "
            f"RATING: {rating}, COLOR CODE 1: {color_code_1}, COLOR CODE 2: {color_code_2}"
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

elif selected_part == "Gasket, Flat":
    st.subheader("Configurazione - Gasket, Flat")

    thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f")
    uom = st.selectbox("Unità di misura", ["mm", "inches"])
    dwg = st.text_input("Disegno")
    material = st.text_input("Materiale")
    note = st.text_area("Note (opzionale)", height=80)

    if st.button("Genera Output", key="gen_gasket_flat"):
        descr = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {material}"
        if note:
            descr += f", NOTE: {note}"

        st.session_state["output_data"] = {
            "Item": "50158…",
            "Description": descr,
            "Identificativo": "4590-GASKET",
            "Classe ricambi": "1-2-3",
            "Categories": "FASCIA ITE 5",
            "Catalog": "ARTVARI",
            "Disegno": dwg,
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_2",
            "ERP_L1": "55_GASKETS_OR_SEAL",
            "ERP_L2": "20_OTHER",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Gasket, Ring Type Joint":
    st.subheader("Configurazione - Gasket, Ring Type Joint")

    rtj_type = st.selectbox("Type", ["Oval", "Octagonal"])
    rtj_size = st.selectbox("Size", [f"R{i}" for i in range(11, 61)])
    note = st.text_area("Note (opzionale)", height=80)
    material = st.text_input("Material")
    material_note = st.text_area("Material Note (opzionale)", height=80)

    if st.button("Genera Output", key="gen_gasket_rtj"):
        descr = f"GASKET, RING TYPE JOINT - TYPE: {rtj_type}, SIZE: {rtj_size}"
        if note:
            descr += f", {note}"
        descr += f", {material}"
        if material_note:
            descr += f", {material_note}"

        st.session_state["output_data"] = {
            "Item": "50158…",
            "Description": descr,
            "Identificativo": "ANELLO SFERICO RING JOINT",
            "Classe ricambi": "1-2-3",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_2",
            "ERP_L1": "55_GASKETS_OR_SEAL",
            "ERP_L2": "20_OTHER",
            "Disegno": "",
            "To supplier": "",
            "Quality": ""
        }
        
        
        elif selected_part == "Bolt, Eye":
    st.subheader("Configurazione - Bolt, Eye")
    thread = st.text_input("Thread type/size")
    length = st.text_input("Length")
    note1 = st.text_area("Note (opzionale)", height=80)
    material = st.text_input("Material")
    material_note = st.text_area("Material Note (opzionale)", height=80)
    if st.button("Genera Output", key="gen_bolt_eye"):
        descr = f"BOLT, EYE - THREAD: {thread}, LENGTH: {length}"
        if note1:
            descr += f", {note1}"
        descr += f", {material}"
        if material_note:
            descr += f", {material_note}"
        st.session_state["output_data"] = {
            "Item": "50150…",
            "Description": descr,
            "Identificativo": "6583-EYE BOLT",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_2",
            "ERP_L1": "60_FASTENER",
            "ERP_L2": "74_OTHER_FASTENING_COMPONENTS_EYE_NUTS_LOCK_NUTS_ETC",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Bolt, Hexagonal":
    st.subheader("Configurazione - Bolt, Hexagonal")
    size = st.text_input("Size")
    length = st.text_input("Length")
    full_thd = st.radio("Full threaded?", ["Yes", "No"], horizontal=True)
    zinc = st.radio("Zinc plated?", ["Yes", "No"], horizontal=True)
    note1 = st.text_area("Note (opzionale)", height=80)
    material = st.text_input("Material")
    note2 = st.text_area("Material Note (opzionale)", height=80)
    if st.button("Genera Output", key="gen_bolt_hex"):
        descr = f"BOLT, HEXAGONAL - SIZE: {size}, LENGTH: {length}"
        if full_thd == "Yes":
            descr += ", FULL THREADED"
        if zinc == "Yes":
            descr += ", ZINC PLATED AS PER ASTM B633"
        if note1:
            descr += f", {note1}"
        descr += f", {material}"
        if note2:
            descr += f", {note2}"
        st.session_state["output_data"] = {
            "Item": "56230…",
            "Description": descr,
            "Identificativo": "6577-HEXAGON HEAD BOLT",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_2",
            "ERP_L1": "60_FASTENER",
            "ERP_L2": "10_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Nut, Hex":
    st.subheader("Configurazione - Nut, Hex")
    size = st.text_input("Size")
    note1 = st.text_area("Note (opzionale)", height=80)
    material = st.text_input("Material")
    note2 = st.text_area("Material Note (opzionale)", height=80)
    if st.button("Genera Output", key="gen_nut_hex"):
        descr = f"NUT, HEX - TYPE: Heavy, SIZE: {size}"
        if note1:
            descr += f", {note1}"
        descr += f", {material}"
        if note2:
            descr += f", {note2}"
        st.session_state["output_data"] = {
            "Item": "56030…",
            "Description": descr,
            "Identificativo": "6581-HEXAGON NUT",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_2",
            "ERP_L1": "60_FASTENER",
            "ERP_L2": "11_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Stud, Threaded":
    st.subheader("Configurazione - Stud, Threaded")
    threaded = st.selectbox("Threaded", ["Partial", "Full"])
    size = st.text_input("Size")
    length = st.text_input("Length")
    note = st.text_area("Note (opzionale)", height=80)
    dwg = st.text_input("Dwg/doc number")
    material = st.text_input("Material")
    note2 = st.text_area("Material Note (opzionale)", height=80)
    if st.button("Genera Output", key="gen_stud"):
        descr = f"STUD, THREADED - THREAD: {threaded}, SIZE: {size}, LENGTH: {length}"
        if note:
            descr += f", {note}"
        descr += f", {material}"
        if note2:
            descr += f", {note2}"
        st.session_state["output_data"] = {
            "Item": "56146…",
            "Description": descr,
            "Identificativo": "6572-STUD",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "ARTVARI",
            "Disegno": dwg,
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_2",
            "ERP_L1": "60_FASTENER",
            "ERP_L2": "12_STANDARD_BOLT_NUT_STUD_SCREW_WASHER",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Gusset, Other":
    st.subheader("Configurazione - Gusset, Other")
    width = st.number_input("Width", min_value=0, step=1, format="%d")
    thickness = st.number_input("Thickness", min_value=0, step=1, format="%d")
    uom = st.selectbox("Unità di misura", ["mm", "inches"])
    note = st.text_area("Note (opzionale)", height=80)
    material = st.text_input("Material")
    note2 = st.text_area("Material Note (opzionale)", height=80)
    if st.button("Genera Output", key="gen_gusset"):
        descr = f"GUSSET, OTHER - WIDTH: {width}{uom}, THK: {thickness}{uom}"
        if note:
            descr += f", {note}"
        descr += f", {material}"
        if note2:
            descr += f", {note2}"
        st.session_state["output_data"] = {
            "Item": "565G…",
            "Description": descr,
            "Identificativo": "GUSSETING",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "ARTVARI",
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_1",
            "ERP_L1": "21_FABRICATION_OR_BASEPLATES",
            "ERP_L2": "29_OTHER",
            "To supplier": "",
            "Quality": ""
        }
        
        elif selected_part == "Ring, Wear":
    st.subheader("Configurazione - Ring, Wear")

    ring_type = st.selectbox("Type", ["Stationary", "Rotary"])
    model = st.selectbox("Product/Pump Model", [""] + pump_models)
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list)

    int_dia = st.number_input("Internal Diameter (mm)", min_value=0, step=1, format="%d")
    ext_dia = st.number_input("External Diameter (mm)", min_value=0, step=1, format="%d")
    thk = st.number_input("Thickness (mm)", min_value=0, step=1, format="%d")
    note = st.text_area("Note (opzionale)", height=80)
    clearance = st.radio("Increased clearance?", ["No", "Yes"], horizontal=True)
    dwg = st.text_input("Dwg/doc number")

    material = st.text_input("Material")
    note2 = st.text_area("Material Note (opzionale)", height=80)

    if st.button("Genera Output", key="gen_ring"):
        descr = f"RING, WEAR - {ring_type} {model} {size}, ID {int_dia}mm, OD {ext_dia}mm, THK {thk}mm"
        if note:
            descr += f", {note}"
        if clearance == "Yes":
            descr += ", INCREASED CLEARANCE"
        descr += f", {material}"
        if note2:
            descr += f", {note2}"

        if ring_type == "Rotary":
            identificativo = "2300-IMPELLER WEAR RING"
            item_code = "40224…"
        else:
            identificativo = "1500-CASING WEAR RING"
            item_code = "40223…"

        st.session_state["output_data"] = {
            "Item": item_code,
            "Description": descr,
            "Identificativo": identificativo,
            "Classe ricambi": "1-2-3",
            "Categories": "FASCIA ITE 4",
            "Catalog": "ALBERO",
            "Disegno": dwg,
            "Material": material,
            "FPD material code": "TO DEFINE",
            "Template": "FPD_BUY_1",
            "ERP_L1": "20_TURNKEY_MACHINING",
            "ERP_L2": "24_RINGS",
            "To supplier": "",
            "Quality": ""
        }
        
        #