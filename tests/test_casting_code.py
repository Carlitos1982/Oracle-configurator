from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.materials import get_casting_code

def test_get_casting_code_missing_column():
    df = pd.DataFrame({"FPD Code": ["123"]})
    assert get_casting_code(df) == "XX"

def test_get_casting_code_present():
    df = pd.DataFrame({"Casting code": ["AB12"]})
    assert get_casting_code(df) == "12"

def test_get_casting_code_nan_value():
    df = pd.DataFrame({"Casting code": [pd.NA]})
    assert get_casting_code(df) == "XX"
