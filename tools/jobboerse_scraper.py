# tools/jobboerse_scraper.py — REWRITE using REST API

import requests
from langchain_core.tools import tool


@tool
def scrape_jobboerse_jobs(keyword: str, location: str) -> str:
    """
    Fetches job listings from Jobbörse via their official
    public REST API. No browser needed — faster and more reliable.
    """

    # ── Official public API — no auth key needed ──────────────
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"

    params = {
        "was":                keyword,    # job title / keyword
        "wo":                 location,   # location
        "angebotsart":        1,          # 1 = jobs (not apprenticeships)
        "veroeffentlichtseit": 1,         # published within last 1 day
        "size":               10,         # number of results
        "page":               1,
    }

    headers = {
        "X-API-Key": "jobboerse-jobsuche",   # public key, no registration needed
        "Accept":    "application/json",
    }

    print(f"🌐 Calling Jobbörse API for '{keyword}' in '{location}'...")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"❌ Jobbörse API request failed: {e}"

    data = response.json()

    # ── Parse response ─────────────────────────────────────────
    jobs = data.get("stellenangebote", [])

    if not jobs:
        return (
            f"❌ No jobs found on Jobbörse for '{keyword}' in '{location}'.\n"
            f"💡 Try German keywords: Robotik"
        )

    print(f"✅ Found {len(jobs)} jobs on Jobbörse!")

    results  = f"🤖 Jobs on Jobbörse for '{keyword}' in {location}:\n"
    results += "=" * 50 + "\n\n"

    for i, job in enumerate(jobs, start=1):
        title    = job.get("titel",             "N/A")
        company  = job.get("arbeitgeber",       "N/A")
        loc      = job.get("arbeitsort", {}).get("ort", "N/A")
        ref      = job.get("refnr",             "N/A")

        # Build job detail link from reference number
        link = f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref}"

        results += f"{i}. 💼 {title}\n"
        results += f"   🏢 Company  : {company}\n"
        results += f"   📍 Location : {loc}\n"
        results += f"   🔗 Link     : {link}\n\n"

    return results