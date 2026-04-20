# output_formatter.py - Handles clean formatting and printing of agent results
def format_job_results(job_cards: list, location: str) -> str:
    """
    Takes a list of BeautifulSoup job card elements
    and formats them into a clean, readable string.
    """
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

        title   = title_tag.get_text(strip=True)    if title_tag    else "N/A"
        company = company_tag.get_text(strip=True)  if company_tag  else "N/A"
        loc     = location_tag.get_text(strip=True) if location_tag else "N/A"
        link    = link_tag["href"]                  if link_tag     else "N/A"

        results += f"{i}. 💼 {title}\n"
        results += f"   🏢 Company  : {company}\n"
        results += f"   📍 Location : {loc}\n"
        results += f"   🔗 Link     : {link}\n\n"

    return results