import os
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def download_welfake():
    out = DATA_DIR / "WELFake"
    out.mkdir(exist_ok=True)

    print("[*] Downloading WELFake dataset...")

    os.system("kaggle datasets download -d saurabhshahane/fake-news-classification -p data/WELFake --unzip")

    print(f"✓ Saved to {out}")

download_welfake()