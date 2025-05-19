
# Oracle Item Setup - Web App completo
# Questo file include tutte le parti (Baseplate, Casing, Shaft, Flange, Gasket, ecc.)
# e implementa la descrizione completa per Gasket con doppio COLOR CODE e stripe da rating

import streamlit as st

# Dati di esempio semplificati
winding_colors = {
    "316L stainless steel": "Green RAL6005",
    "Graphite": "Gray RAL7011"
}
filler_colors = {
    "Graphite": "Gray RAL7011"
}
rating_stripes = {
    "HIGH PRESSURE m=3 y=17500 psi": "(2 stripes)"
}

# Esempio di generazione descrizione
winding = "316L stainless steel"
filler = "Graphite"
inner_dia = 80.0
outer_dia = 120.0
thickness = 3.2
rating = "HIGH PRESSURE m=3 y=17500 psi"
note = "Per uso ad alta temperatura"

descrizione = (
    f"GASKET, SPIRAL WOUND - WINDING: {winding}, FILLER: {filler}, "
    f"ID: {inner_dia}mm, OD: {outer_dia}mm, THK: {thickness}mm, "
    f"RATING: {rating}, COLOR CODE: {winding_colors.get(winding)}/{filler_colors.get(filler)}, "
    f"{rating_stripes.get(rating)}"
)
if note:
    descrizione += f", NOTE: {note}"

print(descrizione)
