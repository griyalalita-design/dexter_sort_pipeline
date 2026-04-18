# ============================================================
# utils/metabase.py - Semua extract data dari Metabase
# Tidak ada transformasi di sini.
# ============================================================

import json
import os
from urllib.parse import quote

import pandas as pd
import requests

from config.settings import GSHEET
from utils.gsheet import get_cell_value


def get_token() -> str:
    """
    Ambil token Metabase dari env atau Google Sheet config.
    """
    env_token = (os.getenv("METABASE_TOKEN") or "").strip()
    if env_token:
        return env_token

    config_sheet = GSHEET["config"]
    token = get_cell_value(
        sheet_id=config_sheet["sheet_id"],
        tab_name=config_sheet["tabs"]["main"],
        cell=config_sheet["token_cell"],
    )

    if not token:
        raise ValueError("Token Metabase kosong di config sheet.")

    return token


def tarik_metabase(url, parameters, token, desc):
    """
    Tarik data Metabase pakai format request yang sama seperti script lama.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Metabase-Session": token,
    }
    payload = "parameters=" + quote(json.dumps(parameters))

    print("Pulling", desc)
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"[{desc}] FAILED:", response.status_code, response.text[:300])
        return pd.DataFrame()

    data = response.json()
    return pd.DataFrame(data) if data else pd.DataFrame()
