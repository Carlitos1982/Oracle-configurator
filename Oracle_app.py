import streamlit as st
import pandas as pd

st.set_page_config(layout="centered", page_title="Oracle Config", page_icon="⚙️")
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

part_options = [
    "Baseplate, Pump",
    "Casing, Pump",
    "Casing Cover, Pump",
    "Impeller, Pump",
    "Balance Bushing, Pump",
    "Balance Drum, Pump",
    "Balance Disc, Pump",
    "Shaft, Pump"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

pump_models = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

def genera_output(parte, item, identificativo, classe, catalog, erp_l2, template_fisso=None, extra_fields=None):
    model = st.selectbox("Product/Pump Model", [""] + pump_models, key=f"model_{parte}")
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list, key=f"size_{parte}")

    feature_1 = ""
    modelli_speciali = ["HDO", "DMX", "WXB", "WIK"]
    if not (model in modelli_speciali and parte != "casing"):
        feature1_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features1")]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + feature1_list, key=f"f1_{parte}")

    feature_2 = ""
    if (model == "HPX" and parte == "casing") or model == "HED":
        feature2_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features2")]["Feature"].dropna().tolist()
        feature_2 = st.selectbox("Additional Feature 2", [""] + feature2_list, key=f"f2_{parte}")

    extra_descr = ""
    if extra_fields == "diameters":
        int_dia = st.number_input("Qual è il diametro interno (in mm)?", min_value=0, step=1, format="%d", key=f"int_dia_{parte}")
        ext_dia = st.number_input("Qual è il diametro esterno (in mm)?", min_value=0, step=1, format="%d", key=f"ext_dia_{parte}")
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
        extra_descr = f"Brg. type: {brg_type} Brg. size: {brg_size} Max dia: {max_dia}mm Max len: {max_len}mm"

    note = st.text_area("Note (opzionale)", height=80, key=f"note_{parte}")
    dwg = st.text_input("Dwg/doc number", key=f"dwg_{parte}")

    if parte == "cover" and model in ["HPX", "PVML"]:
        make_or_buy = st.radio("Make or Buy", ["Make", "Buy"], horizontal=True, key=f"mob_{parte}")
        template = "FPD_MAKE" if make_or_buy == "Make" else "FPD_BUY_1"
    elif parte == "cover":
        template = "FPD_MAKE"
    elif parte in ["balance", "drum", "disc"]:
        template = "FPD_BUY_1"
    elif parte == "baseplate":
        template = "FPD_BUY_4"
    else:
        template = template_fisso

    mtype = st.selectbox("Material Type", [""] + material_types, key=f"mtype_{parte}")
    prefix_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefix_list = sorted(prefix_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefix_list, key=f"mprefix_{parte}")
    if mtype == "MISCELLANEOUS":
        name_list = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        name_list = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
    mname = st.selectbox("Material Name", [""] + name_list, key=f"mname_{parte}")
    madd = st.text_input("Material add. Features (opzionale)", key=f"madd_{parte}")

    if st.button("Genera Output", key=f"gen_{parte}"):
        materiale = f"{mtype} {mname}" if mtype == "MISCELLANEOUS" else f"{mtype} {mprefix} {mname}"
        materiale = materiale.strip()
        match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix) & (materials_df["Name"] == mname)]
        codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
        materiale_descr = " ".join(filter(None, [mtype, mprefix, mname, madd]))
        descrizione = f"{selected_part} " + " ".join(filter(None, [model, size, feature_1, feature_2, extra_descr, note, materiale_descr]))

        st.session_state["output_data"] = {
            "Item": item,
            "Description": descrizione,
            "Identificativo": identificativo,
            "Classe ricambi": classe,
            "Categories": "Fascia ite 5" if parte == "baseplate" else "Fascia ite 4",
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

# === ROUTING ===
if selected_part == "Baseplate, Pump":
    st.subheader("Configurazione - Baseplate, Pump")
    genera_output(parte="baseplate", item="477...", identificativo="6110-BASE PLATE", classe="", catalog="ARTVARI", erp_l2="18_FOUNDATION PLATE", extra_fields="baseplate")

elif selected_part == "Casing, Pump":
    st.subheader("Configurazione - Casing, Pump")
    genera_output(parte="casing", item="40202...", identificativo="1100-CASING", classe="3", catalog="CORPO", erp_l2="17_CASING", template_fisso="FPD_MAKE")

elif selected_part == "Casing Cover, Pump":
    st.subheader("Configurazione - Casing Cover, Pump")
    genera_output(parte="cover", item="40205...", identificativo="1221-CASING COVER", classe="3", catalog="COPERCHIO", erp_l2="13_OTHER")

elif selected_part == "Impeller, Pump":
    st.subheader("Configurazione - Impeller, Pump")
    genera_output(parte="imp", item="40229...", identificativo="2200-IMPELLER", classe="2-3", catalog="GIRANTE", erp_l2="20_IMPELLER_DIFFUSER", template_fisso="FPD_MAKE")

elif selected_part == "Balance Bushing, Pump":
    st.subheader("Configurazione - Balance Bushing, Pump")
    genera_output(parte="balance", item="40226...", identificativo="6231-BALANCE DRUM BUSH", classe="1-2-3", catalog="ALBERO", erp_l2="16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Drum, Pump":
    st.subheader("Configurazione - Balance Drum, Pump")
    genera_output(parte="drum", item="40227...", identificativo="6231-BALANCE DRUM BUSH", classe="1-2-3", catalog="ARTVARI", erp_l2="16_BUSHING", extra_fields="diameters")

elif selected_part == "Balance Disc, Pump":
    st.subheader("Configurazione - Balance Disc, Pump")
    genera_output(parte="disc", item="40228...", identificativo="6210-BALANCE DISC", classe="1-2-3", catalog="ARTVARI", erp_l2="30_DISK", extra_fields="diameters")

elif selected_part == "Shaft, Pump":
    st.subheader("Configurazione - Shaft, Pump")
    genera_output(parte="shaft", item="40231...", identificativo="2100-SHAFT", classe="2-3", catalog="ALBERO", erp_l2="25_SHAFTS", template_fisso="FPD_MAKE", extra_fields="shaft")

# === OUTPUT FINALE ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")
    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")