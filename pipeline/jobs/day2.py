import copy
from datetime import datetime, timedelta

import pandas as pd

from metabase import tarik_metabase, get_token
from gsheet import read_sheet
from settings import METABASE_CONFIG


def get_previous_month_period():
    """
    Ambil tanggal awal dan akhir bulan sebelumnya.
    Contoh:
    Jika hari ini April 2026 -> hasil:
    start_date = 2026-03-01
    end_date   = 2026-03-31
    """
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    start_period_str = first_day_prev_month.strftime("%Y-%m-%d")
    end_period_str = last_day_prev_month.strftime("%Y-%m-%d")

    return start_period_str, end_period_str


def render_params(param_templates, runtime_values):
    """
    Ubah param template yang masih punya value_key
    jadi param final yang sudah punya value.
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


def run_report(report_key, segment_key, runtime_values, token):
    """
    Tarik 1 report Metabase berdasarkan:
    - report_key  : contoh 'poa_iv_1'
    - segment_key : contoh 'b2b_cc' / 'fsbd' / 'others'
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

    print(f"\n=== RUN {desc} ===")
    print(f"URL: {cfg['url']}")
    print("Final params:")
    for p in final_params:
        print(p)

    df_result = tarik_metabase(
        url=cfg["url"],
        parameters=final_params,
        token=token,
        desc=desc
    )

    print(f"{desc} shape: {df_result.shape}")
    return df_result


def build_shipper_lists():
    """
    Ambil shipper list dari sheet 'check' dan pecah jadi:
    - b2b_cc_list
    - fsbd_list
    """
    df_key_shipper = read_sheet("Key Shipper For KPI", "check")

    required_cols = ["Type", "Shipper ID"]
    missing_cols = [c for c in required_cols if c not in df_key_shipper.columns]
    if missing_cols:
        raise ValueError(
            f"Kolom wajib tidak ditemukan di sheet check: {missing_cols}"
        )

    df_key_shipper["Type"] = df_key_shipper["Type"].astype(str).str.strip()

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

    b2b_filtered = df_key_shipper[
        df_key_shipper["Type"].isin(b2b_cc_categories)
    ]

    fsbd_filtered = df_key_shipper[
        df_key_shipper["Type"].isin(fsbd_categories)
    ]

    b2b_cc_list = (
        pd.to_numeric(b2b_filtered["Shipper ID"], errors="coerce")
        .dropna()
        .astype(int)
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    fsbd_list = (
        pd.to_numeric(fsbd_filtered["Shipper ID"], errors="coerce")
        .dropna()
        .astype(int)
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    if not b2b_cc_list:
        print("WARNING: b2b_cc_list kosong!")

    if not fsbd_list:
        print("WARNING: fsbd_list kosong!")

    print(f"Total b2b_cc_list: {len(b2b_cc_list)}")
    print(f"Sample b2b_cc_list: {b2b_cc_list[:10]}")
    print(f"Total fsbd_list: {len(fsbd_list)}")
    print(f"Sample fsbd_list: {fsbd_list[:10]}")

    return b2b_cc_list, fsbd_list


def run():
    print("=== DAY 2 START ===")

    # 1. Ambil periode bulan sebelumnya
    start_period_str, end_period_str = get_previous_month_period()
    print(f"Period start: {start_period_str}")
    print(f"Period end  : {end_period_str}")

    # 2. Ambil token metabase
    metabase_token = get_token()
    print("Metabase token loaded:", bool(metabase_token))

    # 3. Ambil list shipper
    b2b_cc_list, fsbd_list = build_shipper_lists()

    # 4. Runtime values untuk render params
    runtime_values = {
        "start_date": start_period_str,
        "end_date": end_period_str,
        "b2b_cc": b2b_cc_list,
        "fsbd": fsbd_list,
    }

    # 5. Tarik semua segment report dari card yang sama
    results = {}

    results["poa_iv_1_b2b_cc"] = run_report(
        report_key="poa_iv_1",
        segment_key="b2b_cc",
        runtime_values=runtime_values,
        token=metabase_token
    )

    results["poa_iv_1_fsbd"] = run_report(
        report_key="poa_iv_1",
        segment_key="fsbd",
        runtime_values=runtime_values,
        token=metabase_token
    )

    results["poa_iv_1_others"] = run_report(
        report_key="poa_iv_1",
        segment_key="others",
        runtime_values=runtime_values,
        token=metabase_token
    )

    print("\n=== DAY 2 DONE ===")
    for k, v in results.items():
        print(f"{k}: {v.shape}")

    return results


if __name__ == "__main__":
    results = run()
