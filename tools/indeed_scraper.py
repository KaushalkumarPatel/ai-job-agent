import requests
import os
from langchain_core.tools import tool
from dotenv import load_dotenv

# Load environment variables (like JSEARCH_API_KEY) from .env file
load_dotenv()

@tool
def scrape_indeed_jobs(keyword: str, location: str, days: int = 7) -> str:
    """
    Fetches job listings via JSearch API (RapidAPI).
    days = how many days back to search (e.g. 1 = last 24hrs, 7 = last week)
    """

    api_key = os.getenv("JSEARCH_API_KEY")

    if not api_key:
        return "❌ JSEARCH_API_KEY not found in .env file."

    url = "https://jsearch.p.rapidapi.com/search"

    # JSearch date_posted options: all / today / 3days / week / month
    date_map = {
        1: "today",
        2: "3days",
        3: "3days",
        7: "week",
        30: "month"
    }
    # Default to week if exact days match isn't found
    date_posted = date_map.get(days, "week")   
    

    params = {
        "query":       f"{keyword} in {location} ",  # Searches everywhere (StepStone, LinkedIn, Xing, etc.)
        "page":        "1",
        "num_pages":   "1",
        "date_posted": date_posted,
        "country":     "de",                        # Germany
        "language":    "de",                        # Changed to German so "Softwareentwickler" works
    }

    headers = {
        "X-RapidAPI-Key":  api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    print(f"🌐 Calling JSearch API for '{keyword}' in '{location}' (Last {days} days)...")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"❌ JSearch API request failed: {e}"

    data = response.json()
    jobs = data.get("data", [])

    # --- DEBUG LINE: This will show you exactly what RapidAPI returns ---
    print(f"🐛 DEBUG API RESPONSE: Found {len(jobs)} jobs. API Status: {data.get('status')}")

    if not jobs:
        return (
            f"❌ No jobs found for '{keyword}' in '{location}'.\n"
            f"💡 Try: broader keyword or increase days range."
        )

    print(f"✅ Found {len(jobs)} jobs via JSearch!")

    # ── Format results ─────────────────────────────────────────
    results  = f"🤖 Jobs for '{keyword}' in {location} "
    results += f"(Last {days} days):\n"
    results += "=" * 50 + "\n\n"

    for i, job in enumerate(jobs[:10], start=1):
        title    = job.get("job_title",           "N/A")
        company  = job.get("employer_name",       "N/A")
        loc      = job.get("job_city",            "N/A")
        link     = job.get("job_apply_link",      "N/A")
        posted   = job.get("job_posted_at_datetime_utc", "N/A")

        # Sometimes city is missing but country/state is there
        if loc == "N/A":
            loc = job.get("job_state", job.get("job_country", "Germany"))

        results += f"{i}. 💼 {title}\n"
        results += f"   🏢 Company  : {company}\n"
        results += f"   📍 Location : {loc}\n"
        results += f"   📅 Posted   : {posted}\n"
        results += f"   🔗 Link     : {link}\n\n"

    return results