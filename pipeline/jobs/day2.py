# ============================================================
# jobs/day2.py — Tanggal 2: Tarik Metabase, transform, dump
# File ini hanya orkestasi, logic ada di utils/
# ============================================================

import pandas as pd
from config.settings import GSHEET
from utils.gsheet import read_sheet, write_sheet, append_sheet
from utils.metabase import tarik_metabase
from utils.transform import get_last_month_range, categorize_shippers, transform_poa, transform_lnd, merge_with_staff
from utils.email import notify_day2


def run():
    _, _, bulan = get_last_month_range()
    print(f"=== DAY 2 - Tarik data Metabase bulan {bulan} ===")

    # ── STEP 1: Ambil list shipper dari Key Shipper ──────────
    print("\n[1/5] Ambil data shipper dari Key Shipper...")
    df_pns = read_sheet(GSHEET["key_shipper"]["sheet_id"], GSHEET["key_shipper"]["tabs"]["main"])
    shipper_categories = categorize_shippers(df_pns)

    # ── STEP 2: Tarik POA-IV dari Metabase ───────────────────
    print("\n[2/5] Tarik data POA-IV dari Metabase...")
    poa_results = []

    for category, shipper_ids in shipper_categories.items():
        if not shipper_ids:
            print(f"Skip {category} — shipper kosong")
            continue
        df_raw = pull_poa_iv(shipper_ids, category)
        df_transformed = transform_poa(df_raw)
        df_transformed["_category"] = category
        poa_results.append(df_transformed)

    df_poa_all = pd.concat(poa_results, ignore_index=True) if poa_results else pd.DataFrame()

    # ── STEP 3: Tarik LnD dari Metabase ──────────────────────
    print("\n[3/5] Tarik data LnD dari Metabase...")
    lnd_results = []

    for category, shipper_ids in shipper_categories.items():
        if not shipper_ids:
            continue
        df_raw = pull_lnd(shipper_ids, category)
        df_transformed = transform_lnd(df_raw)
        df_transformed["_category"] = category
        lnd_results.append(df_transformed)

    df_lnd_all = pd.concat(lnd_results, ignore_index=True) if lnd_results else pd.DataFrame()

    # ── STEP 4: Dump ke Tracker & Sanggahan ──────────────────
    print("\n[4/5] Dump data ke Tracker dan Sanggahan...")

    tracker_id = GSHEET["tracker"]["sheet_id"]
    sanggahan_id = GSHEET["sanggahan"]["sheet_id"]

    if not df_poa_all.empty:
        # TODO: sesuaikan tab dan start_cell untuk masing-masing kategori
        write_sheet(tracker_id, GSHEET["tracker"]["tabs"]["raw_data_all"], df_poa_all, start_cell="B2")
        write_sheet(sanggahan_id, GSHEET["sanggahan"]["tabs"]["main"], df_poa_all, start_cell="A2")

    if not df_lnd_all.empty:
        # TODO: sesuaikan kolom dump LnD (mungkin beda tab/kolom dari POA)
        write_sheet(tracker_id, GSHEET["tracker"]["tabs"]["raw_data_all"], df_lnd_all, start_cell="K2")

    # ── STEP 5: Kirim Email Notifikasi ───────────────────────
    print("\n[5/5] Kirim email notifikasi...")
    notify_day2(bulan)

    print(f"\nDay 2 selesai! Data {bulan} sudah masuk tracker dan sanggahan.")


if __name__ == "__main__":
    run()
