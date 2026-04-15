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
    
def query_metabase(query_id: int, parameters: list = None) -> pd.DataFrame:
    """
    Tarik data dari Metabase via API.

    Args:
        query_id   : ID question/query di Metabase
        parameters : list of dict filter parameter

    Returns:
        DataFrame hasil query
    """
    token = get_token()
    url = f"{METABASE['base_url']}/api/card/{query_id}/query/json"

    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": token,
    }

    payload = {}
    if parameters:
        payload["parameters"] = parameters

    print(f"Menarik data dari Metabase query ID: {query_id}...")
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 401:
        raise PermissionError("Token Metabase expired! Update token di config sheet.")
    elif response.status_code != 200:
        raise Exception(f"Metabase error {response.status_code}: {response.text}")

    data = response.json()
    df = pd.DataFrame(data)
    print(f"Berhasil tarik {len(df)} rows dari query {query_id}")
    return df


def pull_poa_iv(shipper_ids: list, shipper_type: str) -> pd.DataFrame:
    """
    Tarik data POA-IV dari Metabase untuk kategori shipper tertentu.

    Args:
        shipper_ids  : list shipper ID
        shipper_type : "b2b_cc", "key_shipper", atau "lazada_shopee"
    """
    query_id = METABASE["queries"]["poa_iv"]["id"]
    filter_config = METABASE["shipper_filters"][shipper_type]

    if shipper_type == "b2b_cc":
        parameters = [{
            "type": "category",
            "value": shipper_ids,
            "target": ["variable", ["template-tag", filter_config["param_name"]]],
        }]
    elif shipper_type == "key_shipper":
        parameters = [{
            "type": "category",
            "value": shipper_ids,
            "target": ["variable", ["template-tag", filter_config["param_name_shipper"]]],
        }]
    elif shipper_type == "lazada_shopee":
        parameters = [{
            "type": "category",
            "value": shipper_ids,
            "target": ["variable", ["template-tag", filter_config["param_name_parent"]]],
        }]
    else:
        raise ValueError(f"shipper_type tidak valid: {shipper_type}")

    df = query_metabase(query_id, parameters)
    df["_shipper_type"] = shipper_type
    return df


def pull_lnd(shipper_ids: list, shipper_type: str) -> pd.DataFrame:
    """Tarik data LnD dari Metabase untuk kategori shipper tertentu."""
    query_id = METABASE["queries"]["lnd"]["id"]
    filter_config = METABASE["shipper_filters"][shipper_type]

    parameters = [{
        "type": "category",
        "value": shipper_ids,
        "target": ["variable", ["template-tag", filter_config.get("param_name", "shipper_id")]],
    }]

    df = query_metabase(query_id, parameters)
    df["_shipper_type"] = shipper_type
    return df
