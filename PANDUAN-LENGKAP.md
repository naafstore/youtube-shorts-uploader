# PANDUAN LENGKAP — YouTube Shorts Upload Otomatis via Spreadsheet

## Arsitektur

```
Google Spreadsheet (jadwal + link video)
        │
        ▼
GitHub Actions (jalan tiap 15 menit, GRATIS, 24/7)
        │
        ├── Google Sheets API → baca jadwal
        ├── Google Drive API  → download video
        └── YouTube Data API  → upload shorts
```

**Laptop boleh mati.** Semua jalan di cloud GitHub.

---

## Langkah 1 — Setup Google Cloud Project

1. Buka https://console.cloud.google.com
2. Buat project baru: **youtube-shorts-uploader**
3. Buka menu **APIs & Services > Library**
4. Cari dan ENABLE 3 API ini satu per satu:
   - **YouTube Data API v3**
   - **Google Sheets API**
   - **Google Drive API**

---

## Langkah 2 — Buat OAuth Credentials

### 2a. OAuth Consent Screen
1. Buka **APIs & Services > OAuth consent screen**
2. Pilih **External**, klik **CREATE**
3. Isi:
   - App name: `Youtube Shorts Uploader`
   - User support email: pilih email kamu
   - Developer contact: email kamu
4. Klik **SAVE AND CONTINUE** sampai masuk step **Test users**
5. Di halaman **Test users**, klik **ADD USERS**
6. Masukkan **email Google/YouTube** yang terdaftar di channel tujuan upload
7. Klik **SAVE AND CONTINUE** sampai selesai

### 2b. OAuth Client ID
1. Buka **APIs & Services > Credentials**
2. Klik **+ Create Credentials > OAuth client ID**
3. Application type: **Desktop app**
4. Name: `Desktop Client 1`
5. Klik **CREATE**
6. Klik **DOWNLOAD JSON** → simpan sebagai **`client_secret.json`** di folder proyek

---

## Langkah 3 — Buat Google Spreadsheet

1. Buka https://sheets.new
2. Buat kolom seperti ini (baris 1 = header):

| A (Judul) | B (Deskripsi) | C (Tags) | D (Link Google Drive) | E (Jadwal) | F (Status) |
|---|---|---|---|---|---|
| Tips Python #1 | Belajar coding #shorts | python, coding | https://drive.google.com/file/d/ABC123 | 2026-06-10 10:00 | |
| Tips Python #2 | Lanjutan #shorts | python, shorts | https://drive.google.com/file/d/DEF456 | 2026-06-10 14:00 | |

**Aturan:**
- Format jadwal: `YYYY-MM-DD HH:MM` (24 jam)
- **Timezone: WIB (UTC+7)** — tulis jam Indonesia, script otomatis pakai WIB
- Link Drive: bisa URL lengkap atau langsung file ID
- Kolom F (Status) harus **kosong** untuk video yang antri — nanti otomatis berubah jadi `done`

3. Copy **Spreadsheet ID** dari URL:
   `https://docs.google.com/spreadsheets/d/`**`SPREADSHEET_ID_INI`**`/edit`

---

## Langkah 4 — Setup Folder & .gitignore (PENTING!)

Buka terminal/CMD di folder proyek. Jalankan:

```
echo client_secret.json > .gitignore
echo token.pickle >> .gitignore
echo __pycache__/ >> .gitignore
```

> **⚠️ PERINGATAN:** Jangan pakai tanda petik di .gitignore. Isinya harus:
> ```
> client_secret.json
> token.pickle
> __pycache__/
> ```
> (tanpa tanda kutip)

---

## Langkah 5 — Auth Lokal (Jalankan di Laptop SEKARANG)

```
pip install -r requirements.txt
python auth.py
```

Browser akan terbuka. Login dengan **akun Google yang terdaftar sebagai Test User** (Langkah 2a). Setelah sukses, terminal akan muncul:

```
✅ OAuth berhasil! token.pickle tersimpan.
Refresh token: 1//0gABCDEF...
```

Sekarang folder berisi:
```
client_secret.json  ← hasil download dari Google Cloud
token.pickle        ← hasil dari auth.py
main.py             ← script upload
auth.py             ← script auth
encode_secrets.py   ← helper encode
requirements.txt
.gitignore
.github/workflows/upload.yml
```

---

## Langkah 6 — Encode Secrets untuk GitHub

Jalankan:

```
python encode_secrets.py
```

Akan muncul 3 output. Copy masing-masing ke notepad/sementara:

| Output | Simpan sebagai |
|---|---|
| Teks panjang PERTAMA | `CLIENT_SECRET_B64` |
| Teks panjang KEDUA | `TOKEN_PICKLE_B64` |
| Spreadsheet ID | `SPREADSHEET_ID` |

---

## Langkah 7 — Buat Repository GitHub & Push

### 7a. Buat repo di GitHub
1. Buka https://github.com/new
2. **Repository name**: `youtube-shorts-uploader`
3. **Jangan centang apa-apa** (tidak boleh ada README, .gitignore, atau license)
4. Klik **Create repository**

### 7b. Push dari terminal
```
git init
git add .
git commit -m "init: youtube shorts uploader"
git branch -M main
git remote add origin https://github.com/naafstore/youtube-shorts-uploader.git
git push -u origin main
```

---

## Langkah 8 — Set GitHub Secrets

1. Buka https://github.com/naafstore/youtube-shorts-uploader
2. Klik tab **Settings** → sidebar kiri **Secrets and variables** → **Actions**
3. Klik **New repository secret**, buat 3 secret:

| Name | Value |
|---|---|
| `SPREADSHEET_ID` | ID spreadsheet (dari Langkah 3) |
| `CLIENT_SECRET_B64` | Teks panjang pertama (dari Langkah 6) |
| `TOKEN_PICKLE_B64` | Teks panjang kedua (dari Langkah 6) |

---

## Langkah 9 — Jalankan Workflow

1. Klik tab **Actions** di repository GitHub
2. Klik **I understand my workflows, go ahead and enable them**
3. Klik **Run workflow** → **Run workflow** (untuk tes manual)

Workflow juga akan jalan otomatis **setiap 15 menit** (cek jadwal di file `.github/workflows/upload.yml` baris `cron`). Keterlambatan beberapa menit wajar karena antrian GitHub gratis.

---

## Cara Pakai Sehari-hari

1. Upload video ke **Google Drive** (bisa dari HP atau laptop)
2. Buka spreadsheet, tambah baris baru:
   - Judul, deskripsi, tags
   - Link video dari Google Drive
   - Jadwal upload
   - Biarkan Status kosong
3. **Tutup laptop.** GitHub Actions akan upload otomatis sesuai jadwal.

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| `ModuleNotFoundError: No module named 'google_auth_oauthlib'` | Jalankan `pip install -r requirements.txt` dulu |
| `google.auth.exceptions.RefreshError` | `token.pickle` expired. Hapus file, jalankan `python auth.py` lagi |
| Workflow gagal: secrets not found | Cek GitHub Secrets — nama harus PERSIS `SPREADSHEET_ID`, `CLIENT_SECRET_B64`, `TOKEN_PICKLE_B64` |
| Push ditolak karena secret | Pastikan .gitignore benar (tanpa kutip) dan sudah ada sebelum `git add .` |
| Video tidak terupload sesuai jadwal | Cek apakah jadwal pakai **WIB** (bukan UTC). Script sudah otomatis pakai WIB. Jika jam sekarang belum melewati jadwal WIB, video akan dilewati |
| Workflow sukses (centang hijau) tapi video tidak muncul di YouTube | Klik workflow run → buka step "Run python main.py" → cari baris `✅ https://youtu.be/...`. Jika tidak ada, berarti ada error di proses download/upload. Lihat teks merah di log |
