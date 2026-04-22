# jobs/day15.py — TODO: implement
from utils.gsheet import copy_range
from config.settings import GSHEET
def run():
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["poa_iv_b2b_all_b2c_cold"],
        source_range= "O3:U",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="C4",
    )
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["poa_iv_keyshipper"],
        source_range="O3:U",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="P4",
    )
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["poa_iv_others"],
        source_range="O3:U",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="AC4",
    )
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["lnd_rate_b2b_all_b2c_cold"],
        source_range="J3:L",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="AP4",
    )
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["lnd_rate_keyshipper"],
        source_range="J3:L",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="AY4",
    )
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["lnd_rate_others"],
        source_range="J3:L",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="BH4",
    )
    copy_range(
        GSHEET["sanggahan"]["sheet_id"],
        GSHEET["sanggahan"]["tabs"]["dws"],
        source_range="M3:R",
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="BO4",
    )

if __name__ == "__main__":
    run()
