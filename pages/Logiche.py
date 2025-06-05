
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="📘 Logiche Configuratore", layout="wide")
st.title("📘 Documentazione Logiche - Oracle Item Setup")

st.markdown(
    """
    Questa sezione mostra tutte le logiche aggiornate del configuratore, comprese:
    - ✅ Campi di Input e Output
    - 🧠 Sintassi della Description
    - 📋 Qualità di default e condizionali
    - 🎯 Checkbox logiche (HF, Stamicarbon, Overlay, ecc.)
    - 🔁 Note per la stringa DataLoad

    Tutto aggiornato automaticamente. Puoi anche esportare in Excel.
    """
)

# --- LOGICHE DATI CENTRALIZZATI ---
logiche_data = [
    {
        "Part Name": "Baseplate, Pump",
        "Categoria": "Machined",
        "Input Fields": "Model, Size, Weight, Drawing, Note, Material Type, Prefix, Name, Material Note",
        "Output Fields": "Item, Identificativo, Categories, Catalog, Template, ERP_L1, ERP_L2, Material, FPD material code, Description, Quality",
        "Description Syntax": "[SQ53] [CORP-ENG-0234] [SQ172]",
        "Quality Default": "SQ 53 - HORIZONTAL PUMP BASEPLATES CHECKING PROCEDURE;\nCORP-ENG-0234 - Procedure for Baseplate Inspection J4-11",
        "Quality Condizionali": "SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION",
        "Checkbox Logiche": "Stamicarbon",
        "Dataload Note": "Codice generato automaticamente; solo creazione"
    },
    {
        "Part Name": "Shaft, Pump",
        "Categoria": "Machined",
        "Input Fields": "Model, Size, Brg type, Brg size, Max dia, Max length, Drawing, Note, Material Type, Prefix, Name, Material Note",
        "Output Fields": "Item, Identificativo, Categories, Catalog, Template, ERP_L1, ERP_L2, Material, FPD material code, Description, Quality",
        "Description Syntax": "[CORP-ENG-0115] [SQ60] [DE3513.014] [PQ72] [DE2500.002] [PI23] [SQ172]",
        "Quality Default": "CORP-ENG-0115 - General Surface Quality Requirements G1-1;\nSQ 60 - Procedura di Esecuzione del Run-Out;\nDE 3513.014 - Shaft Demagnetization",
        "Quality Condizionali": "PQ 72; DE 2500.002; PI 23; SQ 172",
        "Checkbox Logiche": "Overlay; HVOF; Water Service; Stamicarbon",
        "Dataload Note": "Richiede codice item; supporta creazione e aggiornamento"
    },
    {
        "Part Name": "Gasket, Spiral Wound",
        "Categoria": "Commercial",
        "Input Fields": "OD, ID, Thickness, Rating, Winding, Filler, Drawing, Note",
        "Output Fields": "Item, Identificativo, Categories, Template, ERP_L1, ERP_L2, Material, FPD material code, Description, Quality",
        "Description Syntax": "[SQ174] [SQ172]",
        "Quality Default": "SQ 174 - Casing/Cover pump spiral wound gaskets: Specification for Mechanical properties, applicable materials and dimensions",
        "Quality Condizionali": "SQ 172 - STAMICARBON - SPECIFICATION FOR MATERIAL OF CONSTRUCTION",
        "Checkbox Logiche": "Stamicarbon",
        "Dataload Note": "Codice item da inserire manualmente; solo creazione"
    }
]

# Mostra tabella
df = pd.DataFrame(logiche_data)
st.dataframe(df, use_container_width=True)

# Download dinamico
buffer = BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Scarica logiche in Excel",
    data=buffer,
    file_name="Logiche_Item_Config.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
