import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_ALIAS = "id-bi-reporting@ninjavan.co"
SENDER_DISPLAY_NAME = "ID BI-Reporting"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

METABASE_URL = "https://docs.google.com/spreadsheets/d/10jwwERVKLvdrk7tkmqVXeZHGp3Q1lV_2IjFsc6fXQhQ/edit?gid=26110973#gid=26110973"
SOSIALISASI_URL = "https://docs.google.com/presentation/d/1-X4ov1yvZ7IlCxhhoS72l3g9ItdY6UpFI480jsfLHg4/edit?slide=id.g1e6796d10b0_0_192#slide=id.g1e6796d10b0_0_192"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/10jwwERVKLvdrk7tkmqVXeZHGp3Q1lV_2IjFsc6fXQhQ/edit?gid=0#gid=0"

def is_email(value: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", str(value or "").strip()))


def get_previous_month_label() -> str:
    months_id = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    prev_month_date = first_day_this_month - timedelta(days=1)
    return f"{months_id[prev_month_date.month - 1]} {prev_month_date.year}"


def get_emails_from_sheet(spreadsheet_id: str, sheet_name: str) -> list[str]:
    df = read_sheet(spreadsheet_id, sheet_name)
    if df.empty:
        return []

    first_col = df.columns[0]
    values = df[first_col].astype(str).str.strip().tolist()

    emails = [x for x in values if is_email(x)]

    seen = set()
    uniq = []
    for email in emails:
        if email not in seen:
            seen.add(email)
            uniq.append(email)

    return uniq


def build_html_sort_email(
    period_label: str,
    tracker_url: str,
    metabase_url: str,
    sosialisasi_url: str,
    sanggahan_url: str,
    template_url: str,
) -> str:
    blue_color = "#1a73e8"
    red_color = "#c62828"
    link_common_style = f'style="color:{blue_color};text-decoration:underline;font-weight:600"'
    link_red_style = f'style="color:{red_color};text-decoration:underline;font-weight:700"'

    tracker_html = f'<a href="{tracker_url}" target="_blank" {link_common_style}>ID SORT KPI Tracker LINK</a>'
    metabase_html = f'<a href="{metabase_url}" target="_blank" {link_common_style}>LINK METABASE</a>'
    sosialisasi_html = f'<a href="{sosialisasi_url}" target="_blank" {link_common_style}>LINK SOSIALISASI</a>'
    sanggahan_html = f'<a href="{sanggahan_url}" target="_blank" {link_red_style}>LINK SANGGAHAN</a>'
    template_html = f'<a href="{template_url}" target="_blank" {link_common_style}>LINK TEMPLATE</a>'

    return f"""
    <div style="font-family:Arial,Helvetica,sans-serif;font-size:13.5px;color:#222;line-height:1.55">
      <p>Dear all,</p>

      <p>Berikut adalah link untuk sheet <b>SORT KPI Tracker</b> periode <b>{period_label}</b>: {tracker_html}</p>
      <p>Berikut juga link <b>Metabase</b> yang dapat digunakan untuk menarik data secara mandiri untuk monitoring harian: {metabase_html}</p>

      <p>Untuk monitoring performance harian yang belum di-update di tracker bisa diakses secara mandiri dari link-link pada gsheet diatas.</p>

      <p><b>NOTE:</b></p>
      <ul>
        <li>Perlu diingatkan kembali bahwa mulai bulan <b>Oktober 2022</b>, perhitungan KPI Sort akan menggunakan skema penyesuaian KPI Sort terbaru. Terdapat perubahan parameter mulai bulan Maret dan April 2023 sesuai dengan sosialisasi {sosialisasi_html}.</li>
        <li>Sanggahan dibuka pada tanggal <b>2–12 setiap bulannya</b>, dan sanggahan dapat langsung dilakukan melalui google sheet berikut: {sanggahan_html}.</li>
        <li>Wajib menggunakan template yang sudah disediakan pada link terkait ({template_html}) dengan mengisi secara lengkap raw data dan summary. Jika tidak sesuai, sanggahan ditolak.</li>
        <li>Selain data dari Metabase, sanggahan akan ditolak.</li>
        <li>Mohon isi data dengan lengkap dan jelas untuk memudahkan tim dalam validasi sanggahan. Informasi mengenai penerimaan/penolakan sanggahan dapat langsung menghubungi tim FST. Jika terdapat sanggahan melalui email maka sanggahan tidak akan diterima.</li>
      </ul>

      <p>Untuk teman-teman Sort FST, <b>@FST Sort (ID)</b> jika ada sort team (SH/MSH manager atau Sort PIC) yang terlewat di email ini minta tolong juga untuk bisa diinfokan langsung ke tim terkait ya untuk tracker dan link Metabase-nya.</p>

      <p>Terima kasih.
      <br>Regards,
      
      <br><b>BI-Reporting</b></p>
    </div>
    """


def strip_html(html: str) -> str:
    return (
        html.replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
        .replace("</p>", "\n\n")
        .replace("<li>", "• ")
        .replace("</li>", "\n")
    )


def send_day2_email() -> None:
    smtp_user = (os.getenv("EMAIL_USER") or "").strip()
    smtp_password = (os.getenv("EMAIL_PASSWORD") or "").strip()

    if not smtp_user or not smtp_password:
        raise ValueError("EMAIL_USER / EMAIL_PASSWORD belum tersedia di environment.")

    recipients = get_emails_from_sheet(
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["recipients"]
    )

    if not recipients:
        raise ValueError("Recipient kosong atau tidak ada email valid di tab Recipients.")

    period_label = get_previous_month_label()
    subject = f"(ID) Sort KPI Progressive Tiering - {period_label}"

    html_body = build_html_sort_email(
        period_label=period_label,
        tracker_url=GSHEET["tracker"]["url"],
        metabase_url=METABASE_URL,
        sosialisasi_url=SOSIALISASI_URL,
        sanggahan_url=GSHEET["sanggahan"]["url"],
        template_url=TEMPLATE_URL,
    )

    plain_body = strip_html(html_body)

    chunk_size = 50
    for i in range(0, len(recipients), chunk_size):
        to_chunk = recipients[i:i + chunk_size]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SENDER_DISPLAY_NAME} <{SENDER_ALIAS}>"
        msg["To"] = ", ".join(to_chunk)

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_chunk, msg.as_string())

        print(f"Email sent to chunk {i // chunk_size + 1}: {len(to_chunk)} recipients")

    print("\n[9/6] Send email to stakeholders...")
    send_day2_email()

  

    print(f"Day 2 email sent successfully. Subject: {subject}")
