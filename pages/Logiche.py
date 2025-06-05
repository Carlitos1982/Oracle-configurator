
import streamlit as st
import pandas as pd

st.set_page_config(page_title="📘 Logiche Configuratore", layout="wide")

st.title("📘 Documentazione Logiche - Oracle Item Setup")

st.markdown(
    '''
    Questa sezione mostra tutte le logiche di configurazione delle parti, comprese:
    - **Campi di Input e Output**
    - **Sintassi della Descrizione**
    - **Quality default e condizionali**
    - **Logiche checkbox (HF, Stamicarbon, Overlay, ecc.)**
    - **Note per la generazione DataLoad**

    Puoi anche scaricare la tabella in formato Excel.
    '''
)

# Carica il file Excel definitivo
file_path = "Logiche_Item_Config.xlsx"
df = pd.read_excel(file_path)

# Mostra tabella interattiva
st.dataframe(df, use_container_width=True)

# Pulsante download
with open(file_path, "rb") as f:
    st.download_button(
        label="📥 Scarica tabella logiche (Excel)",
        data=f,
        file_name="Logiche_Item_Config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
