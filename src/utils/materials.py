import streamlit as st
import pandas as pd


def render_material_selector(prefix: str, material_types, materials_df):
    mtype = st.selectbox("Material Type", [""] + material_types, key=f"{prefix}_mtype")
    pref_df = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())]
    prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox("Material Prefix", [""] + prefixes, key=f"{prefix}_mprefix")
    if mtype == "MISCELLANEOUS":
        names = materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
    else:
        names = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix)]["Name"].dropna().tolist()
    mname = st.selectbox("Material Name", [""] + names, key=f"{prefix}_mname")
    material_note = st.text_area("Material note", height=60, key=f"{prefix}_matnote")
    match = materials_df[(materials_df["Material Type"] == mtype) & (materials_df["Prefix"] == mprefix) & (materials_df["Name"] == mname)]
    codice_fpd = match["FPD Code"].values[0] if not match.empty else ""
    materiale = f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
    return materiale, codice_fpd, material_note, mtype, mprefix, mname


def select_material(materials_df: pd.DataFrame, key_prefix: str):
    """Render a material selection widget and return chosen values.

    This helper encapsulates the common logic used throughout the app for
    material type/prefix/name lookup and FPD code retrieval.  It exposes a
    uniform interface so callers only need to provide the dataframe and a key
    prefix for the Streamlit widgets.

    Parameters
    ----------
    materials_df: pandas.DataFrame
        DataFrame containing columns ``Material Type``, ``Prefix``, ``Name``
        and ``FPD Code``.
    key_prefix: str
        Prefix used to generate unique keys for the Streamlit widgets.

    Returns
    -------
    tuple
        ``(materiale, fpd_code, material_note, mtype, mprefix, mname)`` where
        ``materiale`` is the human readable material string and ``fpd_code`` is
        the associated FPD code (empty string if not found).
    """

    material_types = materials_df["Material Type"].dropna().unique().tolist()

    mtype = st.selectbox(
        "Material Type", [""] + material_types, key=f"{key_prefix}_mtype"
    )

    pref_df = materials_df[
        (materials_df["Material Type"] == mtype) & (materials_df["Prefix"].notna())
    ]
    prefixes = sorted(pref_df["Prefix"].unique()) if mtype != "MISCELLANEOUS" else []
    mprefix = st.selectbox(
        "Material Prefix", [""] + prefixes, key=f"{key_prefix}_mprefix"
    )

    if mtype == "MISCELLANEOUS":
        names = (
            materials_df[materials_df["Material Type"] == mtype]["Name"].dropna().tolist()
        )
    else:
        names = materials_df[
            (materials_df["Material Type"] == mtype)
            & (materials_df["Prefix"] == mprefix)
        ]["Name"].dropna().tolist()

    mname = st.selectbox(
        "Material Name", [""] + names, key=f"{key_prefix}_mname"
    )
    material_note = st.text_area(
        "Material note", height=60, key=f"{key_prefix}_matnote"
    )

    match = materials_df[
        (materials_df["Material Type"] == mtype)
        & (materials_df["Prefix"] == mprefix)
        & (materials_df["Name"] == mname)
    ]
    fpd_code = match["FPD Code"].values[0] if not match.empty else ""

    materiale = (
        f"{mtype} {mprefix} {mname}".strip() if mtype != "MISCELLANEOUS" else mname
    )

    return materiale, fpd_code, material_note, mtype, mprefix, mname


def get_fpd_code(materials_df: pd.DataFrame, mat_type, mat_prefix, mat_name):
    row = materials_df[
        (materials_df["Material Type"] == mat_type)
        & (materials_df["Prefix"] == mat_prefix)
        & (materials_df["Name"] == mat_name)
    ]
    if not row.empty and "FPD Code" in row.columns:
        return row.iloc[0]["FPD Code"]
    return "NOT AVAILABLE"
