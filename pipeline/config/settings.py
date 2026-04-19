# ============================================================
# settings.py — Semua konfigurasi pipeline ada di sini
# Kamu cukup update file ini aja, ga perlu utak-atik file lain
# ============================================================

# ── Google Service Account ───────────────────────────────────
# Letakkan file JSON service account kamu di root project
# lalu isi nama file-nya di sini
SERVICE_ACCOUNT_FILE = "service_account.json"

# ── Google Sheets Links ──────────────────────────────────────
GSHEET = {
    # Tracker utama (tempat dump semua data performance)
    "tracker": {
        "url": "https://docs.google.com/spreadsheets/d/10jwwERVKLvdrk7tkmqVXeZHGp3Q1lV_2IjFsc6fXQhQ/edit?gid=911977561#gid=911977561",
        "sheet_id": "10jwwERVKLvdrk7tkmqVXeZHGp3Q1lV_2IjFsc6fXQhQ",  # ambil dari URL
        "tabs": {
            "raw_data_all":  "Raw Data [All]",
            "raw_data_cost": "Raw Data [Cost]",
            "recipients": "Recipients",
            "master_tracker": "Master Tracker by Hub",
        },
        # Range yang di-clear saat Day 1 (sesuaikan)
        "clear_ranges": {
            "raw_data_all": ["C4:I", "P4:V", "AC4:AI","AP4:AR","AY4:BA","BH4:BJ","BO4:BT"],
            "raw_data_cost": ["B3:K"]
        },
    },
    
    # Gsheet sanggahan
    "sanggahan": {
        "url": "https://docs.google.com/spreadsheets/d/1q1CkYFiZQKRvfYDjZGOJmqNOndbH3hd7Du_Pq0Wn7AU/edit?gid=1000001726#gid=1000001726",
        "sheet_id": "1q1CkYFiZQKRvfYDjZGOJmqNOndbH3hd7Du_Pq0Wn7AU",
        "tabs": {
            "poa_iv_b2b_all_b2c_cold": "POA IV B2B All & B2C Cold",
            "poa_iv_keyshipper": "POA IV Keyshipper" ,
            "poa_iv_others": "POA IV Others",
            "lnd_rate_b2b_all_b2c_cold": "LnD Rate B2B All & B2C Cold",
            "lnd_rate_keyshipper" : "LnD Rate Keyshipper",
            "lnd_rate_others":"LnD Rate Others"
              # sesuaikan nama tab
        },
        # Range yang di-clear di semua tab sanggahan (sesuaikan)
        "clear_ranges": {
              "poa_iv_b2b_all_b2c_cold": ["A3:G"],
              "poa_iv_keyshipper": ["A3:G"],
              "poa_iv_others": ["A3:G"],
              "lnd_rate_b2b_all_b2c_cold": ["A3:C"],
              "lnd_rate_keyshipper": ["A3:C"],
              "lnd_rate_others": ["A3:C"],

        }
    },

 # Gsheet PNS - sumber list shipper (JANGAN diedit, read only)
    "pns": {
        "url": "https://docs.google.com/spreadsheets/d/15ndhmW4gtQ14uMwMOl33IZ1iS67qQTFEaFhWr-UF7Ns/edit?gid=218596977#gid=218596977",
        "sheet_id": "15ndhmW4gtQ14uMwMOl33IZ1iS67qQTFEaFhWr-UF7Ns",
        "tabs": {
            "compile": "USE THIS (COMPILE LIST KEY SHIPPERS)",
        },
        # Kolom yang diambil dari PNS (sesuaikan)
        "columns": {
            "global_id": "Global ID",
            "category": "Shipper Service Category",
        },
    },

    # Gsheet Key Shipper milik BI , copy dari PNS
    "key_shipper": {
        "url": "https://docs.google.com/spreadsheets/d/1Gk_pMm40hHs1jXGTtApLMWXD00HiiRchI2MO-q1HUPQ/edit?gid=1784764051#gid=1784764051",
        "sheet_id": "1Gk_pMm40hHs1jXGTtApLMWXD00HiiRchI2MO-q1HUPQ",
        "tabs": {
            "main": "check",
        },
        # Range yang di-clear sebelum update Key Shipper
        "clear_range": "A2:B",
        # Start cell untuk tulis data
        "start_cell": "A2",
    },

    # Gsheet DWS dari tim Sort
    "dws": {
        "url": "https://docs.google.com/spreadsheets/d/1wm7fyvG_AMlK8U2gCBKDr0_Hb_17fFKW21373vjf2xM/edit?gid=0#gid=0",
        "sheet_id": "1wm7fyvG_AMlK8U2gCBKDr0_Hb_17fFKW21373vjf2xM",
        "tabs": {
            "main": "USE THIS", # sesuaikan nama tab
        }
    },

    # Gsheet CPP dari tim PSP
    "cpp": {
        "url": "https://docs.google.com/spreadsheets/d/155VQIcpKGH9Lbd3XUOWbzCxXUTFj8l8tMnU6t1NXitw/edit?gid=0#gid=0",
        "sheet_id": "155VQIcpKGH9Lbd3XUOWbzCxXUTFj8l8tMnU6t1NXitw",
        "tabs": {
            "main": "USE THIS", # sesuaikan nama tab
        }
    },

    # Gsheet staff list dari SORT
    "staff_list": {
        "url": "https://docs.google.com/spreadsheets/d/1s4BQ2TJYxxY-BttqgHvB185ONZlQ36pc0Bkz5NooSTU/edit?gid=664145533#gid=664145533",
        "sheet_id": "1s4BQ2TJYxxY-BttqgHvB185ONZlQ36pc0Bkz5NooSTU",
        "tabs": {
            "main": "USE THIS",
        },
    },

    # Gsheet Converter (data ke rupiah)
    "converter": {
        "url": "https://docs.google.com/spreadsheets/d/1Sn2HisZcT81duWuWtKpVx_E_8192XeFIwtXrrDoSpGQ/edit?gid=0#gid=0",
        "sheet_id": "1Sn2HisZcT81duWuWtKpVx_E_8192XeFIwtXrrDoSpGQ",
        "tabs": {
            "performance": "Master Tracker by Hub",      # sesuaikan nama tab
            "recipient":   "Staff List",  # sesuaikan nama tab
        }
    },

    # Gsheet config — tempat kamu simpen Metabase token
    "config": {
        "sheet_id": "1RJK6GFPVrourpdF91GQ1DWuxBBn2a9_SndoyraXckZ4",
        "tabs": {
            "main": "App Password & API Keys",  # nama tab tempat token disimpen
        },
        "token_cell": "B2",  # cell tempat token Metabase
    },
}

# ── Metabase ─────────────────────────────────────────────────
METABASE_CONFIG = {
    "poa": {
        "poa_iv_1": {
            "url": "https://metabase.ninjavan.co/api/card/122270/query/json",
            "report_type": "poa",
            "common_params_template": [
                {
                    "id": "e6c527e6-8587-41ef-ba1e-223fadbca52a",
                    "type": "date/single",
                    "value_key": "start_date",
                    "target": ["variable", ["template-tag", "start_date"]],
                },
                {
                    "id": "e33b0e69-95c3-4fc3-9e08-2bce46b52ebe",
                    "type": "date/single",
                    "value_key": "end_date",
                    "target": ["variable", ["template-tag", "end_date"]],
                },
                {
                    "id": "5cfead49-71f9-45f9-86b8-d52079f5c4dd",
                    "type": "category",
                    "value": ["month"],
                    "target": ["variable", ["template-tag", "aggr"]],
                },
                {
                    "id": "74ebbf84-d66c-49c6-9d30-c1f260297ed4",
                    "type": "string/=",
                    "value": [
                        "BDO-BDO", "CBN-CBN", "KNO-KNO", "PDG-PDG", "PKU-PKU",
                        "PLM-PLM", "SOC-SOC", "SRG-SRG", "SUB-SUB", "TKG-TKG", "MAC-MAC"
                    ],
                    "target": ["dimension", ["template-tag", "crossdock_orig_hub"]],
                },
                {
                    "id": "bbb8cd83-b7bd-4ce2-8d44-74c0f6e98704",
                    "type": "number/=",
                    "value": ["120"],
                    "target": ["variable", ["template-tag", "Parameter"]],
                },
            ],
            "shipper_params_template": {
                "b2b_cc": [
                    {
                        "id": "f00e3394-9239-4262-89cd-8e735f249c9a",
                        "type": "string/=",
                        "value_key": "b2b_cc",
                        "target": ["dimension", ["template-tag", "shipper_id"]],
                    }
                ],
                "fsbd": [
                    {
                        "id": "f9ba1af7-0782-4239-9b17-fa26bfb9150a",
                        "type": "string/=",
                        "value": ["7474545"],
                        "target": ["dimension", ["template-tag", "parent_id_coalesce"]],
                    },
                    {
                        "id": "f00e3394-9239-4262-89cd-8e735f249c9a",
                        "type": "string/=",
                        "value_key": "key_shipper",
                        "target": ["dimension", ["template-tag", "shipper_id"]],
                    }
                ],
                "others": [
                    {
                        "id": "f9ba1af7-0782-4239-9b17-fa26bfb9150a",
                        "type": "string/=",
                        "value": ["216977","341107"],
                        "target": ["dimension", ["template-tag", "parent_id_coalesce"]],
                    }
                ],
            },
        }
    }
}
# ── Email ─────────────────────────────────────────────────────
EMAIL = {
    "sender": "your_email@company.com",       # TODO: ganti
    "smtp_server": "smtp.gmail.com",           # ganti kalau bukan Gmail
    "smtp_port": 587,
    # Password disimpen di environment variable, bukan di sini
    # Set di GitHub Secrets dengan nama EMAIL_PASSWORD

    "recipients": {
        "day2_notification": [
            "recipient1@company.com",          # TODO: isi penerima notif tanggal 2
        ],
        "day6_fst": [
            "fst_team@company.com",            # TODO: penerima notif FST tanggal 6
        ],
        "day10_reviewer": [
            "reviewer@company.com",            # TODO: penerima notif reviewer
        ],
        "day14_reviewer": [
            "reviewer@company.com",
        ],
        "day16_psp": [
            "psp_team@company.com",            # TODO: penerima notif PSP
        ],
    },

    # Body email per tanggal — edit sesuai kebutuhan
    "body": {
        "day2": """
Hi Team,

Data performance bulan {bulan} sudah tersedia di tracker.
Silakan cek link berikut:

Tracker: {tracker_url}
Sanggahan: {sanggahan_url}

Periode sanggahan: {start_date} s/d {end_date}

Regards,
Automation Pipeline
        """,

        "day6_fst": """
Hi FST Team,

Reminder: Data DWS untuk bulan {bulan} belum diupdate.
Mohon segera update di link berikut: {dws_url}

Regards,
Automation Pipeline
        """,

        "day10_reviewer": """
Hi Reviewer,

Data sanggahan bulan {bulan} sudah bisa direview.
Silakan cek: {sanggahan_url}

Regards,
Automation Pipeline
        """,

        "day14_reviewer": """
Hi Reviewer,

Reminder: Masih ada data sanggahan bulan {bulan} yang belum direview.
Mohon segera review di: {sanggahan_url}

Regards,
Automation Pipeline
        """,

        "day16_psp": """
Hi PSP Team,

Data performance bulan {bulan} sudah final dan siap digunakan.

Tracker  : {tracker_url}
Sanggahan: {sanggahan_url}
Converter: {converter_url}

Regards,
Automation Pipeline
        """,
    }
}

# ── Pipeline Schedule ─────────────────────────────────────────
# Ini untuk referensi GitHub Actions
# Tanggal yang pipeline jalan tiap bulan
SCHEDULE_DAYS = [1, 2, 6, 10, 14, 15, 16]
