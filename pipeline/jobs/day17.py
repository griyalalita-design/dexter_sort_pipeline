# jobs/day17.py
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config.settings import SERVICE_ACCOUNT_FILE


# ===== EDIT SESUAI KEBUTUHAN =====
SOURCE_FILE_ID = "1FQHaGP7r80qYKzLjCpeZ_ZAosyB14kWQQAGvLW0tE4M"
TARGET_FOLDER_ID = "1T1_D3dZ-ejrLzpNJrpJavhfQ8LAHb00t"
# =================================


def get_prev_month_label() -> str:
    """
    Return previous month label like 'Aug 25'
    """
    now = datetime.today()
    first_of_this_month = now.replace(day=1)
    last_of_prev_month = first_of_this_month - timedelta(days=1)

    mons = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    mon = mons[last_of_prev_month.month - 1]
    yy = str(last_of_prev_month.year)[-2:]
    return f"{mon} {yy}"


def get_drive_service():
    """
    Build Google Drive API service using:
    1) SERVICE_ACCOUNT_FILE
    2) GSHEET_SERVICE_ACCOUNT_JSON env var
    """
    scopes = ["https://www.googleapis.com/auth/drive"]

    if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=scopes
        )
    else:
        raw = os.getenv("GSHEET_SERVICE_ACCOUNT_JSON")
        if not raw:
            raise FileNotFoundError(
                "Service account not found. Set SERVICE_ACCOUNT_FILE or GSHEET_SERVICE_ACCOUNT_JSON."
            )

        info = json.loads(raw)
        creds = Credentials.from_service_account_info(
            info,
            scopes=scopes
        )

    return build("drive", "v3", credentials=creds)


def run_archive(source_file_id: str, target_folder_id: str) -> str:
    """
    Copy a Google Drive file to target folder and append previous month suffix.
    Returns new file id.
    """
    service = get_drive_service()

    # Get source file name
    src_file = service.files().get(
        fileId=source_file_id,
        fields="id,name"
    ).execute()

    suffix = f" - {get_prev_month_label()}"
    new_name = f"{src_file['name']}{suffix}"

    copied_file = service.files().copy(
        fileId=source_file_id,
        body={
            "name": new_name,
            "parents": [target_folder_id]
        },
        fields="id,name,parents"
    ).execute()

    print(f"Archive success: {copied_file['name']} (ID: {copied_file['id']})")
    return copied_file["id"]


def run():
    print("===== Kita Mulai Run Day 17 Archive =====")
    run_archive(
        source_file_id=SOURCE_FILE_ID,
        target_folder_id=TARGET_FOLDER_ID,
    )
    print("===== Day 17 Archive Done =====")


if __name__ == "__main__":
    run()
