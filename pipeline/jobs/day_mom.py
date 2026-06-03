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
    df_master_tracker,
    snapshot_month
  )
  print(df_flatten.shape)
  print(df_flatten.head())

    # write_sheet(
    #     spreadsheet_id=GSHEET["tracker"]["sheet_id"],
    #     sheet_name=GSHEET["tracker"]["tabs"]["raw_data_cost"],
    #     df=df_cpp,
    #     start_cell="B3",
    #     include_header=False
    # )
    # print("===== Input Data ke Tracker Done =====")

    # print("===== Input CPP ke Sanggahan =====")
    # write_sheet(
    #     spreadsheet_id=GSHEET["sanggahan"]["sheet_id"],
    #     sheet_name=GSHEET["sanggahan"]["tabs"]["cpp"],
    #     df=df_cpp,
    #     start_cell="A3",
    #     include_header=False
    # )
    # print("===== Input CPP ke Sanggahan Done =====")


if __name__ == "__main__":
    run()
