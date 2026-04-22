# jobs/day16.py — TODO: implement
from utils.transform import get_last_month_range
from utils.gsheet import copy_range
from config.settings import GSHEET

def run():
    copy_range(
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["master_tracker_by_hub"],
        source_range= "A7:Q",
        GSHEET["converter"]["sheet_id"],
        GSHEET["converter"]["tabs"]["master_tracker_by_hub"],
        dest_start_cell="A7"
    )
    copy_range(
        GSHEET["staff_list"]["sheet_id"],
        GSHEET["staff_list"]["tabs"]["main"],
        source_range= "A2:E",
        GSHEET["converter"]["sheet_id"],
        GSHEET["converter"]["tabs"]["staff_list"],
        dest_start_cell="B2"
    )
if __name__ == "__main__":
    run()
