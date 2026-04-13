# ============================================================
# jobs/day1.py - Tanggal 1: Cleansing
# File ini hanya orkestasi, logic ada di utils/
# ============================================================

from config.settings import GSHEET
from utils.gsheet import clear_range
from utils.transform import get_last_month_range


def run():
    _, _, bulan = get_last_month_range()
    print(f"=== DAY 1 - Persiapan data bulan {bulan} ===")

    # STEP 1: Cleansing Tracker
    print("\n[1/3] Cleansing tracker...")

    tracker_id = GSHEET["tracker"]["sheet_id"]

    # Clear Raw Data [All]
    raw_all_tab = GSHEET["tracker"]["tabs"]["raw_data_all"]
    for rng in GSHEET["tracker"].get("clear_ranges", {}).get("raw_data_all", []):
        clear_range(tracker_id, raw_all_tab, rng)

    # Clear Raw Data [Cost]
    raw_cost_tab = GSHEET["tracker"]["tabs"]["raw_data_cost"]
    for rng in GSHEET["tracker"].get("clear_ranges", {}).get("raw_data_cost", []):
        clear_range(tracker_id, raw_cost_tab, rng)

    # STEP 2: Cleansing Sanggahan (semua tab)
    print("\n[2/3] Cleansing sanggahan...")

    sanggahan_id = GSHEET["sanggahan"]["sheet_id"]
    # TODO: sesuaikan range yang perlu di-clear di setiap tab sanggahan
    for tab_name in GSHEET["sanggahan"]["tabs"].values():
        for rng in GSHEET["sanggahan"].get("clear_ranges", ["A2:Z1000"]):
            clear_range(sanggahan_id, tab_name, rng)

    # STEP 3: Skip PNS copy (source sudah dari Key Shipper)
    print("\n[3/3] Skip copy PNS -> Key Shipper (source sudah dari Key Shipper).")

    print("\nDay 1 selesai! Tracker & sanggahan sudah bersih.")


if __name__ == "__main__":
    run()
