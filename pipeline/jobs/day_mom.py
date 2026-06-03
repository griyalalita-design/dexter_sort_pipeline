# jobs/day10.py 
from utils.gsheet import read_sheet, write_sheet, flatten_master_tracker
from config.settings import GSHEET


def run():
  print("MoM flatten data mulai.....")

  df_master = read_sheet(
    GSHEET["tracker"]["sheet_id"], 
    GSHEET["tracker"]["tabs"]["master_tracker_by_hub"]
  )
  snapshot_month = "May-26"
  df_flatten = flatten_master_tracker(
    df_master,
    snapshot_month
  )
  print(df_flatten.shape)
  print(df_flatten.head())


if __name__ == "__main__":
    run()
