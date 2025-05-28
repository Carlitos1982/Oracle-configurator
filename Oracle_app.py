import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(layout="wide", page_title="Oracle Item Setup - Web App")

# CSS per correggere il layout su iOS (cerchi bianchi) e migliorare l'estetica
st.markdown("""
    <style>
        /* Correzione estetica selectbox su iOS */
        div[data-baseweb="select"] > div {
            padding: 0.25rem !important;
        }

        /* Ripristino scritta rotazione su schermo stretto */
        @media (max-width: 768px) {
            .rotate-message {
                display: block;
                color: red;
                font-weight: bold;
                font-size: 1.1em;
                text-align: center;
                margin-top: 10px;
            }
        }

        @media (min-width: 769px) {
            .rotate-message {
                display: none;
            }
        }
    </style>
    <div class="rotate-message">📱 Ruota lo smartphone in orizzontale per una migliore visualizzazione</div>
""", unsafe_allow_html=True)

# Esempio layout base (puoi sostituirlo con il tuo contenuto attuale)
col1, col2, col3 = st.columns(3)

with col1:
    st.header("🔧 Input")
    st.number_input("Thickness", min_value=0.0, step=0.1)
    st.selectbox("UOM", ["mm", "inches"])
    st.text_input("Dwg/doc number")
    st.selectbox("Material Type", ["ASTM", "EN", "MISCELLANEOUS"])
    st.selectbox("Material Prefix", ["A", "B", "C"])
    st.selectbox("Material Name", ["316L", "304", "DUPLEX"])
    st.button("Genera Output")

with col2:
    st.header("📤 Output")
    st.text_input("Item", value="50158…")
    st.text_area("Description", value="GASKET, FLAT - THK: 0.1mm, MATERIAL:")

with col3:
    st.header("🧾 DataLoad")
    st.radio("Modalità operazione", ["Creazione item", "Aggiornamento item"])
    st.text_input("Item Number", placeholder="Es. 50158-0001")
    st.text_area("Stringa per DataLoad")