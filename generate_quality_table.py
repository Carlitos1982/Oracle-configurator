Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> # tools/generate_quality_table.py
... from itertools import product
... import pandas as pd
... from src.utils.quality import build_quality_tags
... 
... FLAGS = [
...     ("hf_service", "HF service"),
...     ("tmt_service", "TMT/HVOF protection"),
...     ("overlay", "Overlay / laser hardening"),
...     ("hvof", "HVOF coating"),
...     ("water", "Water service"),
...     ("stamicarbon", "Stamicarbon service"),
... ]
... 
... def generate_table(path="quality_combinations.xlsx"):
...     rows = []
...     for combo in product([False, True], repeat=len(FLAGS)):
...         options = {key: val for (key, _), val in zip(FLAGS, combo)}
...         tags, lines = build_quality_tags(options)
...         triggers = ", ".join(label for (key, label), val in zip(FLAGS, combo) if val)
...         rows.append({
...             **options,
...             "Triggers": triggers,
...             "Tags": tags,
...             "Quality lines": lines,
...         })
... 
...     pd.DataFrame(rows).to_excel(path, index=False)
... 
... if __name__ == "__main__":
...     generate_table()
