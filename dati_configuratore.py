# === DATI MODELLI E TAGLIE ===
size_options = {
    "HPX": ["1.5HPX15A", "2HPX10A", "3HPX12B", "4HPX13A", "6HPX14A"],
    "HDX": ["4HDX14A", "6HDX13A", "8HDX11B"],
    "HED": ["1.5HED11", "2HED13", "3HED15", "4HED16"],
    "HZM": ["1HZM10", "2HZM12"],
    "HZS": ["1HZS8", "2HZS9"]
}

# === DATI FEATURES PER MODELLO ===
features_options = {
    "HPX": {
        "features1": ["STD", "INDUCER", "EXPANDED NOZZLE"],
        "features2": ["PLUGGED DISCHARGE NOZZLE", "BACK FLUSH"]
    },
    "HDX": {
        "features1": ["TOP-TOP", "SIDE-TOP", "END-SIDE"],
        "features2": None
    },
    "HED": {
        "features1": ["TOP-TOP", "SIDE-SIDE"],
        "features2": ["HEAVY", "BYPASS"]
    },
    "HZM": {
        "features1": ["COMPACT", "VERTICAL"],
        "features2": ["COOLING JACKET"]
    },
    "HZS": {
        "features1": ["SMALL", "SINGLE STAGE"],
        "features2": None
    }
}

# === MATERIALI ===
material_options = {
    "ASTM": {
        "A": ["A105", "A216 WCB"],
        "B": ["B564 UNS N06625", "B148 C95800"]
    },
    "EN": {
        "C": ["1.4301", "1.4408"],
        "D": ["1.0619", "1.7035"]
    },
    "MISCELLANEOUS": {
        None: ["BRONZE", "PLASTIC", "COMPOSITE"]
    }
}
