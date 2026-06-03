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


import os

from config.settings import GSHEET
from utils.gsheet import get_cell_value


def get_token() -> str:
    """
    Ambil token Metabase dari env dulu.
    Kalau tidak ada, fallback ke Google Sheet config.
    """
    env_token = (os.getenv("METABASE_TOKEN") or "").strip().strip("'").strip('"')
    if env_token:
        print("Using METABASE_TOKEN from environment.")
        return env_token

    print("METABASE_TOKEN not found in environment. Fallback to Google Sheet config...")

    config_sheet = GSHEET["config"]
    token = get_cell_value(
        sheet_id=config_sheet["sheet_id"],
        tab_name=config_sheet["tabs"]["main"],
        cell=config_sheet["token_cell"],
    )

    token = (token or "").strip().strip("'").strip('"')

    if not token:
        raise ValueError("Token Metabase kosong di environment dan config sheet.")

    print("Using token from Google Sheet config.")
    return token


def tarik_metabase(url, parameters, token, desc):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Metabase-Session": token
    }

    payload = "parameters=" + quote(json.dumps(parameters))

    print(f"Pulling {desc} ...")

    r = requests.post(
        url,
        headers=headers,
        data=payload,
        timeout=300
    )

    if r.status_code != 200:
        print(f"[{desc}] FAILED: {r.status_code} | {r.text[:300]}")
        return pd.DataFrame()

    try:
        data = r.json()
    except Exception as e:
        print(f"[{desc}] Invalid JSON response")
        print(repr(e))
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    # =====================
    # Normal Metabase
    # =====================
    if isinstance(data, list):
        return pd.DataFrame(data)

    # =====================
    # Dict Response
    # =====================
    if isinstance(data, dict):

        print(
            f"[{desc}] Metabase response is dict. "
            f"Keys: {list(data.keys())}"
        )

        # {"data": [...]}
        if isinstance(data.get("data"), list):
            return pd.DataFrame(data["data"])

        # {"rows": [...]}
        if isinstance(data.get("rows"), list):
            return pd.DataFrame(data["rows"])

        # {"columns": [...], "rows": [...]}
        if "columns" in data and "rows" in data:

            cols = data.get("columns")
            rows = data.get("rows")

            if isinstance(cols, list) and isinstance(rows, list):

                try:
                    return pd.DataFrame(
                        rows,
                        columns=cols
                    )
                except Exception as e:
                    print(
                        f"[{desc}] Failed create dataframe "
                        f"from columns/rows"
                    )
                    print(repr(e))
                    return pd.DataFrame()

        print(
            f"[{desc}] Unexpected dict response. "
            f"Returning empty dataframe."
        )

        return pd.DataFrame()

    print(
        f"[{desc}] Unexpected response type: "
        f"{type(data)}"
    )

    return pd.DataFrame()


def build_params(common_params, extra_params):
    return common_params + extra_params
