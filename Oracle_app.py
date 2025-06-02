import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

# --- Configurazione pagina wide
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- Header con titolo e logo Flowserve
flowserve_logo = Image.open("assets/IMG_1456.png")
col_header, col_spacer, col_logo = st.columns([3, 4, 1], gap="small")
with col_header:
    st.markdown("# Oracle Item Setup - Web App")
with col_logo:
    st.image(flowserve_logo, width=100)

st.markdown("---")

# --- Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df = pd.read_excel(xls, sheet_name="Pump Size")
    features_df = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- Selezione parte
part = st.selectbox("Seleziona il tipo di parte da configurare:", [
    "Shaft, Pump",
    "Gasket, Flat",
    "Flange, Pipe",
    "Gasket, Spiral Wound",
    "Nut, Hex",
    "Stud, Threaded",
    "Ring, Wear",
    "Gusset, Other"
])
st.markdown("---")

# --- SHAFT, PUMP

# --- FLANGE, PIPE

if part == "Flange, Pipe":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        pipe_type = st.selectbox("Pipe Type", ["SW", "WN"])
        size = st.selectbox("Size", ["1/8\"", "1/4\"", "3/8\"", "1/2\"", "3/4\"", "1\"", "1 1/4\"", "1 1/2\"", "2\"", "2 1/2\"", "3\"", "4\""])
        face_type = st.selectbox("Face Type", ["RF", "FF", "RJ"])
        pressure_class = st.text_input("Class")
        material = st.text_input("Material")
        add_feat = st.text_input("Additional features (opzionale)")

        if st.button("Genera Output", key="gen_flange"):
            desc = f"FLANGE - TYPE: {pipe_type}, SIZE: {size}, FACE: {face_type}, CLASS: {pressure_class}, MATERIAL: {material}"
            if add_feat:
                desc += f", FEATURES: {add_feat}"
            st.session_state["output"] = {
                "Item": "50155…",
                "Description": desc,
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
                "Quality": ""
            }

    with col2:
        st.subheader("📤 Output")
        if "output" in st.session_state:
            for k, v in st.session_state.output.items():
                if k == "Description":
                    st.text_area(k, value=v, height=80)
                else:
                    st.text_input(k, value=v)

    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="flange_dl_mode")
        item_code_input = st.text_input("Codice item", key="flange_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_flange"):
            if not item_code_input:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\%FN", item_code_input,
                    "\%TC", get_val("Template"), "TAB",
                    "\%D", "\%O", "TAB",
                    get_val("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\%O", "\^S",
                    "\%TA", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val("Categories").split()[-1], "\^S", "\^{F4}",
                    "\%TG", get_val("Catalog"), "TAB", "TAB", "TAB",
                    get_val("Disegno"), "TAB", "\^S", "\^{F4}",
                    "\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\^S", "\^{F4}",
                    "\%VA", "TAB",
                    get_val("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val("Quality") if get_val("Quality") != "." else ".", "\^S",
                    "\%FN", "TAB",
                    get_val("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val("To supplier") if get_val("To supplier") != "." else ".", "\^S", "\^S", "\^{F4}", "\^S"
                ]
                dataload_string = "	".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(
                    label="📎 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code_input}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")


# --- GASKET, FLAT
elif part == "Gasket, Flat":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        thickness = st.number_input("Thickness (mm)", min_value=0.0, step=0.1, key="thk")
        uom = st.selectbox("UOM", ["mm", "inches"], key="uom")
        dwg = st.text_input("Dwg/doc number", key="dwg")
        mtype = st.selectbox("Material Type", [""] + material_types, key="mtype")

        df_pref = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(df_pref["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = (
                materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Prefix"] == mprefix)
                ]["Name"].dropna().tolist()
            )
        mname = st.selectbox("Material Name", [""] + names, key="mname")

        if st.button("Genera Output", key="gen_flatgasket"):
            st.session_state["output"] = {}
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
            descr = f"GASKET, FLAT - THK: {thickness}{uom}, MATERIAL: {materiale}"
            st.session_state["output"] = {
                "Item": "50158…",
                "Description": descr,
                "Identificativo": "4590-GASKET",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_BUY_2",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    with col2:
        st.subheader("📤 Output")
        if "output" in st.session_state:
            for k, v in st.session_state.output.items():
                if k == "Description":
                    st.text_area(k, value=v, height=80)
                else:
                    st.text_input(k, value=v)

    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="flat_dl_mode")
        item_code_input = st.text_input("Codice item", key="flat_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_flat"):
            if not item_code_input:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output"]
                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."
                dataload_fields = [
                    "\%FN", item_code_input,
                    "\%TC", get_val("Template"), "TAB",
                    "\%D", "\%O", "TAB",
                    get_val("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\%O", "\^S",
                    "\%TA", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val("Categories").split()[-1], "\^S", "\^{F4}",
                    "\%TG", get_val("Catalog"), "TAB", "TAB", "TAB",
                    get_val("Disegno"), "TAB", "\^S", "\^{F4}",
                    "\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\^S", "\^{F4}",
                    "\%VA", "TAB",
                    get_val("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val("Quality") if get_val("Quality") != "." else ".", "\^S",
                    "\%FN", "TAB",
                    get_val("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val("To supplier") if get_val("To supplier") != "." else ".", "\^S", "\^S", "\^{F4}", "\^S"
                ]
                dataload_string = "	".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])
                st.download_button(
                    label="📎 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code_input}.csv",
                    mime="text/csv"
                )
                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")


# --- SHAFT, PUMP
if part == "Shaft, Pump":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.text_input("Product/Pump Model")
        size = st.text_input("Product Pump Size")
        feat1 = st.text_input("Additional features 1")
        feat2 = st.text_input("Additional features 2")
        brg_type = st.text_input("Brg. type")
        brg_size = st.text_input("Brg. Size")
        diameter = st.number_input("Max diameter (mm)", min_value=0.0, step=0.1)
        length = st.number_input("Max length (mm)", min_value=0.0, step=0.1)
        dwg = st.text_input("Dwg/doc")
        note = st.text_area("Note")
        mtype = st.selectbox("Material Type", [""] + material_types, key="shaft_mtype")

        df_pref = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
        prefixes = sorted(df_pref["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
        mprefix = st.selectbox("Material Prefix", [""] + prefixes, key="shaft_mprefix")

        if mtype == "MISCELLANEOUS":
            names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        else:
            names = (
                materials_df[
                    (materials_df["Material Type"] == mtype) &
                    (materials_df["Prefix"] == mprefix)
                ]["Name"].dropna().tolist()
            )
        mname = st.selectbox("Material Name", [""] + names, key="shaft_mname")

        if st.button("Genera Output", key="gen_shaft"):
            materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
            match = materials_df[
                (materials_df["Material Type"] == mtype) &
                (materials_df["Prefix"] == mprefix) &
                (materials_df["Name"] == mname)
            ]
            codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
            descr = f"SHAFT - MODEL: {model}, SIZE: {size}, Ø{diameter}x{length}mm, BRG: {brg_type} {brg_size}, FEATURES: {feat1}, {feat2}, NOTE: {note}"

            st.session_state["output"] = {
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
                "Quality": ""
            }

    with col2:
        st.subheader("📤 Output")
        if "output" in st.session_state:
            for k, v in st.session_state.output.items():
                if k == "Description":
                    st.text_area(k, value=v, height=80)
                else:
                    st.text_input(k, value=v)

    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="shaft_dl_mode")
        item_code_input = st.text_input("Codice item", key="shaft_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_shaft"):
            if not item_code_input:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output"]

                def get_val(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields = [
                    "\\%FN", item_code_input,
                    "\\%TC", get_val("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val("Identificativo"), "TAB",
                    get_val("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val('ERP_L1')}.{get_val('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val("Catalog"), "TAB", "TAB", "TAB",
                    get_val("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val("FPD material code"), "TAB",
                    get_val("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val("Quality") if get_val("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val("To supplier") if get_val("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string = "\t".join(dataload_fields)
                st.text_area("Anteprima (per copia manuale)", dataload_string, height=200)

                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields:
                    writer.writerow([riga])

                st.download_button(
                    label="📎 Scarica file CSV per Import Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"dataload_{item_code_input}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- Footer
st.markdown("---")
st.markdown("<div style='text-align:center;'><small>v1.0 • © 2025 Flowserve Desio Order Engineering</small></div>", unsafe_allow_html=True)
st.markdown("""
<div style="
    background-color:#f9f9f9;
    padding:0.8rem;
    border-radius:8px;
    text-align:center;
    font-size:0.9rem;
    color:#555;
    margin-top:1rem;
">
    Created by <strong>dzecchinel</strong> • <a href="mailto:dzecchinel@gmail.com">dzecchinel@gmail.com</a>
</div>
""", unsafe_allow_html=True)
