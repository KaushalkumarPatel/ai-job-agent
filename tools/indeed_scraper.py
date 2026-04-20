# indeed_scraper.py - Playwright + BeautifulSoup scraper for Indeed jobs

# Indeed_scraper.py - Playwright + BeautifulSoup scraper for Indeed jobs

from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

from config import JOBS_TIME_FILTER
from utils.output_formatter import format_job_results


@tool
def scrape_indeed_jobs(keyword: str, location: str) -> str:
    """
    Scrapes job listings from Indeed using Playwright to load the page
    and BeautifulSoup to extract the data cleanly.
    Filters for jobs posted in the last 24 hours.
    """

    with sync_playwright() as p:

        # --- Step 1: Playwright loads the page ---
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        page = context.new_page()

        # Remove bot detection flag
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        url = (
            f"https://www.indeed.com/"
            f"?keywords={keyword}"
            f"&location={location}"
            f"&f_TPR={JOBS_TIME_FILTER}"
        )

        print(f"🌐 Loading Indeed page...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Check for auth redirect
        if "authwall" in page.url or "login" in page.url:
            browser.close()
            return "❌ Indeed redirected to login page."

        # Scroll to trigger lazy-loaded content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        # --- Step 2: Get fully rendered HTML ---
        html_content = page.content()
        browser.close()
        print("✅ Page loaded! Now parsing with BeautifulSoup...")

        # --- Step 3: BeautifulSoup parses the HTML ---
        soup = BeautifulSoup(html_content, "html.parser")

        job_cards = (
            soup.find_all("div", class_="job-search-card") or
            soup.find_all("li",  class_="jobs-search__results-list") or
            soup.find_all("div", class_="base-card")
        )

        if not job_cards:
            with open("debug_page.html", "w") as f:
                f.write(html_content)
            return "❌ No job cards found. Saved debug_page.html for inspection."

        print(f"✅ Found {len(job_cards)} job cards!")

        # --- Step 4: Format and return results ---
        return format_job_results(job_cards, location)