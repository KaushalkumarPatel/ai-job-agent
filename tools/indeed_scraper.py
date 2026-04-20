from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

from config import JOBS_TIME_FILTER
from utils.output_formatter import format_job_results


def format_job_results_indeed(job_cards: list, location: str) -> str:
    """
    Indeed-specific formatter because Indeed uses
    different HTML structure than LinkedIn.
    """
    results  = f"🤖 Robotics Jobs on Indeed in {location} (Last 24 Hours):\n"
    results += "=" * 50 + "\n\n"

    for i, card in enumerate(job_cards[:10], start=1):

        # Indeed title is inside <h2> with class "jobTitle"
        title_tag = (
            card.find("h2",   class_="jobTitle") or
            card.find("span", attrs={"title": True})
        )

        # Indeed company name
        company_tag = (
            card.find("span", class_="companyName") or
            card.find("a",    class_="companyName") or
            card.find("span", attrs={"data-testid": "company-name"})
        )

        # Indeed location
        location_tag = (
            card.find("div",  class_="companyLocation") or
            card.find("span", attrs={"data-testid": "text-location"})
        )

        # Indeed job link — find nearest <a> with /rc/clk or /pagead
        link_tag = card.find("a", href=True)

        title   = title_tag.get_text(strip=True)    if title_tag    else "N/A"
        company = company_tag.get_text(strip=True)  if company_tag  else "N/A"
        loc     = location_tag.get_text(strip=True) if location_tag else "N/A"
        link    = "https://de.indeed.com" + link_tag["href"] \
                  if link_tag and link_tag["href"].startswith("/") \
                  else (link_tag["href"] if link_tag else "N/A")

        results += f"{i}. 💼 {title}\n"
        results += f"   🏢 Company  : {company}\n"
        results += f"   📍 Location : {loc}\n"
        results += f"   🔗 Link     : {link}\n\n"

    return results

@tool
def scrape_indeed_jobs(keyword: str, location: str) -> str:
    """
    Scrapes job listings from Indeed Germany using Playwright
    and BeautifulSoup. Uses de.indeed.com for German results.
    """

    with sync_playwright() as p:

        # ── 1. Launch browser ───────────────────────────────────
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="de-DE",               # ← German locale for de.indeed.com
        )

        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # ── 2. Build URL ────────────────────────────────────────
        # fromage=1 = last 24 hours on Indeed
        url = (
            f"https://de.indeed.com/jobs"
            f"?q={keyword}"
            f"&l={location}"
            f"&fromage=1"
        )

        print(f"🌐 Loading Indeed page...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Check for CAPTCHA or block page
        if "captcha" in page.url or "blocked" in page.url:
            browser.close()
            return "❌ Indeed blocked the request (CAPTCHA detected)."

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        html_content = page.content()
        browser.close()
        print("✅ Page loaded! Now parsing with BeautifulSoup...")

        # ── 3. Parse HTML ───────────────────────────────────────
        soup = BeautifulSoup(html_content, "html.parser")

        job_cards = (
            soup.find_all("div", class_="job_seen_beacon") or
            soup.find_all("div", class_="cardOutline") or
            soup.find_all("td",  class_="resultContent")
        )

        if not job_cards:
            with open("debug_indeed.html", "w") as f:
                f.write(html_content)
            return "❌ No job cards found on Indeed. Saved debug_indeed.html"

        print(f"✅ Found {len(job_cards)} job cards on Indeed!")

        # ── 4. Format using indeed-specific selectors ───────────
        return format_job_results_indeed(job_cards, location)


