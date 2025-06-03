import streamlit as st
import pandas as pd
from PIL import Image
import io
import csv

# --- 1) Configurazione pagina wide
st.set_page_config(layout="wide", page_title="Oracle Config", page_icon="⚙️")

# --- 2) Header con titolo e logo Flowserve
flowserve_logo = Image.open("assets/IMG_1456.png")
col_header, col_spacer, col_logo = st.columns([3, 4, 1], gap="small")
with col_header:
    st.markdown("# Oracle Item Setup - Web App")
with col_logo:
    st.image(flowserve_logo, width=100)

st.markdown("---")

# --- 3) Caricamento dati
@st.cache_data
def load_config_data():
    url = "https://raw.githubusercontent.com/Carlitos1982/Oracle-configurator/main/dati_config4.xlsx"
    xls = pd.ExcelFile(url)
    size_df      = pd.read_excel(xls, sheet_name="Pump Size")
    features_df  = pd.read_excel(xls, sheet_name="Features")
    materials_df = pd.read_excel(xls, sheet_name="Materials")
    materials_df = materials_df.drop_duplicates(subset=["Material Type", "Prefix", "Name"]).reset_index(drop=True)
    return size_df, features_df, materials_df

size_df, features_df, materials_df = load_config_data()
material_types = materials_df["Material Type"].dropna().unique().tolist()

# --- 4) Selezione parte (solo due parti per ora)
part = st.selectbox("Seleziona il tipo di parte da configurare:", [
    "Shaft, Pump",
    "Gasket, Flat"
])
st.markdown("---")

# --- 5) SHAFT, PUMP
if part == "Shaft, Pump":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        model       = st.text_input("Product/Pump Model", key="shaft_model")
        size_pump   = st.text_input("Product Pump Size", key="shaft_size")
        feat1       = st.text_input("Additional features 1", key="shaft_feat1")
        feat2       = st.text_input("Additional features 2", key="shaft_feat2")
        brg_type    = st.text_input("Brg. type", key="shaft_brg_type")
        brg_size    = st.text_input("Brg. Size", key="shaft_brg_size")
        diameter    = st.number_input("Max diameter (mm)", min_value=0.0, step=0.1, key="shaft_diameter")
        length      = st.number_input("Max length (mm)", min_value=0.0, step=0.1, key="shaft_length")
        dwg_shaft   = st.text_input("Dwg/doc", key="shaft_dwg")
        note_shaft  = st.text_area("Note", key="shaft_note")
        mtype_shaft = st.selectbox("Material Type", ["" ] + material_types, key="shaft_mtype")

        df_pref_shaft = materials_df[
            (materials_df["Material Type"] == mtype_shaft) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_shaft = sorted(df_pref_shaft["Prefix"].unique()) if mtype_shaft != "MISCELLANEOUS" else []
        mprefix_shaft  = st.selectbox("Material Prefix", ["" ] + prefixes_shaft, key="shaft_mprefix")

        if mtype_shaft == "MISCELLANEOUS":
            names_shaft = materials_df[
                materials_df["Material Type"] == mtype_shaft
            ]["Name"].dropna().tolist()
        else:
            names_shaft = materials_df[
                (materials_df["Material Type"] == mtype_shaft) &
                (materials_df["Prefix"] == mprefix_shaft)
            ]["Name"].dropna().tolist()
        mname_shaft = st.selectbox("Material Name", ["" ] + names_shaft, key="shaft_mname")

        if st.button("Genera Output", key="gen_shaft"):
            materiale_shaft = (
                f"{mtype_shaft} {mprefix_shaft} {mname_shaft}".strip()
                if mtype_shaft != "MISCELLANEOUS" else mname_shaft
            )
            match_shaft = materials_df[
                (materials_df["Material Type"] == mtype_shaft) &
                (materials_df["Prefix"] == mprefix_shaft) &
                (materials_df["Name"] == mname_shaft)
            ]
            codice_fpd_shaft = match_shaft["FPD Code"].values[0] if not match_shaft.empty else ""
            descr_shaft = (
                f"SHAFT - MODEL: {model}, SIZE: {size_pump}, Ø{diameter}x{length}mm, "
                f"BRG: {brg_type} {brg_size}, FEATURES: {feat1}, {feat2}, NOTE: {note_shaft}"
            )

            st.session_state["output"] = {
                "Item": "40231…",
                "Description": descr_shaft,
                "Identificativo": "2100-SHAFT",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ALBERO",
                "Disegno": dwg_shaft,
                "Material": materiale_shaft,
                "FPD material code": codice_fpd_shaft,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "25_SHAFTS",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output" in st.session_state:
            for k, v in st.session_state.output.items():
                if k == "Description":
                    st.text_area(k, value=v, height=80, key=f"shaft_{k}")
                else:
                    st.text_input(k, value=v, key=f"shaft_{k}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_shaft = st.radio(
            "Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="shaft_dl_mode"
        )
        item_code_shaft = st.text_input("Codice item", key="shaft_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_shaft"):
            if not item_code_shaft:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data_shaft = st.session_state["output"]
                def get_val_shaft(key):
                    val = data_shaft.get(key, "").strip()
                    return val if val else "."

                dataload_fields_shaft = [
                    "\\%FN", item_code_shaft,
                    "\\%TC", get_val_shaft("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_shaft("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_shaft("Identificativo"), "TAB",
                    get_val_shaft("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_shaft('ERP_L1')}.{get_val_shaft('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_shaft("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_shaft("Catalog"), "TAB", "TAB", "TAB",
                    get_val_shaft("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_shaft("FPD material code"), "TAB",
                    get_val_shaft("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_shaft("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_shaft("Quality") if get_val_shaft("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_shaft("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_shaft("To supplier") if get_val_shaft("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_shaft = "\t".join(dataload_fields_shaft)
                st.text_area("Anteprima (per copia manuale)", dataload_string_shaft, height=200)

                csv_buffer_shaft = io.StringIO()
                writer_shaft = csv.writer(csv_buffer_shaft, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_shaft:
                    writer_shaft.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_shaft.getvalue(),
                    file_name=f"dataload_{item_code_shaft}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")


# --- 6) GASKET, FLAT
if part == "Gasket, Flat":
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: INPUT
    with col1:
        st.subheader("✏️ Input")
        thickness_flat = st.number_input("Thickness (mm)", min_value=0.0, step=0.1, key="flat_thk")
        uom_flat       = st.selectbox("UOM", ["mm", "inches"], key="flat_uom")
        dwg_flat       = st.text_input("Dwg/doc number", key="flat_dwg")
        mtype_flat     = st.selectbox("Material Type", ["" ] + material_types, key="flat_mtype")

        df_pref_flat = materials_df[
            (materials_df["Material Type"] == mtype_flat) &
            (materials_df["Prefix"].notna())
        ]
        prefixes_flat = sorted(df_pref_flat["Prefix"].unique()) if mtype_flat != "MISCELLANEOUS" else []
        mprefix_flat  = st.selectbox("Material Prefix", ["" ] + prefixes_flat, key="flat_mprefix")

        if mtype_flat == "MISCELLANEOUS":
            names_flat = materials_df[
                materials_df["Material Type"] == mtype_flat
            ]["Name"].dropna().tolist()
        else:
            names_flat = materials_df[
                (materials_df["Material Type"] == mtype_flat) &
                (materials_df["Prefix"] == mprefix_flat)
            ]["Name"].dropna().tolist()
        mname_flat = st.selectbox("Material Name", ["" ] + names_flat, key="flat_mname")

        if st.button("Genera Output", key="gen_flat"):
            materiale_flat = (
                f"{mtype_flat} {mprefix_flat} {mname_flat}".strip()
                if mtype_flat != "MISCELLANEOUS" else mname_flat
            )
            match_flat = materials_df[
                (materials_df["Material Type"] == mtype_flat) &
                (materials_df["Prefix"] == mprefix_flat) &
                (materials_df["Name"] == mname_flat)
            ]
            codice_fpd_flat = match_flat["FPD Code"].values[0] if not match_flat.empty else ""
            descr_flat = f"GASKET, FLAT - THK: {thickness_flat}{uom_flat}, MATERIAL: {materiale_flat}"

            st.session_state["output"] = {
                "Item": "50158…",
                "Description": descr_flat,
                "Identificativo": "4590-GASKET",
                "Classe ricambi": "1-2-3",
                "Categories": "FASCIA ITE 5",
                "Catalog": "ARTVARI",
                "Disegno": dwg_flat,
                "Material": materiale_flat,
                "FPD material code": codice_fpd_flat,
                "Template": "FPD_BUY_2",
                "ERP_L1": "55_GASKETS_OR_SEAL",
                "ERP_L2": "20_OTHER",
                "To supplier": "",
                "Quality": ""
            }

    # COLONNA 2: OUTPUT
    with col2:
        st.subheader("📤 Output")
        if "output" in st.session_state:
            for k, v in st.session_state.output.items():
                if k == "Description":
                    st.text_area(k, value=v, height=80, key=f"flat_{k}")
                else:
                    st.text_input(k, value=v, key=f"flat_{k}")

    # COLONNA 3: DATALOAD
    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_flat = st.radio(
            "Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="flat_dl_mode"
        )
        item_code_flat = st.text_input("Codice item", key="flat_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_flat"):
            if not item_code_flat:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data_flat = st.session_state["output"]
                def get_val_flat(key):
                    val = data_flat.get(key, "").strip()
                    return val if val else "."

                dataload_fields_flat = [
                    "\\%FN", item_code_flat,
                    "\\%TC", get_val_flat("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_flat("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_flat("Identificativo"), "TAB",
                    get_val_flat("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_flat('ERP_L1')}.{get_val_flat('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_flat("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_flat("Catalog"), "TAB", "TAB", "TAB",
                    get_val_flat("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_flat("FPD material code"), "TAB",
                    get_val_flat("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_flat("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_flat("Quality") if get_val_flat("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_flat("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_flat("To supplier") if get_val_flat("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_flat = "\t".join(dataload_fields_flat)
                st.text_area("Anteprima (per copia manuale)", dataload_string_flat, height=200)

                csv_buffer_flat = io.StringIO()
                writer_flat = csv.writer(csv_buffer_flat, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_flat:
                    writer_flat.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_flat.getvalue(),
                    file_name=f"dataload_{item_code_flat}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")

# --- Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center;'><small>v1.0 • © 2025 Flowserve Desio Order Engineering</small></div>",
    unsafe_allow_html=True
)
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)
