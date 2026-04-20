from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

@tool
def scrape_jobs_with_bs4(keyword: str, location: str) -> str:
    """
    Scrapes job listings using Playwright to load the page
    and BeautifulSoup to extract the data cleanly.
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

        # LinkedIn URL with 24hr filter
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={keyword}"
            f"&location={location}"
            f"&f_TPR=r86400"
        )

        print(f"🌐 Loading page...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)  # Wait for JS to render

        # Check for auth redirect
        if "authwall" in page.url or "login" in page.url:
            browser.close()
            return "❌ LinkedIn redirected to login page."

        # Scroll down to load more jobs (LinkedIn is lazy-loaded)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        # --- Step 2: Get the fully rendered HTML ---
        html_content = page.content()  # ← This is where BS4 takes over!
        browser.close()
        print("✅ Page loaded! Now parsing with BeautifulSoup...")

        # --- Step 3: BeautifulSoup parses the HTML ---
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all job cards
        job_cards = (
            soup.find_all("div", class_="job-search-card") or
            soup.find_all("li", class_="jobs-search__results-list") or
            soup.find_all("div", class_="base-card")
        )

        if not job_cards:
            # Save HTML for debugging
            with open("debug_page.html", "w") as f:
                f.write(html_content)
            return "❌ No job cards found. Saved debug_page.html for inspection."

        print(f"✅ Found {len(job_cards)} job cards!")

        # --- Step 4: Extract job details cleanly ---
        results = f"🤖 Robotics Jobs in {location} (Last 24 Hours):\n"
        results += "=" * 50 + "\n\n"

        for i, card in enumerate(job_cards[:10], start=1):
            # Extract Title
            title_tag = (
                card.find("h3", class_="base-search-card__title") or
                card.find("h3") or
                card.find("span", class_="sr-only")
            )

            # Extract Company
            company_tag = (
                card.find("h4", class_="base-search-card__subtitle") or
                card.find("a", class_="hidden-nested-link") or
                card.find("h4")
            )

            # Extract Location
            location_tag = (
                card.find("span", class_="job-search-card__location") or
                card.find("span", class_="base-search-card__metadata")
            )

            # Extract Link
            link_tag = card.find("a", href=True)

            title    = title_tag.get_text(strip=True)    if title_tag    else "N/A"
            company  = company_tag.get_text(strip=True)  if company_tag  else "N/A"
            location = location_tag.get_text(strip=True) if location_tag else "N/A"
            link     = link_tag["href"]                  if link_tag     else "N/A"

            results += f"{i}. 💼 {title}\n"
            results += f"   🏢 Company  : {company}\n"
            results += f"   📍 Location : {location}\n"
            results += f"   🔗 Link     : {link}\n\n"

        return results

llm = ChatOllama(model="qwen3.5:9b", temperature=0)

agent = create_agent(
    model=llm,
    tools=[scrape_jobs_with_bs4],
    system_prompt="You are a precise agent. Search for jobs posted in the last 24 hours in Germany."
)

# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Find robotics jobs posted in the last 24 hours in Hamburg Germany in LinkedIn."}]}
)
final_answer = result["messages"][-1].content
print(final_answer)