# ว่าง = ดูรายชื่อ / ใส่ชื่อไฟล์ = อ่านเนื้อหา
FILE = ""

import json
from urllib.request import urlopen, Request
from urllib.parse import quote

REPO = "Boonyapat-12/async-2026-CDTI"

def fetch(url):
    return urlopen(Request(url, headers={"User-Agent": "vLab-reader"}),
                   timeout=30)

try:
    if not FILE:
        url = f"https://api.github.com/repos/{REPO}/git/trees/HEAD?recursive=1"
        with fetch(url) as response:
            data = json.load(response)
        for item in data["tree"]:
            icon = "[DIR] " if item["type"] == "tree" else "      "
            print(icon + item["path"])
        if data.get("truncated"):
            print("\nรายการจาก GitHub ไม่ครบ เพราะ repo มีขนาดใหญ่")
    else:
        url = f"https://raw.githubusercontent.com/{REPO}/HEAD/{quote(FILE, safe='/')}"
        with fetch(url) as response:
            text = response.read().decode("utf-8-sig")
        print(f"===== {FILE} =====\n")
        print(text)
except Exception as error:
    print("อ่านไม่สำเร็จ:", error)