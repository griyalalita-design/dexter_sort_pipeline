from datetime import datetime

from utils.gsheet import (
    read_sheet_with_header_row,
    flatten_master_tracker,
    write_sheet,
)
from config.settings import GSHEET


def get_snapshot_month() -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    today = datetime.today()
    return f"{months[today.month - 1]}-{str(today.year)[-2:]}"


def run():
    print("=== MoM flatten data mulai ===")

    df_master = read_sheet_with_header_row(
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["master_tracker_by_hub"],
        header_row=6,
    )

    print("Master tracker shape:", df_master.shape)
    print("Columns:", df_master.columns.tolist())

    snapshot_month = get_snapshot_month()
    print("Snapshot month:", snapshot_month)

    df_flatten = flatten_master_tracker(
        df_master,
        snapshot_month,
    )

    print("Flatten shape:", df_flatten.shape)
    print(df_flatten.head(20).to_string(index=False))

    write_sheet(
        spreadsheet_id=GSHEET["lm_mom_recap"]["sheet_id"],
        sheet_name=GSHEET["lm_mom_recap"]["tabs"]["monthly_snapshot"],
        df=df_flatten,
        start_cell="A1",
        include_header=True,
    )

    print("=== MoM flatten selesai dan dumped ke recap ===")

    return df_flatten


if __name__ == "__main__":
    run()
