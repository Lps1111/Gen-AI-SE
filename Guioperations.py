import time
import os
import pyautogui
import requests
from bs4 import BeautifulSoup

URL = "https://www.thehindu.com/"
OUTFILE = "thehindu_headlines.txt"

def open_chrome_and_navigate(url: str):
    # Safety: move mouse to top-left corner to abort (PyAutoGUI failsafe)
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.3

    # 1) Open Start menu
    pyautogui.press("win")
    time.sleep(0.5)

    # 2) Type Chrome and open
    pyautogui.write("chrome", interval=0.05)
    time.sleep(0.5)
    pyautogui.press("enter")

    # 3) Wait Chrome to open
    time.sleep(2.5)

    # 4) Focus address bar and type URL
    pyautogui.hotkey("ctrl", "l")
    pyautogui.write(url, interval=0.03)
    pyautogui.press("enter")

    # 5) Wait for page load
    time.sleep(5)

def scrape_headlines(url: str, max_items: int = 25):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    # Common pattern on many news sites: headlines in h2/h3 with links
    candidates = []
    for tag in soup.select("h2 a, h3 a"):
        text = tag.get_text(" ", strip=True)
        href = tag.get("href", "").strip()
        if text and href and "thehindu.com" in href:
            candidates.append((text, href))

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for t, h in candidates:
        key = (t, h)
        if key not in seen:
            seen.add(key)
            unique.append((t, h))

    return unique[:max_items]

def save_headlines(items, outfile: str):
    with open(outfile, "w", encoding="utf-8") as f:
        for i, (title, link) in enumerate(items, start=1):
            f.write(f"{i}. {title}\n   {link}\n\n")

def main():
    print("Opening browser with PyAutoGUI...")
    open_chrome_and_navigate(URL)

    print("Scraping headlines with requests+BeautifulSoup...")
    items = scrape_headlines(URL, max_items=30)

    if not items:
        print("No headlines found (site HTML may have changed).")
    else:
        save_headlines(items, OUTFILE)
        print(f"Saved {len(items)} headlines to: {os.path.abspath(OUTFILE)}")

if __name__ == "__main__":
    main()
