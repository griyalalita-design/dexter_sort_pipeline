import copy
from datetime import datetime, timedelta

import pandas as pd

from utils.metabase import tarik_metabase, get_token
from utils.gsheet import read_sheet
from config.settings import METABASE_CONFIG, GSHEET
from utils.gsheet import get_cell_value
# Kalau folder kamu huruf besar, ganti jadi:
# from CONFIG.settings import METABASE_CONFIG, GSHEET


def get_previous_month_period():
    """
    Ambil tanggal awal dan akhir bulan sebelumnya.
    Contoh:
    jika hari ini April 2026 -> hasil:
    start_date = 2026-03-01
    end_date   = 2026-03-31
    """
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    start_date = first_day_prev_month.strftime("%Y-%m-%d")
    end_date = last_day_prev_month.strftime("%Y-%m-%d")
    return start_date, end_date


def render_params(param_templates, runtime_values):
    """
    Ubah param template yang masih pakai value_key
    jadi param final yang sudah berisi value.
    """
    rendered = []

    for param in param_templates:
        p = copy.deepcopy(param)

        if "value_key" in p:
            key = p.pop("value_key")

            if key not in runtime_values:
                raise KeyError(f"runtime_values tidak punya key: {key}")

            p["value"] = runtime_values[key]

        rendered.append(p)

    return rendered


def build_shipper_lists():
    """
    Ambil b2b_cc_list dan fsbd_list dari sheet key_shipper tab main.
    """
    print("\n[1/4] Read Google Sheet key_shipper...")

    df = read_sheet(
        GSHEET["key_shipper"]["sheet_id"],
        GSHEET["key_shipper"]["tabs"]["main"]
    )

    print(f"Sheet shape: {df.shape}")
    print("Columns:", df.columns.tolist())

    required_cols = ["Type", "Shipper ID"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom tidak ditemukan di sheet key_shipper: {missing_cols}")

    df["Type"] = df["Type"].astype(str).str.strip()

    b2b_cc_categories = [
        "B2C Cold Chain Sameday",
        "B2C Cold Chain Next Day",
        "B2B Dry Reguler",
        "B2B Sameday Reguler",
        "B2B Sameday Premium",
    ]

    fsbd_categories = [
        "FSBD Key Shipper",
        "Aggregator Keyshipper",
    ]

    b2b_df = df[df["Type"].isin(b2b_cc_categories)].copy()
    fsbd_df = df[df["Type"].isin(fsbd_categories)].copy()

    b2b_cc_list = (
        pd.to_numeric(b2b_df["Shipper ID"], errors="coerce")
        .dropna()
        .astype(int)
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    fsbd_list = (
        pd.to_numeric(fsbd_df["Shipper ID"], errors="coerce")
        .dropna()
        .astype(int)
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    print(f"Total b2b_cc_list: {len(b2b_cc_list)}")
    print(f"Sample b2b_cc_list: {b2b_cc_list[:10]}")

    print(f"Total fsbd_list: {len(fsbd_list)}")
    print(f"Sample fsbd_list: {fsbd_list[:10]}")

    if not b2b_cc_list:
        print("WARNING: b2b_cc_list kosong!")
    if not fsbd_list:
        print("WARNING: fsbd_list kosong!")

    return b2b_cc_list, fsbd_list


def run_report(report_key, segment_key, runtime_values, token):
    """
    Jalankan 1 report Metabase.
    """
    cfg = METABASE_CONFIG["poa"][report_key]

    common_params = render_params(
        cfg["common_params_template"],
        runtime_values
    )

    segment_params = render_params(
        cfg["shipper_params_template"][segment_key],
        runtime_values
    )

    final_params = common_params + segment_params
    desc = f"{report_key}_{segment_key}"

    print(f"\n[RUN] {desc}")
    print(f"URL: {cfg['url']}")
    print(f"Total params: {len(final_params)}")
    print("Rendered params:")
    for i, p in enumerate(final_params, start=1):
        print(f"  Param {i}: {p}")

    df_result = tarik_metabase(
        url=cfg["url"],
        parameters=final_params,
        token=token,
        desc=desc
    )

    print(f"{desc} shape: {df_result.shape}")

    if df_result.empty:
        print(f"WARNING: {desc} hasil kosong")
    else:
        print(f"{desc} preview:")
        print(df_result.head(5).to_string(index=False))

    return df_result


def run():
    print("=== DAY 2 START ===")

    start_date, end_date = get_previous_month_period()
    print(f"\n[0/4] Period: {start_date} to {end_date}")

    print("\n[2/4] Get Metabase token...")
    token = get_token()
    print("Token loaded:", bool(token))

    print("\n[3/4] Build shipper lists...")
    b2b_cc_list, fsbd_list = build_shipper_lists()

    runtime_values = {
        "start_date": start_date,
        "end_date": end_date,
        "b2b_cc": b2b_cc_list,
        "fsbd": fsbd_list,
    }

    print("\n[4/4] Pull Metabase reports...")
    results = {}

    results["poa_iv_1_b2b_cc"] = run_report(
        report_key="poa_iv_1",
        segment_key="b2b_cc",
        runtime_values=runtime_values,
        token=token,
    )

    results["poa_iv_1_fsbd"] = run_report(
        report_key="poa_iv_1",
        segment_key="fsbd",
        runtime_values=runtime_values,
        token=token,
    )

    results["poa_iv_1_others"] = run_report(
        report_key="poa_iv_1",
        segment_key="others",
        runtime_values=runtime_values,
        token=token,
    )

    print("\n=== DAY 2 DONE ===")
    for name, df in results.items():
        print(f"{name}: {df.shape}")

    return results


if __name__ == "__main__":
    run()
