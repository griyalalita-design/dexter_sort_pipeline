import copy
from datetime import datetime, timedelta

import pandas as pd

from utils.metabase import tarik_metabase, get_token
from utils.gsheet import read_sheet, get_cell_value
from config.settings import METABASE_CONFIG, GSHEET


def get_previous_month_period():
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    start_date = first_day_prev_month.strftime("%Y-%m-%d")
    end_date = last_day_prev_month.strftime("%Y-%m-%d")
    return start_date, end_date


def render_params(param_templates, runtime_values):
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
    print("\n[1/6] Read Google Sheet key_shipper...")

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

    print(f"Total b2b_cc_list: {len(b2b_cc_list)} | sample: {b2b_cc_list[:5]}")
    print(f"Total fsbd_list: {len(fsbd_list)} | sample: {fsbd_list[:5]}")

    if not b2b_cc_list:
        print("WARNING: b2b_cc_list kosong!")
    if not fsbd_list:
        print("WARNING: fsbd_list kosong!")

    return b2b_cc_list, fsbd_list


def run_report(report_group, report_key, segment_key, runtime_values, token):
    cfg = METABASE_CONFIG[report_group][report_key]

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
    print(f"Group: {report_group}")
    print(f"Total params: {len(final_params)}")

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


# =========================
# POA HELPERS
# =========================
def reduce_poa_columns(df):
    if df.empty:
        return pd.DataFrame(columns=["origin_hub", "remarks"])

    required_cols = ["origin_hub", "remarks"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom POA tidak ditemukan: {missing_cols}")

    out = df[required_cols].copy()
    out["origin_hub"] = out["origin_hub"].astype(str).str.strip()
    out["remarks"] = out["remarks"].astype(str).str.strip().str.lower()

    return out


def compile_poa_segment(results, segment_key):
    compiled = []

    for report_key in ["poa_iv_1", "poa_iv_2", "poa_iv_3", "poa_iv_4"]:
        result_key = f"{report_key}_{segment_key}"
        df = results.get(result_key, pd.DataFrame())
        compiled.append(reduce_poa_columns(df))

    if not compiled:
        return pd.DataFrame(columns=["origin_hub", "remarks"])

    return pd.concat(compiled, ignore_index=True)


def build_poa_pivot(df_compiled):
    if df_compiled.empty:
        return pd.DataFrame(columns=[
            "orig_hub_name", "hit", "hit: offload", "miss", "miss: potential hit", "total_hit"
        ])

    pivot = (
        df_compiled.assign(count=1)
        .pivot_table(
            index="orig_hub_name",
            columns="remarks",
            values="count",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    expected_cols = ["hit", "hit: offload", "miss", "miss: potential hit"]
    for col in expected_cols:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot["total_hit"] = pivot["hit"] + pivot["hit: offload"]

    final_cols = ["orig_hub_nameb", "hit", "hit: offload", "miss", "miss: potential hit", "total_hit"]
    return pivot[final_cols].sort_values("orig_hub_name").reset_index(drop=True)


# =========================
# LND HELPERS
# =========================
def reduce_lnd_columns(df):
    if df.empty:
        return pd.DataFrame(columns=["hub", "total_loss_damage", "total_volume"])

    required_cols = ["hub", "total_loss_damage", "total_volume"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom LND tidak ditemukan: {missing_cols}")

    out = df[required_cols].copy()
    out["hub"] = out["hub"].astype(str).str.strip()

    return out


def run():
    print("=== DAY 2 START ===")

    start_date, end_date = get_previous_month_period()
    print(f"\n[0/6] Period: {start_date} to {end_date}")

    print("\n[2/6] Get Metabase token...")
    token = get_token()
    print("Token loaded:", bool(token))

    print("\n[3/6] Build shipper lists...")
    b2b_cc_list, fsbd_list = build_shipper_lists()

    runtime_values = {
        "start_date": start_date,
        "end_date": end_date,
        "b2b_cc": b2b_cc_list,
        "fsbd": fsbd_list,
    }

    # =========================
    # POA
    # =========================
    print("\n[4/6] Pull POA reports...")
    poa_results = {}

    poa_report_keys = ["poa_iv_1", "poa_iv_2", "poa_iv_3", "poa_iv_4"]
    segment_keys = ["b2b_cc", "fsbd", "others"]

    for report_key in poa_report_keys:
        for segment_key in segment_keys:
            result_name = f"{report_key}_{segment_key}"
            poa_results[result_name] = run_report(
                report_group="poa",
                report_key=report_key,
                segment_key=segment_key,
                runtime_values=runtime_values,
                token=token,
            )

    print("\n[5/6] Compile and pivot POA...")
    compiled_poa_b2b_cc = compile_poa_segment(poa_results, "b2b_cc")
    compiled_poa_fsbd = compile_poa_segment(poa_results, "fsbd")
    compiled_poa_others = compile_poa_segment(poa_results, "others")

    pivot_poa_b2b_cc = build_poa_pivot(compiled_poa_b2b_cc)
    pivot_poa_fsbd = build_poa_pivot(compiled_poa_fsbd)
    pivot_poa_others = build_poa_pivot(compiled_poa_others)

    print("pivot_poa_b2b_cc shape:", pivot_poa_b2b_cc.shape)
    print("pivot_poa_fsbd shape:", pivot_poa_fsbd.shape)
    print("pivot_poa_others shape:", pivot_poa_others.shape)

    # =========================
    # LND
    # =========================
    print("\n[6/6] Pull LND reports...")
    lnd_results = {}

    for segment_key in segment_keys:
        result_name = f"lnd_1_{segment_key}"
        lnd_results[result_name] = run_report(
            report_group="lnd",
            report_key="lnd_1",
            segment_key=segment_key,
            runtime_values=runtime_values,
            token=token,
        )

    lnd_b2b_cc = reduce_lnd_columns(lnd_results["lnd_1_b2b_cc"])
    lnd_fsbd = reduce_lnd_columns(lnd_results["lnd_1_fsbd"])
    lnd_others = reduce_lnd_columns(lnd_results["lnd_1_others"])

    print("lnd_b2b_cc shape:", lnd_b2b_cc.shape)
    print("lnd_fsbd shape:", lnd_fsbd.shape)
    print("lnd_others shape:", lnd_others.shape)

    print("\n=== DAY 2 DONE ===")

    return {
        # raw
        "poa_results": poa_results,
        "lnd_results": lnd_results,

        # poa compiled
        "compiled_poa_b2b_cc": compiled_poa_b2b_cc,
        "compiled_poa_fsbd": compiled_poa_fsbd,
        "compiled_poa_others": compiled_poa_others,

        # poa final
        "pivot_poa_b2b_cc": pivot_poa_b2b_cc,
        "pivot_poa_fsbd": pivot_poa_fsbd,
        "pivot_poa_others": pivot_poa_others,

        # lnd final
        "lnd_b2b_cc": lnd_b2b_cc,
        "lnd_fsbd": lnd_fsbd,
        "lnd_others": lnd_others,
    }


if __name__ == "__main__":
    run()
