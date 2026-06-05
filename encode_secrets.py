import base64, json, pickle

# 1. Baca & encode client_secret.json
with open("client_secret.json", "rb") as f:
    cs_b64 = base64.b64encode(f.read()).decode()

print("=" * 60)
print("CLIENT_SECRET_B64 (copy ini ke GitHub secret):")
print("=" * 60)
print(cs_b64)

# 2. Baca & encode token.pickle
with open("token.pickle", "rb") as f:
    tk_b64 = base64.b64encode(f.read()).decode()

print("\n" + "=" * 60)
print("TOKEN_PICKLE_B64 (copy ini ke GitHub secret):")
print("=" * 60)
print(tk_b64)

print("\n" + "=" * 60)
print("SPREADSHEET_ID (copy dari URL spreadsheet):")
print("=" * 60)
print("https://docs.google.com/spreadsheets/d/ ---INI-YANG-DI-COPY--- /edit")
