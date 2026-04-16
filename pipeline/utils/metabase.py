# ============================================================
# utils/metabase.py — Semua extract data dari Metabase
# TIDAK ada transformasi di sini, murni tarik data aja
# ============================================================

import requests
import pandas as pd
from config.settings import METABASE, GSHEET
from utils.gsheet import get_cell_value


def get_token() -> str:
    """
    Ambil Metabase session token dari Google Sheets config.
    Token disimpen di cell B2 tab A di config sheet.
    """
    token = get_cell_value(
        sheet_id=GSHEET["config"]["sheet_id"],
        tab_name=GSHEET["config"]["tabs"]["main"],
        cell=GSHEET["config"]["token_cell"],
    )
    if not token:
        raise ValueError("Token Metabase kosong! Update dulu di config sheet.")
    return token

def tarik_metabase(url, parameters, token, desc):
    headers = {"Content-Type":"application/x-www-form-urlencoded","X-Metabase-Session":token}
    payload = "parameters=" + quote(json.dumps(parameters))
    print("Pulling", desc)
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code != 200:
        print(f"[{desc}] FAILED:", r.status_code, r.text[:300])
        return pd.DataFrame()
    data = r.json()
    return pd.DataFrame(data) if data else pd.DataFrame()
    
