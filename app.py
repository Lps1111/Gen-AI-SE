# app.py
import asyncio
import hashlib
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright

from sites import SITES
from db import init_db, upsert_headlines, fetch_by_date
from export_excel import export_to_excel
from briefing import write_briefing

OUTPUT_DIR = Path("output")


def normalize_url(base: str, href: str) -> str:
    if not href:
        return ""
    return urljoin(base, href)


def make_title_hash(title: str) -> str:
    cleaned = " ".join(title.lower().split()).strip()
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:24]


def is_valid_candidate(site_url: str, title: str, url: str) -> bool:
    """
    Filters out junk links and keeps high-probability article headlines.
    """
    if not title or not url:
        return False

    title = title.strip()

    # Title length rules
    if len(title) < 20:
        return False
    if len(title) > 160:
        return False

    # URL must be http(s)
    if not url.startswith("http"):
        return False

    # Keep same domain (reduces external/junk)
    site_domain = urlparse(site_url).netloc.replace("www.", "")
    u_domain = urlparse(url).netloc.replace("www.", "")
    if site_domain and u_domain and site_domain not in u_domain:
        return False

    # Avoid obvious non-article pages
    bad_words = [
        "subscribe", "subscription", "sign in", "log in", "newsletter",
        "privacy", "terms", "cookies", "advertise", "contact", "about",
        "podcast", "live", "watch", "listen"
    ]
    tl = title.lower()
    if any(b in tl for b in bad_words):
        return False

    return True


async def scrape_site(page, site: dict) -> list[dict]:
    name = site["name"]
    base_url = site["url"]
    selectors = site["selectors"]
    max_items = site.get("max_items", 40)

    await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(1500)  # settle for dynamic content

    results = []
    seen = set()

    for sel in selectors:
        try:
            elements = await page.query_selector_all(sel)
        except Exception:
            continue

        for el in elements:
            try:
                text = (await el.inner_text()) or ""
                href = await el.get_attribute("href") or ""
                full_url = normalize_url(base_url, href)

                text = " ".join(text.split()).strip()

                if not is_valid_candidate(base_url, text, full_url):
                    continue

                # Deduplicate in-session
                key = (text.lower(), full_url)
                if key in seen:
                    continue
                seen.add(key)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                results.append({
                    "source": name,
                    "title": text,
                    "url": full_url,
                    "collected_at": now,
                    "title_hash": make_title_hash(text)
                })

                if len(results) >= max_items:
                    break
            except Exception:
                continue

        if len(results) >= max_items:
            break

    return results


async def run_pipeline() -> None:
    # 1) Initialize DB
    init_db()

    # 2) Scrape sites
    all_items = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for site in SITES:
            try:
                items = await scrape_site(page, site)
                all_items.extend(items)
                print(f"[OK] {site['name']}: scraped {len(items)}")
            except Exception as e:
                print(f"[ERROR] {site['name']}: {e}")

        await context.close()
        await browser.close()

    # 3) Save to DB (dedupe)
    inserted = upsert_headlines(all_items)
    print(f"New headlines inserted: {inserted}")

    # 4) Fetch today's headlines
    today = date.today().strftime("%Y-%m-%d")
    rows = fetch_by_date(today)

    # 5) Export Excel + Briefing
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    excel_path = OUTPUT_DIR / f"news_{today}.xlsx"
    md_path = OUTPUT_DIR / f"briefing_{today}.md"
    txt_path = OUTPUT_DIR / f"briefing_{today}.txt"

    export_to_excel(rows, excel_path)
    write_briefing(rows, md_path, txt_path)

    print(f"Saved: {excel_path}")
    print(f"Saved: {md_path}")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
