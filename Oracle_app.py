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
    "Bolt, Eye"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

# Dati comuni
pump_models    = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

# Funzione generica per le parti a catalog
def genera_output(parte, item, identificativo, classe, erp_l2,
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

    # Campi extra
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
            "Item":               item,
            "Description":        descrizione,
            "Identificativo":     identificativo,
            "Classe ricambi":     classe,
            "FPD material code":  codice_fpd,
            "Template":           template,
            "ERP_L1":             "21_FABRICATIONS_OR_BASEPLATES" if parte == "baseplate" else "20_TURNKEY_MACHINING",
            "ERP_L2":             erp_l2,
            "To supplier":        "",
            "Quality":            ""
        }

# --- ROUTING DELLE PARTI --- #
if selected_part == "Baseplate, Pump":
    st.subheader("Configurazione - Baseplate, Pump")
    genera_output("baseplate", "477…", "6110-BASE PLATE", "", "18_FOUNDATION_PLATE", extra_fields="baseplate")

elif selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")
    genera_output("casing", "40202…", "1100-CASING", "3", "17_CASING", template_fisso="FPD_MAKE")

elif selected_part == "Casing Cover, Pump":
    st.subheader("Configurazione - Casing Cover, Pump")
    genera_output("cover", "40205…", "1221-CASING COVER", "3", "13_OTHER")

elif selected_part == "Impeller, Pump":
    st.subheader("Configurazione - Impeller, Pump")
    genera_output("imp", "40229…", "2200-IMPELLER", "2-3", "20_IMPELLER_DIFFUSER", template_fisso="FPD_MAKE")

elif selected_part == "Balance Bushing, Pump":
    st.subheader("Configurazione - Balance Bushing, Pump")
    genera_output("balance", "40226…", "6231-BALANCE DRUM BUSH", "1-2-3", "16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Drum, Pump":
    st.subheader("Configurazione - Balance Drum, Pump")
    genera_output("drum", "40227…", "6231-BALANCE DRUM BUSH", "1-2-3", "16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Disc, Pump":
    st.subheader("Configurazione - Balance Disc, Pump")
    genera_output("disc", "40228…", "6210-BALANCE DISC", "1-2-3", "30_DISK", extra_fields="diameters")

elif selected_part == "Shaft, Pump":
    st.subheader("Configurazione - Shaft, Pump")
    genera_output("shaft", "40231…", "2100-SHAFT", "2-3", "25_SHAFTS", template_fisso="FPD_MAKE", extra_fields="shaft")

elif selected_part == "Flange, Pipe":
    st.subheader("Configurazione - Flange, Pipe")
    flange_type = st.selectbox("Type", ["SW", "BW"], key="flange_type")
    size_fp     = st.selectbox("Size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="flange_size")
    face_type   = st.selectbox("Face Type", ["RF","FF","RJ"], key="flange_face")
    flange_cls  = st.selectbox("Class", ["150","300","600","1500","2500"], key="flange_class")
    schedule_fp = st.selectbox("Schedula", ["5","10","20","30","40","60","80","100","120","140","160"], key="flange_schedula")
    flange_mat  = st.selectbox("Flange Material", [
        "A105","A106-GR B","UNS-S31803","UNS-S32760","A350 LF2","A182-F316L",
        "ALLOY 825","GALVANIZED CARBON STEEL"
    ], key="flange_mat")
    note_fp = st.text_area("Note (opzionale)", height=80, key="note_flange")
    if st.button("Genera Output", key="gen_flange"):
        descr_fp = (
            f"FLANGE, PIPE - TYPE: {flange_type}, SIZE: {size_fp}, "
            f"FACE TYPE: {face_type}, CLASS: {flange_cls}, SCHEDULA: {schedule_fp}, MATERIAL: {flange_mat}"
        )
        if note_fp:
            descr_fp += f", NOTE: {note_fp}"
        st.session_state["output_data"] = {
            "Item":               "50155…",
            "Description":        descr_fp,
            "Identificativo":     "1245-FLANGE",
            "Classe ricambi":     "",
            "FPD material code":  "BO-NA",
            "Template":           "FPD_BUY_2",
            "ERP_L1":             "23_FLANGE",
            "ERP_L2":             "13_OTHER",
            "To supplier":        "",
            "Quality":            ""
        }

elif selected_part == "Gate, Valve":
    st.subheader("Configurazione - Gate, Valve")
    size        = st.selectbox("Size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="gate_size")
    pclass      = st.selectbox("Pressure class", ["150","300","600","1500","2500"], key="gate_pressure")
    inlet_type  = st.selectbox("Inlet connection type", ["SW","WN"], key="gate_inlet_type")
    inlet_size  = st.selectbox("Inlet connection size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="gate_inlet_size")
    outlet_type = st.selectbox("Outlet connection type", ["SW","WN"], key="gate_outlet_type")
    outlet_size = st.selectbox("Outlet connection size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'], key="gate_outlet_size")
    valve_mat   = st.selectbox("Valve material", [
        "A105","A106-GR B","UNS-S31803","UNS-S32760","A350 LF2","A182-F316L",
        "ALLOY 825","GALVANIZED CARBON STEEL"
    ], key="gate_mat")
    schedule    = st.selectbox("Schedula", ["5","10","20","30","40","60","80","100","120","140","160"], key="gate_schedula")
    note_gate   = st.text_area("Note (opzionale)", height=80, key="gate_note")
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
            "Item":               "50186…",
            "Description":        descr_gate,
            "Identificativo":     "VALVOLA (GLOBO,SARAC,SFERA,NEEDLE,MANIF,CONTR)",
            "Classe ricambi":     "",
            "FPD material code":  "BO-NA",
            "Template":           "FPD_BUY_2",
            "ERP_L1":             "72_VALVE",
            "ERP_L2":             "18_GATE_VALVE",
            "To supplier":        "",
            "Quality":            ""
        }

elif selected_part == "Gasket, Spiral Wound":
    st.subheader("Configurazione - Gasket, Spiral Wound")
    # … (resto come prima) …

# … gli altri blocchi analoghi …

# Output finale
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100)
        else:
            st.text_input(campo, value=valore)