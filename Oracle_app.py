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
    "Casing, Pump",
    "Casing Cover, Pump",
    "Impeller, Pump",
    "Balance Bushing, Pump"
]
selected_part = st.selectbox("Seleziona Parte", part_options)

pump_models = sorted(size_df["Pump Model"].dropna().unique())
material_types = materials_df["Material Type"].dropna().unique().tolist()

def genera_output(parte, item, identificativo, classe, catalog, erp_l2, template_fisso=None, extra_fields=None):
    model = st.selectbox("Product/Pump Model", [""] + pump_models, key=f"model_{parte}")
    size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
    size = st.selectbox("Product/Pump Size", [""] + size_list, key=f"size_{parte}")

    feature1_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features1")]["Feature"].dropna().tolist()
    feature2_list = features_df[(features_df["Pump Model"] == model) & (features_df["Feature Type"] == "features2")]["Feature"].dropna().tolist()

    feature_1 = st.selectbox("Additional Feature 1", [""] + feature1_list, key=f"f1_{parte}")
    feature_2 = st.selectbox("Additional Feature 2", [""] + feature2_list if feature2_list else [""], key=f"f2_{parte}")

    extra_descr = ""
    if extra_fields == "diameters":
        int_dia = st.number_input("Qual è il diametro interno (in mm)?", min_value=0.0, step=0.1, key=f"int_dia_{parte}")
        ext_dia = st.number_input("Qual è il diametro esterno (in mm)?", min_value=0.0, step=0.1, key=f"ext_dia_{parte}")
        extra_descr = f"int. dia.: {int_dia}mm ext. dia.: {ext_dia}mm"

    note = st.text_area("Note (opzionale)", height=80, key=f"note_{parte}")
    dwg = st.text_input("Dwg/doc number", key=f"dwg_{parte}")

    if parte == "cover":
        make_or_buy = st.radio("Make or Buy", ["Make", "Buy"], horizontal=True, key="mob_cover")
        template = "FPD_MAKE" if make_or_buy == "Make" else "FPD_BUY_1"
    elif parte == "balance":
        template = "FPD_BUY_1"
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
            "Categories": "Fascia ite 4",
            "Catalog": catalog,
            "Disegno": dwg,
            "Material": materiale,
            "FPD material code": codice_fpd,
            "Template": template,
            "ERP_L1": "20_TURNKEY_MACHINING",
            "ERP_L2": erp_l2,
            "To supplier": "",
            "Quality": ""
        }

# === ROUTING ===
if selected_part == "Casing, Pump":
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
    genera_output(
        parte="balance",
        item="402XX...",
        identificativo="6231-BALANCE DRUM BUSH",
        classe="1-2-3",
        catalog="ALBERO",
        erp_l2="16_BUSHING",
        extra_fields="diameters"
    )

# === OUTPUT FINALE ===
if "output_data" in st.session_state:
    st.subheader("Risultato finale")
    st.markdown("_Clicca nei campi e usa Ctrl+C per copiare il valore_")

    for campo, valore in st.session_state["output_data"].items():
        if campo == "Description":
            st.text_area(campo, value=valore, height=100, key=f"out_{campo}")
        else:
            st.text_input(campo, value=valore, key=f"out_{campo}")