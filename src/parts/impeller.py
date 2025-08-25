import streamlit as st
from src.utils.materials import render_material_selector
from src.utils.quality import assemble_quality_tags
from src.utils.dataload import render_dataload_panel


def render(size_df, features_df, materials_df, material_types):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("✏️ Input")
        model = st.selectbox("Product Type", [""] + sorted(size_df["Pump Model"].dropna().unique()), key="imp_model")
        size_list = size_df[size_df["Pump Model"] == model]["Size"].dropna().tolist()
        size = st.selectbox("Pump Size", [""] + size_list, key="imp_size")

        f1_list = features_df[
            (features_df["Pump Model"] == model) &
            (features_df["Feature Type"] == "features1")
        ]["Feature"].dropna().tolist()
        feature_1 = st.selectbox("Additional Feature 1", [""] + f1_list, key="imp_feat1") if f1_list else ""

        note = st.text_area("Note", height=80, key="imp_note")
        dwg = st.text_input("Dwg/doc number", key="imp_dwg")

        materiale, codice_fpd, material_note, mtype, mprefix, mname = render_material_selector(
            "imp", material_types, materials_df
        )

        hf_service = st.checkbox("Is it an hydrofluoric acid alkylation service (lethal)?", key="imp_hf")
        tmt_service = st.checkbox("TMT/HVOF protection requirements?", key="imp_tmt")
        overlay = st.checkbox("DLD, PTAW, Laser Hardening, METCO, Ceramic Chrome?", key="imp_overlay")
        hvof = st.checkbox("HVOF coating?", key="imp_hvof")
        water = st.checkbox("Water service?", key="imp_water")
        stamicarbon = st.checkbox("Stamicarbon?", key="imp_stamicarbon")

        if st.button("Generate Output", key="imp_gen"):
            extra = []
            if mprefix == "A747_" and mname == "Tp. CB7Cu-1 (H1150 DBL)":
                extra.append(("[DE2980.001]", "DE2980.001 - Progettazione e Produzione giranti in 17-4 PH"))
            tag_string, quality = assemble_quality_tags(
                hf_service,
                tmt_service,
                overlay,
                hvof,
                water,
                stamicarbon,
                extra=extra,
                mat_prefix=mprefix,
                mat_name=mname,
            )
            descr_parts = ["IMPELLER, PUMP"]
            for val in [model, size, feature_1, note, materiale, material_note]:
                if val:
                    descr_parts.append(val)
            descr = "*" + " - ".join(descr_parts) + " " + tag_string
            st.session_state["output_data"] = {
                "Item": "40229…",
                "Description": descr,
                "Identificativo": "2200-IMPELLER",
                "Classe ricambi": "2-3",
                "Categories": "FASCIA ITE 4",
                "Catalog": "ARTVARI",
                "Disegno": dwg,
                "Material": materiale,
                "FPD material code": codice_fpd,
                "Template": "FPD_MAKE",
                "ERP_L1": "20_TURNKEY_MACHINING",
                "ERP_L2": "20_IMPELLER_DIFFUSER",
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
            item_code_key="imp_item_code",
            create_btn_key="gen_dl_imp",
            update_btn_key="gen_upd_imp",
        )
