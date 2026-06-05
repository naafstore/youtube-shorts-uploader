import os, json, pickle, base64, re, tempfile, io
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SHEET_RANGE = "Sheet1!A:F"
CLIENT_SECRET_B64 = os.environ["CLIENT_SECRET_B64"]
TOKEN_PICKLE_B64 = os.environ["TOKEN_PICKLE_B64"]


def get_services():
    client_config = json.loads(base64.b64decode(CLIENT_SECRET_B64).decode())
    creds = pickle.loads(base64.b64decode(TOKEN_PICKLE_B64))
    if creds.expired:
        creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    sheets = build("sheets", "v4", credentials=creds)
    return youtube, drive, sheets, creds


def get_pending_videos(sheets):
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE
    ).execute()
    values = result.get("values", [])
    pending = []
    for i, row in enumerate(values, start=1):
        if i == 1:
            continue
        if len(row) < 5:
            continue
        title = row[0].strip()
        desc = row[1].strip() if len(row) > 1 else ""
        tags = row[2].strip() if len(row) > 2 else ""
        link = row[3].strip() if len(row) > 3 else ""
        jadwal = row[4].strip() if len(row) > 4 else ""
        status = row[5].strip().lower() if len(row) > 5 else ""
        if status == "done" or not link or not jadwal:
            continue
        try:
            t = datetime.strptime(jadwal, "%Y-%m-%d %H:%M")
            if t <= datetime.now():
                pending.append((i, title, desc, tags, link))
        except ValueError:
            continue
    return pending


def extract_file_id(link):
    m = re.search(r"(?:/d/|id=)([a-zA-Z0-9_-]+)", link)
    return m.group(1) if m else link.strip()


def download_video(drive, file_id):
    req = drive.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(buf.getvalue())
    tmp.close()
    return tmp.name


def upload(youtube, path, title, desc, tags):
    body = {
        "snippet": {
            "title": title,
            "description": desc,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(path, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  Progress: {int(status.progress() * 100)}%")
    return resp


def mark_done(sheets, row):
    sheets.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"F{row}",
        valueInputOption="USER_ENTERED",
        body={"values": [["done"]]},
    ).execute()


def save_updated_token(creds):
    b64 = base64.b64encode(pickle.dumps(creds)).decode()
    print(f"\nTOKEN_PICKLE_B64={b64}")
    print("⚠️ Update GH secret TOKEN_PICKLE_B64 dengan nilai di atas!")


def main():
    print(f"Mulai {datetime.now()}")
    yt, dr, sh, creds = get_services()
    pending = get_pending_videos(sh)
    if not pending:
        print("Tidak ada video terjadwal.")
        save_updated_token(creds)
        return
    for row, title, desc, tags, link in pending:
        print(f"\nUpload: {title}")
        fid = extract_file_id(link)
        print(f"Download dari Drive...")
        path = download_video(dr, fid)
        try:
            result = upload(yt, path, title, desc, tags)
            vid = result["id"]
            print(f"✅ https://youtu.be/{vid}")
            mark_done(sh, row)
        finally:
            os.unlink(path)
    save_updated_token(creds)


if __name__ == "__main__":
    main()
