import streamlit as st
from src.utils.materials import render_material_selector
from src.utils.quality import assemble_quality_tags
from src.utils.dataload import render_dataload_panel


def render(size_df, features_df, materials_df, material_types):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="casing_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="casing_size")

        feature_1 = ""
        special = ["HDO", "DMX", "WXB", "WIK"]
        if model not in special:
            f1_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features1")
            ]["Feature"].dropna().tolist()
            feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="casing_f1")

        feature_2 = ""
        if model in ["HPX", "HED"]:
            f2_list = features_df[
                (features_df["Pump Model"] == model) &
                (features_df["Feature Type"] == "features2")
            ]["Feature"].dropna().tolist()
            feature_2 = st.selectbox("Additional Feature 2", [""] + f2_list, key="casing_f2")

        note = st.text_area("Note", height=80, key="casing_note")
        dwg = st.text_input("Dwg/doc number", key="casing_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = render_material_selector(
            "casing", material_types, materials_df
        )

        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="casing_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="casing_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="casing_overlay")
        hvof = st.checkbox("HVOF coating?", key="casing_hvof")
        water = st.checkbox("Water service?", key="casing_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="casing_stamicarbon")

        if st.button("Generate Output", key="casing_gen"):
            tag_string, quality = assemble_quality_tags(
                hf_service,
                tmt_service,
                overlay,
                hvof,
                water,
                stamicarbon,
                extra=[
                    (
                        "[CORP-ENG-0194]",
                        "CORP-ENG-0194 - Inspection of Flat and Raised Face Flanges G1-3",
                    )
                ],
                mat_prefix=mprefix,
                mat_name=mname,
            )
            descr_parts = ["CASING, PUMP"]
            for val in [model, size, feature_1, feature_2, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string
            st.session_state["output_data"] = {
                "Item": "40201…",
                "Description": descr,
                "Identificativo": "1100-CASING",
                "Classe ricambi": "3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "CORPO",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "17_CASING",
                "To supplier": "",
                "Quality": quality,
            }

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for k, v in st.session_state["output_data"].items():
                if k in ["Quality", "To supplier", "Description"]:
                    st.text_area(k, value=v, height=200)
                else:
                    st.text_input(k, value=v)

    with col3:
        render_dataload_panel(
            item_code_key="casing_item_code",
            create_btn_key="gen_dl_casing",
            update_btn_key="gen_upd_casing",
        )
