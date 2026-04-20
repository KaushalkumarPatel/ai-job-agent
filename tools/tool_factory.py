# tool_factory.py - Maps website name strings to actual tool objects
# Example: ["linkedin", "indeed"] -> [scrape_linkedin_jobs, scrape_indeed_jobs]

from tools.linkedin_scraper import scrape_linkedin_jobs
from tools.indeed_scraper import scrape_indeed_jobs 
from tools.jobboerse_scraper import scrape_jobboerse_jobs 


def get_tools() -> list:
    """
    Returns the full list of tools available to the agent.
    Add new scrapers here as you build them.
    """
    return [
        scrape_linkedin_jobs,
        scrape_indeed_jobs,
        scrape_jobboerse_jobs
    ]