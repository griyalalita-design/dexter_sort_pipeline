# ============================================================
# jobs/day2.py - Tanggal 2
# Ambil token, tarik data Metabase, lalu lanjut proses berikutnya.
# ============================================================

import pandas as pd

from config.settings import GSHEET, METABASE
from utils.gsheet import read_sheet
from utils.metabase import get_token, tarik_metabase
from utils.transform import categorize_shippers, get_last_month_range, transform_lnd, transform_poa


def _build_context(start_date: str, end_date: str, shipper_groups: dict) -> dict:
    return {
        "start_date": start_date,
        "end_date": end_date,
        "b2b_cc_shipper_ids": shipper_groups.get("b2b_cc", []),
        "key_shipper_ids": shipper_groups.get("key_shipper", []),
        "others_parent_ids": METABASE.get("others_parent_ids", []),
        "key_shipper_parent_ids": METABASE.get("key_shipper_parent_ids", []),
    }


def _resolve_param_value(raw_value, context: dict):
    if isinstance(raw_value, str) and raw_value.startswith("$"):
        return context.get(raw_value[1:], [])
    return raw_value


def _build_params(param_templates: list, context: dict) -> list:
    params = []
    for item in param_templates:
        params.append(
            {
                "id": item["id"],
                "type": item["type"],
                "value": _resolve_param_value(item["value"], context),
                "target": ["variable", ["template-tag", item["target"]]],
            }
        )
    return params


def _safe_transform(df_raw: pd.DataFrame, report_type: str) -> pd.DataFrame:
    if df_raw.empty:
        return pd.DataFrame()

    if report_type == "poa":
        return transform_poa(df_raw)

    if report_type == "lnd":
        return transform_lnd(df_raw)

    return df_raw


def run():
    start_period, end_period, bulan = get_last_month_range()
    start_period_str = start_period.strftime("%Y-%m-%d")
    end_period_str = end_period.strftime("%Y-%m-%d")

    print(f"=== DAY 2 - Tarik data Metabase bulan {bulan} ===")

    print("\n[1/3] Ambil token Metabase...")
    token = get_token()

    print("\n[2/3] Ambil list shipper dari Key Shipper...")
    df_key_shipper = read_sheet(
        GSHEET["key_shipper"]["sheet_id"],
        GSHEET["key_shipper"]["tabs"]["main"],
    )
    shipper_groups = categorize_shippers(df_key_shipper)
    context = _build_context(start_period_str, end_period_str, shipper_groups)

    reports = METABASE.get("reports", {})
    if not reports:
        print("Config METABASE['reports'] belum diisi. Isi dulu URL dan param template tiap report.")
        return

    print("\n[3/3] Tarik data semua report...")
    pulled_data = {}

    for report_name, report_conf in reports.items():
        report_type = report_conf.get("report_type", "raw")
        report_url = report_conf["url"]
        pulled_data[report_name] = {}

        for shipper_type, param_templates in report_conf["shipper_params"].items():
            full_templates = report_conf.get("common_params", []) + param_templates
            params = _build_params(full_templates, context)

            df_raw = tarik_metabase(
                url=report_url,
                parameters=params,
                token=token,
                desc=f"{report_name}_{shipper_type}",
            )
            df_final = _safe_transform(df_raw, report_type)
            pulled_data[report_name][shipper_type] = df_final

            print(f"{report_name} | {shipper_type}: {len(df_final)} rows")

    # TODO:
    # 1. dump hasil ke tracker
    # 2. dump hasil ke sanggahan
    # 3. merge staff list
    # 4. kirim email
    print("\nDay 2 selesai sampai tahap pull Metabase.")


if __name__ == "__main__":
    run()
