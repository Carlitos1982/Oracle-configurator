elif selected_part == "Pin, Dowel":
    st.subheader("Configurazione - Pin, Dowel")

    # Input dimensioni
    diameter       = st.number_input("Diameter", min_value=0, step=1, format="%d", key="pin_diameter")
    uom_diameter   = st.selectbox("UOM", ["mm", "inches"], key="pin_uom_diameter")
    length         = st.number_input("Length", min_value=0, step=1, format="%d", key="pin_length")
    uom_length     = st.selectbox("UOM", ["mm", "inches"], key="pin_uom_length")

    # Standard (può restare vuoto)
    standard       = st.selectbox("Standard", [""] + ["ISO 2338"], key="pin_standard")

    # Campo Note (prima del materiale)
    note_pin       = st.text_area("Note (opzionale)", height=80, key="pin_note")

    # Selezione materiale
    mtype_pin      = st.selectbox("Material Type", [""] + material_types, key="mtype_pin")
    pref_df_pin    = materials_df[
        (materials_df["Material Type"] == mtype_pin) &
        (materials_df["Prefix"].notna())
    ]
    prefixes_pin   = sorted(pref_df_pin["Prefix"].unique()) if mtype_pin != "MISCELLANEOUS" else []
    mprefix_pin    = st.selectbox("Material Prefix", [""] + prefixes_pin, key="mprefix_pin")

    if mtype_pin == "MISCELLANEOUS":
        names_pin = materials_df[
            materials_df["Material Type"] == mtype_pin
        ]["Name"].dropna().drop_duplicates().tolist()
    else:
        names_pin = materials_df[
            (materials_df["Material Type"] == mtype_pin) &
            (materials_df["Prefix"] == mprefix_pin)
        ]["Name"].dropna().drop_duplicates().tolist()
    mname_pin      = st.selectbox("Material Name", [""] + names_pin, key="mname_pin")

    # Material Note
    material_note_pin = st.text_area("Material Note (opzionale)", height=80, key="pin_matnote")

    # Bottone di generazione con key univoca
    if st.button("Genera Output", key="gen_pin_dowel"):
        # Materiale e codice FPD
        if mtype_pin != "MISCELLANEOUS":
            materiale_pin = f"{mtype_pin} {mprefix_pin} {mname_pin}".strip()
            match_pin     = materials_df[
                (materials_df["Material Type"] == mtype_pin) &
                (materials_df["Prefix"] == mprefix_pin) &
                (materials_df["Name"] == mname_pin)
            ]
        else:
            materiale_pin = mname_pin
            match_pin     = materials_df[
                (materials_df["Material Type"] == mtype_pin) &
                (materials_df["Name"] == mname_pin)
            ]
        codice_fpd_pin = match_pin["FPD Code"].values[0] if not match_pin.empty else ""

        # Costruzione descrizione: note prima del materiale
        descr_pin = (
            f"PIN, DOWEL - DIAMETER: {int(diameter)}{uom_diameter}, "
            f"LENGTH: {int(length)}{uom_length}"
        )
        if standard:
            descr_pin += f", {standard}"
        if note_pin:
            descr_pin += f", {note_pin}"
        descr_pin += f", {materiale_pin}"
        if material_note_pin:
            descr_pin += f", {material_note_pin}"

        # Memorizzo l’output
        st.session_state["output_data"] = {
            "Item":               "56230…",
            "Description":        descr_pin,
            "Identificativo":     "6810-DOWEL PIN",
            "Classe ricambi":     "",
            "Categories":         "FASCIA ITE 5",
            "Catalog":            "",
            "Material":           materiale_pin,
            "FPD material code":  codice_fpd_pin,
            "Template":           "FPD_BUY_2",
            "ERP_L1":             "64_HARDWARE",
            "ERP_L2":             "14_PINS",
            "To supplier":        "",
            "Quality":            ""
        }