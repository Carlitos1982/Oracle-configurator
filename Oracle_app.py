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

        # Costruzione descrizione
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

elif selected_part == "Flange, Pipe":
    st.subheader("Configurazione - Flange, Pipe")
    flange_type = st.selectbox("Type", ["SW", "BW"])
    size_fp     = st.selectbox("Size", ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'])
    face_type   = st.selectbox("Face Type", ["RF","FF","RJ"])
    flange_cls  = st.selectbox("Class", ["150","300","600","1500","2500"])
    schedule_fp = st.selectbox("Schedula", ["5","10","20","30","40","60","80","100","120","140","160"])
    flange_mat  = st.selectbox("Flange Material", [
        "A105","A106-GR B","UNS-S31803","UNS-S32760","A350 LF2","A182-F316L",
        "ALLOY 825","GALVANIZED CARBON STEEL"
    ])
    note_fp = st.text_area("Note (opzionale)", height=80, key="note_flange")
    dwg_fp  = st.text_input("Dwg/doc number", key="dwg_flange")
    if st.button("Genera Output", key="gen_flange"):
        descr_fp = (
            f"FLANGE, PIPE - TYPE: {flange_type}, SIZE: {size_fp}, "
            f"FACE TYPE: {face_type}, CLASS: {flange_cls}, SCHEDULA: {schedule_fp}, MATERIAL: {flange_mat}"
        )
        if note_fp:
            descr_fp += f", NOTE: {note_fp}"
        st.session_state["output_data"] = {
            "Item": "50155…",
            "Description": descr_fp,
            "Identificativo": "1245-FLANGE",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": "NOT AVAILABLE",
            "FPD material code": "BO-NA",
            "Template": "FPD_BUY_2",
            "ERP_L1": "23_FLANGE",
            "ERP_L2": "13_OTHER",
            "To supplier": "",
            "Quality": ""
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
    ], key="gate_material")
    schedule    = st.selectbox("Schedula", ["5","10","20","30","40","60","80","100","120","140","160"], key="gate_schedule")
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
            "Item": "50186…",
            "Description": descr_gate,
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
    winding_colors = {
        "304 stainless steel":"Yellow RAL1021","316L stainless steel":"Green RAL6005",
        "317L stainless steel":"Maroon RAL3003","321 stainless steel":"Turquoise RAL5018",
        "347 stainless steel":"Blue RAL5017","MONEL":"Orange RAL2003","Nickel":"Red RAL3024",
        "Titanium":"Purple RAL4003","Alloy20":"Black RAL9005","INCONEL 600":"Gold RAL1004",
        "HASTELLOY B":"Brown RAL8003","HASTELLOY C":"Beige RAL1001","INCOLOY800":"White RAL9010",
        "DUPLEX":"Yellow+Blue RAL1021+5017","SUPERDUPLEX":"Red+Black RAL3024+9005",
        "ALLOY 825":"Orange+Green RAL2003+6005","UNS S31254":"Orange+Blue RAL2003+5017",
        "ZYRCONIUM 702":"Gold+Green RAL1004+6005","INCONEL X750HT":"Gold+Black RAL1004+9005"
    }
    filler_colors = {
        "Graphite":"Gray RAL7011","PTFE":"White RAL9010",
        "Ceramic":"Ceramic Lt. Green RAL6021","Verdicarb (Mica Graphite)":"Pink RAL3015"
    }
    rating_stripes = {
        "STANDARD PRESSURE m=3 y=10000 psi":"(1 stripe)",
        "HIGH PRESSURE m=3 y=17500 psi":"(2 stripes)",
        "ULTRA HIGH PRESSURE m=3 y=23500 psi":"(3 stripes)"
    }

    winding   = st.selectbox("Winding material", list(winding_colors.keys()))
    filler    = st.selectbox("Filler", list(filler_colors.keys()))
    inner_dia = st.number_input("Diametro interno (mm)", min_value=0.0, step=0.1, format="%.1f")
    outer_dia = st.number_input("Diametro esterno (mm)", min_value=0.0, step=0.1, format="%.1f")
    thickness = st.number_input("Spessore (mm)", min_value=0.0, step=0.1, format="%.1f")
    rating    = st.selectbox("Rating", list(rating_stripes.keys()))
    dwg_g     = st.text_input("Dwg/doc number", key="dwg_gasket")
    note_g    = st.text_area("Note (opzionale)", height=80, key="note_gasket")

    if st.button("Genera Output", key="gen_gasket"):
        c1     = winding_colors[winding]
        c2     = filler_colors[filler]
        stripe = rating_stripes[rating]
        descr  = (
            f"GASKET, SPIRAL WOUND - WINDING: {winding}, FILLER: {filler}, "
            f"ID: {inner_dia}mm, OD: {outer_dia}mm, THK: {thickness}mm, "
            f"RATING: {rating}, COLOR CODE: {c1}/{c2}, {stripe}"
        )
        if note_g:
            descr += f", NOTE: {note_g}"

        st.session_state["output_data"] = {
            "Item": "50415…",
            "Description": descr,
            "Identificativo": "4510-JOINT",
            "Classe ricambi": "1-2-3",
            "Categories": "FASCIA ITE 5",
            "Catalog": "ARTVARI",
            "Disegno": dwg_g,
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
    thickness    = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.1f", key="thk_flat")
    uom          = st.selectbox("UOM", ["mm", "inches"], key="uom_flat")
    dwg_flat     = st.text_input("Dwg/doc number", key="dwg_flat")
    mtype_flat   = st.selectbox("Material Type", [""] + material_types, key="mtype_flat")
    pref_df_flat = materials_df[
        (materials_df["Material Type"] == mtype_flat) &
        (materials_df["Prefix"].notna())
    ]
    prefixes_flat = sorted(pref_df_flat["Prefix"].unique()) if mtype_flat != "MISCELLANEOUS" else []
    mprefix_flat  = st.selectbox("Material Prefix", [""] + prefixes_flat, key="mprefix_flat")
    if mtype_flat == "MISCELLANEOUS":
        names_flat = materials_df[materials_df["Material Type"] == mtype_flat]["Name"].dropna().tolist()
    else:
        names_flat = materials_df[
            (materials_df["Material Type"] == mtype_flat) &
            (materials_df["Prefix"] == mprefix_flat)
        ]["Name"].dropna().tolist()
    mname_flat = st.selectbox("Material Name", [""] + names_flat, key="mname_flat")

    if st.button("Genera Output", key="gen_flat"):
        if mtype_flat != "MISCELLANEOUS":
            materiale_flat = f"{mtype_flat} {mprefix_flat} {mname_flat}".strip()
            match_flat = materials_df[
                (materials_df["Material Type"] == mtype_flat) &
                (materials_df["Prefix"] == mprefix_flat) &
                (materials_df["Name"] == mname_flat)
            ]
        else:
            materiale_flat = mname_flat
            match_flat = materials_df[
                (materials_df["Material Type"] == mtype_flat) &
                (materials_df["Name"] == mname_flat)
            ]
        codice_flat = match_flat["FPD Code"].values[0] if not match_flat.empty else ""
        descr_flat = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {materiale_flat}"

        st.session_state["output_data"] = {
            "Item": "50158…",
            "Description": descr_flat,
            "Identificativo": "4590-GASKET",
            "Classe ricambi": "1-2-3",
            "Categories": "FASCIA ITE 5",
            "Catalog": "ARTVARI",
            "Disegno": dwg_flat,
            "Material": materiale_flat,
            "FPD material code": codice_flat,
            "Template": "FPD_BUY_2",
            "ERP_L1": "55_GASKETS_OR_SEAL",
            "ERP_L2": "20_OTHER",
            "To supplier": "",
            "Quality": ""
        }

elif selected_part == "Bearing, Hydrostatic/Hydrodynamic":
    st.subheader("Configurazione - Bearing, Hydrostatic/Hydrodynamic")
    ins_dia        = st.number_input("InsDia (mm)",  min_value=0.0, step=0.1, format="%.1f", key="insdia_bearing")
    out_dia        = st.number_input("OutDia (mm)",  min_value=0.0, step=0.1, format="%.1f", key="outdia_bearing")
    width          = st.number_input("Width (mm)",   min_value=0.0, step=0.1, format="%.1f", key="width_bearing")
    add_feat       = st.text_input("Additional Features", key="feat_bearing")
    dwg_bearing    = st.text_input("Dwg/doc number", key="dwg_bearing")
    mtype_bearing  = st.selectbox("Type", [""] + material_types, key="mtype_bearing")
    prefixes       = (
        sorted(materials_df[
            (materials_df["Material Type"]==mtype_bearing)&
            (materials_df["Prefix"].notna())
        ]["Prefix"].unique())
        if mtype_bearing in ["ASTM","EN"] else []
    )
    mprefix_bearing = st.selectbox("Prefix (only if ASTM or EN)", [""] + prefixes, key="mprefix_bearing")
    if mtype_bearing == "MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"]==mtype_bearing]["Name"].dropna().tolist()
    else:
        names = materials_df[
            (materials_df["Material Type"]==mtype_bearing)&
            (materials_df["Prefix"]==mprefix_bearing)
        ]["Name"].dropna().tolist()
    mname_bearing    = st.selectbox("Name", [""] + names, key="mname_bearing")
    mat_feat_bearing = st.text_input("Material add. Features", key="matfeat_bearing")

    if st.button("Genera Output", key="gen_bearing"):
        if mtype_bearing != "MISCELLANEOUS":
            materiale_b = f"{mtype_bearing} {mprefix_bearing} {mname_bearing}".strip()
            match_b     = materials_df[
                (materials_df["Material Type"]==mtype_bearing)&
                (materials_df["Prefix"]==mprefix_bearing)&
                (materials_df["Name"]==mname_bearing)
            ]
        else:
            materiale_b = mname_bearing
            match_b     = materials_df[
                (materials_df["Material Type"]==mtype_bearing)&
                (materials_df["Name"]==mname_bearing)
            ]
        codice_fpd_b = match_b["FPD Code"].values[0] if not match_b.empty else ""
        descr_b = (
            "Bearing, Hydrostatic/Hydrodynamic; "
            f"InsDia(mm){ins_dia} "
            f"OutDia(mm){out_dia} "
            f"Width(mm){width} "
            f"{add_feat} "
            f"{mat_feat_bearing}"
        )
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

elif selected_part == "Bearing, Rolling":
    st.subheader("Configurazione - Bearing, Rolling")
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
    ins_dia_r     = st.number_input("InsDia (mm)",  min_value=0.0, step=0.1, format="%.1f", key="insdia_rolling")
    out_dia_r     = st.number_input("OutDia (mm)", min_value=0.0, step=0.1, format="%.1f", key="outdia_rolling")
    width_r       = st.number_input("Width (mm)",  min_value=0.0, step=0.1, format="%.1f", key="width_rolling")
    add_feat_r    = st.text_input("Additional Features", key="feat_rolling")
    dwg_rolling   = st.text_input("Dwg/doc number", key="dwg_rolling")

    if st.button("Genera Output", key="gen_rolling"):
        descr_rolling = (
            f"Bearing, Rolling;{bearing_type} {designation} "
            f"InsDia(mm){ins_dia_r} OutDia(mm){out_dia_r} Width(mm){width_r} "
            f"{add_feat_r}"
        )
        st.session_state["output_data"] = {
            "Item":               "50122…",
            "Description":        descr_rolling,
            "Identificativo":     "3010-ANTI-FRICTION BEARING",
            "Classe ricambi":     "1-2-3",
            "Categories":         "FASCIA ITE 5",
            "Catalog":            "ALBERO",
            "Disegno":            dwg_rolling,
            "Material":           "BUY OUT NOT AVAILABLE",
            "FPD material code":  "BO-NA",
            "Template":           "FPD_BUY_2",
            "ERP_L1":             "31_COMMERCIAL_BEARING",
            "ERP_L2":             "11_BALL_BEARING",
            "To supplier":        "",
            "Quality":            ""
        }


### **1. Bolt, Eye** *(senza etichetta “MATERIAL:” nella descrizione)*
elif selected_part == "Bolt, Eye":
    st.subheader("Configurazione - Bolt, Eye")

    thread = st.selectbox("Thread type/size", [
        "#10-24UNC", "5/16\"-18UNC", "3/8\"-16UNC", "1/2\"-13UNC", "3/4\"-16UNF",
        "7/8\"-9UNC", "7/8\"-14UNF", "1\"-12UNF", "1-1/8\"-12UNF", "1-1/2\"-12UNC",
        "2\"-4.5UNC", "2-1/2\"-4UNC", "3\"-6UNC", "4\"-8UNC",
        "M6x1", "M8x1.25", "M10x1.5", "M12x1.75", "M16x2", "M20x2.5", "M24x3",
        "M30x3.5", "M36x4", "M42x4.5", "M48x5", "M56x5.5", "M64x6", "M72x6", "M80x6",
        "M90x6", "M100x6"
    ], key="bolt_thread")

    length = st.selectbox("Length", [
        "1/8\"in", "1/4\"in", "3/8\"in", "5/16\"in", "1/2\"in", "3/4\"in",
        "1\"in", "1-1/8\"in", "1-1/4\"in", "1-3/8\"in", "1-1/2\"in", "2\"in",
        "2-1/8\"in", "2-1/4\"in", "2-3/8\"in", "2-1/2\"in", "2-3/4\"in",
        "3\"in", "3-1/8\"in", "3-1/4\"in", "3-3/8\"in", "3-1/2\"in", "4\"in",
        "4-1/8\"in", "4-1/4\"in", "4-3/8\"in", "4-1/2\"in",
        "50mm", "55mm", "60mm", "65mm", "70mm", "75mm", "80mm", "85mm", "90mm", "95mm",
        "100mm", "105mm", "110mm", "115mm", "120mm", "125mm", "130mm", "135mm", "140mm",
        "145mm", "150mm", "155mm", "160mm", "165mm", "170mm", "175mm", "180mm", "185mm",
        "190mm", "195mm"
    ], key="bolt_length")

    note1 = st.text_area("Note (opzionale)", height=80, key="bolt_note1")

    mtype_bolt = st.selectbox("Material Type", [""] + material_types, key="mtype_bolt")
    pref_df_bolt = materials_df[(materials_df["Material Type"] == mtype_bolt) & (materials_df["Prefix"].notna())]
    prefixes_bolt = sorted(pref_df_bolt["Prefix"].unique()) if mtype_bolt != "MISCELLANEOUS" else []
    mprefix_bolt = st.selectbox("Material Prefix", [""] + prefixes_bolt, key="mprefix_bolt")

    if mtype_bolt == "MISCELLANEOUS":
        names_bolt = materials_df[materials_df["Material Type"] == mtype_bolt]["Name"].dropna().tolist()
    else:
        names_bolt = materials_df[
            (materials_df["Material Type"] == mtype_bolt) &
            (materials_df["Prefix"] == mprefix_bolt)
        ]["Name"].dropna().tolist()
    mname_bolt = st.selectbox("Material Name", [""] + names_bolt, key="mname_bolt")

    material_note = st.text_area("Material Note (opzionale)", height=80, key="bolt_note2")

    if st.button("Genera Output", key="gen_bolt"):
        if mtype_bolt != "MISCELLANEOUS":
            materiale_bolt = f"{mtype_bolt} {mprefix_bolt} {mname_bolt}".strip()
            match_bolt = materials_df[
                (materials_df["Material Type"] == mtype_bolt) &
                (materials_df["Prefix"] == mprefix_bolt) &
                (materials_df["Name"] == mname_bolt)
            ]
        else:
            materiale_bolt = mname_bolt
            match_bolt = materials_df[
                (materials_df["Material Type"] == mtype_bolt) &
                (materials_df["Name"] == mname_bolt)
            ]
        codice_fpd_bolt = match_bolt["FPD Code"].values[0] if not match_bolt.empty else ""

        # Descrizione con NOTE prima del materiale, e material note senza etichetta
        descr_bolt = f"BOLT, EYE - THREAD: {thread}, LENGTH: {length}"
        if note1:
            descr_bolt += f", NOTE: {note1}"
        descr_bolt += f", {materiale_bolt}"
        if material_note:
            descr_bolt += f", {material_note}"

        st.session_state["output_data"] = {
            "Item": "50150…",
            "Description": descr_bolt,
            "Identificativo": "6583-EYE BOLT",
            "Classe ricambi": "",
            "Categories": "FASCIA ITE 5",
            "Catalog": "",
            "Material": materiale_bolt,
            "FPD material code": codice_fpd_bolt,
            "Template": "FPD_BUY_2",
            "ERP_L1": "60_FASTENER",
            "ERP_L2": "74_OTHER_FASTENING_COMPONENTS_EYE_NUTS_LOCK_NUTS_ETC",
            "To supplier": "",
            "Quality": ""
        }
        
elif selected_part == "Bolt, Hexagonal":
    st.subheader("Configurazione - Bolt, Hexagonal")

    bolt_sizes = [ ... ]  # stesso elenco di Bolt, Eye
    bolt_lengths = [ ... ]

    size_hex   = st.selectbox("Size", bolt_sizes, key="hex_size")
    length_hex = st.selectbox("Length", bolt_lengths, key="hex_length")
    full_thd   = st.radio("Full threaded?", ["Yes", "No"], horizontal=True, key="hex_fullthread")
    zinc       = st.radio("Zinc Plated?", ["Yes", "No"], horizontal=True, key="hex_zinc")
    note1_hex  = st.text_area("Note (opzionale)", height=80, key="hex_note1")

    mtype_hex = st.selectbox("Material Type", [""] + material_types, key="mtype_hex")
    pref_df_hex = materials_df[(materials_df["Material Type"] == mtype_hex) & (materials_df["Prefix"].notna())]
    prefixes_hex = sorted(pref_df_hex["Prefix"].unique()) if mtype_hex != "MISCELLANEOUS" else []
    mprefix_hex  = st.selectbox("Material Prefix", [""] + prefixes_hex, key="mprefix_hex")

    if mtype_hex == "MISCELLANEOUS":
        names_hex = materials_df[materials_df["Material Type"] == mtype_hex]["Name"].dropna().tolist()
    else:
        names_hex = materials_df[
            (materials_df["Material Type"] == mtype_hex) &
            (materials_df["Prefix"] == mprefix_hex)
        ]["Name"].dropna().tolist()
    mname_hex = st.selectbox("Material Name", [""] + names_hex, key="mname_hex")

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

        descr_hex = f"BOLT, HEXAGONAL - SIZE: {size_hex}, LENGTH: {length_hex}"
        if full_thd == "Yes":
            descr_hex += ", FULL THREADED"
        if zinc == "Yes":
            descr_hex += ", ZINC PLATED AS PER ASTM B633"
        descr_hex += f", {materiale_hex}"
        if note1_hex:
            descr_hex += f", NOTE: {note1_hex}"
        if note2_hex:
            descr_hex += f", NOTE: {note2_hex}"

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

        
# Output finale
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100)
        else:
            st.text_input(campo, value=valore)