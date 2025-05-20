elif selected_part == "Bolt, Eye":
    st.subheader("Configurazione - Bolt, Eye")
    # THREAD
    thread_options = [
        '5/16"-18UNC','3/8"-16UNC','1/2"-13UNC','3/4"-16UNF',
        '7/8"-9UNC','7/8"-14UNF','1"-8UNC','1"-12UNF',
        '1-1/8"-7UNC','1-1/8"-12UNF','1-1/4"-7UNC','1-1/4"-12UNF',
        '1-3/8"-6UNC','1-3/8"-12UNF','1-1/2"-6UNC','1-1/2"-12UNF',
        '2"-4.5UNC','2"-12UNC','2-1/2"-12UNF','3"-8UNC',
        '4"-8UNC','M6x1','M8x1.25','M10x1.5','M12x1.75','M14x2',
        'M16x2','M18x2.5','M20x2.5','M22x2.5','M24x3','M27x3',
        'M30x3.5','M33x3.5','M36x4','M39x4','M42x4.5','M45x4.5',
        'M48x5','M52x5','M56x5.5','M60x5.5','M64x6','M68x6',
        'M72x6','M76x6','M80x6','M85x6','M90x6','M95x6'
    ]
    thread_size = st.selectbox("Thread Type/Size", thread_options, key="bolt_thread")

    # LENGTH e UOM
    len_uom = st.selectbox("LenUOM", ["in", "mm"], key="bolt_lenuom")
    in_lengths = [
        '1/8"','1/4"','3/8"','5/16"','1/2"','3/4"','1"','1-1/8"',
        '1-1/4"','1-3/8"','1-1/2"','1-3/4"','2"','2-1/8"','2-1/4"',
        '2-3/8"','2-1/2"','2-3/4"','3"','3-1/8"','3-1/4"','3-3/8"',
        '3-1/2"','3-3/4"','4"','4-1/8"','4-1/4"','4-3/8"','4-1/2"',
        '4-3/4"'
    ]
    mm_lengths = list(range(50, 201, 5))
    length = st.selectbox("Length", in_lengths if len_uom=="in" else mm_lengths, key="bolt_length")

    note_bolt    = st.text_input("Note", key="bolt_note")

    # MATERIAL
    mtype_bolt   = st.selectbox("Type", [""] + material_types, key="bolt_mtype")
    prefixes     = (
        sorted(materials_df[
            (materials_df["Material Type"]==mtype_bolt)&
            (materials_df["Prefix"].notna())
        ]["Prefix"].unique())
        if mtype_bolt in ["ASTM","EN"] else []
    )
    mprefix_bolt = st.selectbox("Prefix (only if ASTM or EN)", [""] + prefixes, key="bolt_mprefix")
    if mtype_bolt == "MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"]==mtype_bolt]["Name"].dropna().tolist()
    else:
        names = materials_df[
            (materials_df["Material Type"]==mtype_bolt)&
            (materials_df["Prefix"]==mprefix_bolt)
        ]["Name"].dropna().tolist()
    mname_bolt   = st.selectbox("Name", [""] + names, key="bolt_mname")
    matfeat_bolt = st.text_input("Material add. Features", key="bolt_matfeat")

    if st.button("Genera Output", key="gen_bolt"):
        # Calcolo FPD Code
        if mtype_bolt != "MISCELLANEOUS":
            materiale_bolt = f"{mtype_bolt} {mprefix_bolt} {mname_bolt}".strip()
            match_bolt     = materials_df[
                (materials_df["Material Type"]==mtype_bolt)&
                (materials_df["Prefix"]==mprefix_bolt)&
                (materials_df["Name"]==mname_bolt)
            ]
        else:
            materiale_bolt = mname_bolt
            match_bolt     = materials_df[
                (materials_df["Material Type"]==mtype_bolt)&
                (materials_df["Name"]==mname_bolt)
            ]
        codice_fpd_bolt = match_bolt["FPD Code"].values[0] if not match_bolt.empty else ""

        # Description
        descr_bolt = (
            f"Bolt, Eye; THREAD: {thread_size}; L: {length}{len_uom}; NOTE: {note_bolt}"
        )

        st.session_state["output_data"] = {
            "Item":               "50125…",
            "Description":        descr_bolt,
            "Identificativo":     "3020-EYE BOLT",
            "Classe ricambi":     "1-2-3",
            "Categories":         "FASCIA ITE 5",
            "Material":           materiale_bolt,
            "FPD material code":  codice_fpd_bolt,
            "Template":           "FPD_BUY_2",
            "ERP_L1":             "23_BOLT_HARDWARE",
            "ERP_L2":             "12_EYE_BOLT",
            "To supplier":        "",
            "Quality":            ""
        }