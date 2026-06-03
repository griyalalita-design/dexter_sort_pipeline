"""
gsheet.py
---------
Responsibility: All Google Sheets operations.
Read, write, clear sheets. No transformation logic here.
"""

from __future__ import annotations

import json
import os
from typing import Iterable, List, Optional

import gspread
import pandas as pd

from config.settings import SERVICE_ACCOUNT_FILE


# --- Client helpers ---

def _get_client() -> gspread.Client:
    """
    Create gspread client from service account file or env var JSON.
    Priority:
      1) SERVICE_ACCOUNT_FILE (path)
      2) GSHEET_SERVICE_ACCOUNT_JSON (env var, raw JSON string)
    """
    if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        return gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    raw = os.getenv("GSHEET_SERVICE_ACCOUNT_JSON")
    if raw:
        info = json.loads(raw)
        return gspread.service_account_from_dict(info)

    raise FileNotFoundError(
        "Service account not found. Set SERVICE_ACCOUNT_FILE or GSHEET_SERVICE_ACCOUNT_JSON."
    )


def open_by_key(sheet_id: str) -> gspread.Spreadsheet:
    return _get_client().open_by_key(sheet_id)


def open_by_url(url: str) -> gspread.Spreadsheet:
    return _get_client().open_by_url(url)


# --- Core ops ---
def _a1(sheet_name, range_a1):
    safe_sheet_name = str(sheet_name).replace("'", "''")

    # Kalau nama tab simple tanpa spasi/simbol, tidak perlu quote
    if safe_sheet_name.replace("_", "").replace("-", "").isalnum():
        return f"{safe_sheet_name}!{range_a1}"

    return f"'{safe_sheet_name}'!{range_a1}"


def clear_range(spreadsheet_id: str, sheet_name: str, range_a1: str) -> None:
    """
    Clear a specific range (A1 notation) in a sheet tab.
    """
    wb = open_by_key(spreadsheet_id)
    wb.values_clear(_a1(sheet_name, range_a1))


def clear_sheet(spreadsheet_id: str, sheet_name: str) -> None:
    """
    Clear all data from a specific sheet tab.
    """
    wb = open_by_key(spreadsheet_id)
    worksheet = wb.worksheet(sheet_name)
    worksheet.clear()


def read_sheet(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    """
    Read data from a specific sheet tab and return as DataFrame.
    """
    wb = open_by_key(spreadsheet_id)
    worksheet = wb.worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)
    
def get_cell_value(sheet_id: str, tab_name: str, cell: str) -> str:
    """
    Read single cell value from a specific sheet tab.
    """
    wb = open_by_key(sheet_id)
    worksheet = wb.worksheet(tab_name)
    value = worksheet.acell(cell).value
    return (value or "").strip().strip("'").strip('"')


def write_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    df: pd.DataFrame,
    start_cell: str = "A1",
    include_header: bool = True,
) -> None:
    """
    Write a DataFrame to a specific sheet tab.
    """
    wb = open_by_key(spreadsheet_id)

    if include_header:
        values = [df.columns.tolist()] + df.values.tolist() if not df.empty else [df.columns.tolist()]
    else:
        values = df.values.tolist() if not df.empty else []

    if not values:
        return

    wb.values_update(
        _a1(sheet_name, start_cell),
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": values},
    )


def append_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    df: pd.DataFrame,
    start_cell: str = "A1",
) -> None:
    """
    Append a DataFrame to a sheet (no header by default).
    """
    wb = open_by_key(spreadsheet_id)
    values = df.values.tolist() if not df.empty else []
    if not values:
        return
    wb.values_append(
        _a1(sheet_name, start_cell),
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": values},
    )


def copy_range(
    source_sheet_id: str,
    source_tab: str,
    source_range: str,
    dest_sheet_id: str,
    dest_tab: str,
    dest_start_cell: str,
) -> None:
    """
    Copy values from one sheet range to another.
    """
    src = open_by_key(source_sheet_id)
    dest = open_by_key(dest_sheet_id)

    values = src.values_get(_a1(source_tab, source_range)).get("values", [])
    if not values:
        return

    dest.values_update(
        _a1(dest_tab, dest_start_cell),
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": values},
    )


def copy_columns(
    source_sheet_id: str,
    source_tab: str,
    target_sheet_id: str,
    target_tab: str,
    columns: List[str],
    start_cell: str = "A1",
) -> None:
    """
    Copy selected columns by header name from source to target.
    """
    df = read_sheet(source_sheet_id, source_tab)
    if df.empty:
        return
    existing = [c for c in columns if c in df.columns]
    if not existing:
        return
    write_sheet(target_sheet_id, target_tab, df[existing], start_cell=start_cell)


def mark_sanggahan_open(spreadsheet_id: str, sheet_name: str) -> None:
    """
    Mark all sanggahan rows as 'open' in the tracker.
    TODO: Implement real logic if needed.
    """
    # Placeholder: implement column-based update when schema is final
    return

import pandas as pd


def flatten_master_tracker(df_master, snapshot_month):
    """
    Convert Master Tracker by Hub
    menjadi format long / AI friendly

    Output:
    snapshot_month
    hub
    kpi
    value
    tier
    """

    KPI_MAPPING = [
        {
            "kpi": "POA B2B CC",
            "value_col": "POA-IV B2B All & B2C Cold",
            "tier_col": "Tier_POA_B2B_CC"
        },
        {
            "kpi": "POA Keyshipper",
            "value_col": "POA-IV Keyshipper",
            "tier_col": "Tier_POA_Keyshipper"
        },
        {
            "kpi": "POA Others",
            "value_col": "POA-IV Others",
            "tier_col": "Tier_POA_Others"
        },
        {
            "kpi": "LND B2B CC",
            "value_col": "LnD Rate B2B All & B2C Cold",
            "tier_col": "Tier_LND_B2B_CC"
        },
        {
            "kpi": "LND Keyshipper",
            "value_col": "LnD Rate Keyshipper",
            "tier_col": "Tier_LND_Keyshipper"
        },
        {
            "kpi": "LND Others",
            "value_col": "LnD Rate Others",
            "tier_col": "Tier_LND_Others"
        },
        {
            "kpi": "DWS",
            "value_col": "DWS",
            "tier_col": "Tier_DWS"
        },
        {
            "kpi": "CPP",
            "value_col": "CPP",
            "tier_col": "Tier_CPP"
        }
    ]

    rows = []

    for _, row in df_master.iterrows():

        hub = row["Hub"]

        for mapping in KPI_MAPPING:

            rows.append({
                "snapshot_month": snapshot_month,
                "hub": hub,
                "kpi": mapping["kpi"],
                "value": row.get(mapping["value_col"]),
                "tier": row.get(mapping["tier_col"])
            })

    return pd.DataFrame(rows)
