# --- FLANGE, PIPE
elif selected_part == "Flange, Pipe":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✏️ Input")
        flange_type = st.selectbox("Type", ["SW", "BW"], key="flange_type")
        size_fp     = st.selectbox(
            "Size",
            ['1/8”','1/4”','3/8”','1/2”','3/4”','1”','1-1/4”','1-1/2”','2”','2-1/2”','3”','4”'],
            key="flange_size"
        )
        face_type   = st.selectbox("Face Type", ["RF", "FF", "RJ"], key="flange_face")
        flange_cls  = st.selectbox("Class", ["150", "300", "600", "1500", "2500"], key="flange_class")

        # AVVISO IN EVIDENZA
        if flange_cls in ["1500", "2500"] and face_type != "RJ":
            st.markdown(
                "<div style='background-color:#ffcccc; padding:0.8rem; border:2px solid #ff0000; border-radius:6px;'>"
                "<strong>⚠️ ATTENZIONE:</strong> Per classi <strong>1500</strong> o <strong>2500</strong> "
                "È FORTEMENTE RACCOMANDATO USARE il tipo di faccia <strong>RJ</strong>. "
                "Verificare lo scopo di fornitura prima di procedere."
                "</div>",
                unsafe_allow_html=True
            )

        schedule_fp = st.selectbox(
            "Schedule",
            ["5","10","20","30","40","60","80","100","120","140","160"],
            key="flange_schedule"
        )
        flange_mat  = st.selectbox(
            "Flange Material",
            ["A105", "A106-GR B", "UNS-S31803", "UNS-S32760", "A350 LF2", "A182-F316L",
             "ALLOY 825", "GALVANIZED CARBON STEEL"],
            key="flange_material"
        )
        note_fp = st.text_area("Note (opzionale)", height=80, key="note_fp")
        dwg_fp  = st.text_input("Dwg/doc number", key="dwg_fp")

        if st.button("Genera Output", key="gen_flange"):
            descr_fp = (
                f"FLANGE, PIPE - TYPE: {flange_type}, SIZE: {size_fp}, "
                f"FACE TYPE: {face_type}, CLASS: {flange_cls}, SCHEDULE: {schedule_fp}, MATERIAL: {flange_mat}"
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

    with col2:
        st.subheader("📤 Output")
        if "output_data" in st.session_state:
            for campo, valore in st.session_state["output_data"].items():
                if campo == "Description":
                    st.text_area(campo, value=valore, height=80, key=f"flange_{campo}")
                else:
                    st.text_input(campo, value=valore, key=f"flange_{campo}")

    with col3:
        st.subheader("🧾 DataLoad")
        dataload_mode_fp = st.radio("Tipo operazione:", ["Crea nuovo item", "Aggiorna item"], key="fp_dl_mode")
        item_code_fp = st.text_input("Codice item", key="fp_item_code")

        if st.button("Genera stringa DataLoad", key="gen_dl_fp"):
            if not item_code_fp:
                st.error("❌ Inserisci prima il codice item per generare la stringa DataLoad.")
            elif "output_data" not in st.session_state:
                st.error("❌ Genera prima l'output dalla colonna 1.")
            else:
                data = st.session_state["output_data"]
                def get_val_fp(key):
                    val = data.get(key, "").strip()
                    return val if val else "."

                dataload_fields_fp = [
                    "\\%FN", item_code_fp,
                    "\\%TC", get_val_fp("Template"), "TAB",
                    "\\%D", "\\%O", "TAB",
                    get_val_fp("Description"), "TAB", "TAB", "TAB", "TAB", "TAB", "TAB",
                    get_val_fp("Identificativo"), "TAB",
                    get_val_fp("Classe ricambi"), "TAB",
                    "\\%O", "\\^S",
                    "\\%TA", "TAB",
                    f"{get_val_fp('ERP_L1')}.{get_val_fp('ERP_L2')}", "TAB", "FASCIA ITE", "TAB",
                    get_val_fp("Categories").split()[-1], "\\^S", "\\^{F4}",
                    "\\%TG", get_val_fp("Catalog"), "TAB", "TAB", "TAB",
                    get_val_fp("Disegno"), "TAB", "\\^S", "\\^{F4}",
                    "\\%TR", "MATER+DESCR_FPD", "TAB", "TAB",
                    get_val_fp("FPD material code"), "TAB",
                    get_val_fp("Material"), "\\^S", "\\^{F4}",
                    "\\%VA", "TAB",
                    get_val_fp("Quality"), "TAB", "TAB", "TAB", "TAB",
                    get_val_fp("Quality") if get_val_fp("Quality") != "." else ".", "\\^S",
                    "\\%FN", "TAB",
                    get_val_fp("To supplier"), "TAB", "TAB", "TAB",
                    "Short Text", "TAB",
                    get_val_fp("To supplier") if get_val_fp("To supplier") != "." else ".", "\\^S", "\\^S", "\\^{F4}", "\\^S"
                ]

                dataload_string_fp = "\t".join(dataload_fields_fp)
                st.text_area("Anteprima (per copia manuale)", dataload_string_fp, height=200)

                csv_buffer_fp = io.StringIO()
                writer_fp = csv.writer(csv_buffer_fp, quoting=csv.QUOTE_MINIMAL)
                for riga in dataload_fields_fp:
                    writer_fp.writerow([riga])

                st.download_button(
                    label="💾 Scarica file CSV per Import Data",
                    data=csv_buffer_fp.getvalue(),
                    file_name=f"dataload_{item_code_fp}.csv",
                    mime="text/csv"
                )

                st.caption("📂 Usa questo file in **DataLoad Classic → File → Import Data...**")
