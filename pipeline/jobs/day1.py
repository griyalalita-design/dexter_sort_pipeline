# ============================================================
# jobs/day1.py - Tanggal 1: Cleansing
# File ini hanya orkestasi, logic ada di utils/
# ============================================================

from config.settings import GSHEET
from utils.gsheet import clear_range
from utils.transform import get_last_month_range


def _iter_ranges(value):
    if isinstance(value, dict):
        return list(value.values())
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        return [value]
    return []

def _ranges_for_tab(clear_ranges, tab_key):
    if isinstance(clear_ranges, dict):
        return _iter_ranges(clear_ranges.get(tab_key, []))
    return _iter_ranges(clear_ranges)


def run():
    _, _, bulan = get_last_month_range()
    print(f"=== DAY 1 - Persiapan data bulan {bulan} ===")

    # STEP 1: Cleansing Tracker
    print("\n[1/3] Cleansing tracker...")

    tracker_id = GSHEET["tracker"]["sheet_id"]

    # Clear Raw Data [All]
    raw_all_tab = GSHEET["tracker"]["tabs"]["raw_data_all"]
    raw_all_ranges = _iter_ranges(GSHEET["tracker"].get("clear_ranges", {}).get("raw_data_all", []))
    for rng in raw_all_ranges:
        clear_range(tracker_id, raw_all_tab, rng)

    # Clear Raw Data [Cost]
    raw_cost_tab = GSHEET["tracker"]["tabs"]["raw_data_cost"]
    raw_cost_ranges = _iter_ranges(GSHEET["tracker"].get("clear_ranges", {}).get("raw_data_cost", []))
    for rng in raw_cost_ranges:
        clear_range(tracker_id, raw_cost_tab, rng)

    # STEP 2: Cleansing Sanggahan (semua tab)
    print("\n[2/3] Cleansing sanggahan...")

    sanggahan_id = GSHEET["sanggahan"]["sheet_id"]
    # TODO: sesuaikan range yang perlu di-clear di setiap tab sanggahan
    clear_conf = GSHEET["sanggahan"].get("clear_ranges", ["A2:Z1000"])
    for tab_key, tab_name in GSHEET["sanggahan"]["tabs"].items():
        for rng in _ranges_for_tab(clear_conf, tab_key):
            clear_range(sanggahan_id, tab_name, rng)

    # STEP 3: Skip PNS copy (source sudah dari Key Shipper)
    print("\n[3/3] Skip copy PNS -> Key Shipper (source sudah dari Key Shipper).")

    print("\nDay 1 selesai! Tracker & sanggahan sudah bersih.")


if __name__ == "__main__":
    run()
