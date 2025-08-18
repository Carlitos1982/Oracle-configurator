"""Shared constant values for the Oracle configurator app."""

# ------------------ Bearing descriptive dictionaries ------------------
base_series_desc = {
    "60":  "Deep groove ball bearing – light series",
    "62":  "Deep groove ball bearing – medium series",
    "63":  "Deep groove ball bearing – heavy series",
    "72":  "Angular contact ball bearing – 15°",
    "73":  "Angular contact ball bearing – 40°",
    "32":  "Double-row angular contact ball bearing",
    "12":  "Self-aligning ball bearing – light series",
    "22":  "Self-aligning ball bearing – medium series",
    "NU":  "Cylindrical roller bearing (NU)",
    "NUP": "Cylindrical roller bearing (NUP)",
    "NJ":  "Cylindrical roller bearing (NJ)",
    "222": "Spherical roller bearing – 222 series",
    "223": "Spherical roller bearing – 223 series",
    "230": "Spherical roller bearing – 230 series",
    "231": "Spherical roller bearing – 231 series",
    "302": "Tapered roller bearing – 302 series",
    "303": "Tapered roller bearing – 303 series",
    "320": "Tapered roller bearing – 320 series",
}

design_desc = {
    "BE": "40° AC, paired",
    "B": "40° AC",
    "AC": "25° AC",
    "A": "30° AC",
    "E": "high capacity",
    "EC": "high capacity",
}

pairing_desc = {
    "CB": "light preload",
    "CC": "medium preload",
    "CD": "heavy preload",
    "GA": "paired",
    "GB": "paired",
    "GC": "paired",
}

cage_desc = {
    "TN9": "polyamide cage",
    "J": "pressed steel cage",
    "M": "machined brass cage",
    "MA": "brass cage",
    "CA": "brass cage",
    "CC": "polyamide cage",
}

clearance_desc = {
    "C2": "reduced clearance",
    "CN": "normal clearance",
    "C3": "increased clearance",
    "C4": "large clearance",
    "C5": "very large clearance",
}

tolerance_desc = {
    "P0": "normal tol.",
    "P6": "P6 tol.",
    "P5": "P5 tol.",
    "P4": "P4 tol.",
}

heat_desc = {
    "S0": "stabilized S0",
    "S1": "S1",
    "S2": "S2",
    "S3": "S3",
}

grease_desc = {
    "VT143": "grease VT143",
    "VT378": "grease VT378",
    "MT33": "grease MT33",
    "GJN": "grease GJN",
}

vibration_desc = {
    "V1": "V1 vib.",
    "V2": "V2 vib.",
    "V3": "V3 vib.",
    "V4": "V4 vib.",
    "VA201": "VA201 vib.",
    "VA208": "VA208 vib.",
    "VA228": "VA228 vib.",
}

# ------------------ Dowel pin dimensions ------------------
dowel_diameters_mm_raw = [
    "Ø1", "Ø1.5", "Ø2", "Ø2.5", "Ø3", "Ø4", "Ø5", "Ø6", "Ø8", "Ø10",
    "Ø12", "Ø14", "Ø16", "Ø18", "Ø20", "Ø22", "Ø25", "Ø30",
]

dowel_lengths_mm = [
    "4mm", "5mm", "6mm", "8mm", "10mm", "12mm", "16mm", "20mm", "25mm", "30mm",
    "35mm", "40mm", "45mm", "50mm", "60mm", "70mm", "80mm", "90mm", "100mm",
]

dowel_diameters_in = [
    '1/16"', '3/32"', '1/8"', '5/32"', '3/16"', '7/32"', '1/4"', '9/32"',
    '5/16"', '3/8"', '7/16"', '1/2"', '9/16"', '5/8"', '3/4"', '7/8"', '1"',
]

dowel_lengths_in = [
    '1/4"', '3/8"', '1/2"', '5/8"', '3/4"', '1"', '1-1/4"', '1-1/2"',
    '1-3/4"', '2"', '2-1/4"', '2-1/2"', '3"', '3-1/2"', '4"',
]

# ------------------ Gasket spiral wound materials ------------------
winding_materials = [
    "SS316L",
    "SS304",
    "MONEL",
    "INCONEL",
    "DUPLEX",
    "HASTELLOY C276",
]

filler_materials = [
    "GRAPHITE",
    "PTFE",
    "MICA",
    "CERAMIC",
    "GLASS",
    "SS304",
]

color_codes = {
    "SS316L": "Green",
    "SS304": "Red",
    "MONEL": "Blue",
    "INCONEL": "Yellow",
    "DUPLEX": "Purple",
    "HASTELLOY C276": "Orange",
    "GRAPHITE": "Black",
    "PTFE": "White",
    "MICA": "Gray",
    "CERAMIC": "Light Gray",
    "GLASS": "Clear",
}
