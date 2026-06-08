from utils.gsheet import read_sheet_allow_duplicate_headers, flatten_master_tracker
from config.settings import GSHEET


def run():
    print("MoM flatten data mulai.....")

    df_master = read_sheet_allow_duplicate_headers(
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["master_tracker_by_hub"]
    )

    print("Master tracker shape:", df_master.shape)
    print("Columns:", df_master.columns.tolist())

    snapshot_month = "May-26"

    df_flatten = flatten_master_tracker(
        df_master,
        snapshot_month
    )

    print("Flatten shape:", df_flatten.shape)
    print(df_flatten.head())

    return df_flatten


if __name__ == "__main__":
    run()
