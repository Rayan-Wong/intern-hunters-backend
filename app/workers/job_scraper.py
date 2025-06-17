from jobspy import scrape_jobs
import numpy as np

from app.schemas.internship_listings import InternshipListing
from app.exceptions.internship_listings_exceptions import ScraperDown

columns = ["site", "job_url", "title", "company", "date_posted", "description"]

def sync_scrape_jobs(preference: str, start: int, end: int, preferred_industry: str | None = None):
    try:
        if preferred_industry:
            term = (f"{preferred_industry} {preference} (intern OR internship OR co-op OR 'summer intern' OR 'summer analyst')")
        else:
            term = (f"{preference} (intern OR internship OR co-op OR 'summer intern' OR 'summer analyst')")
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=term,
            location="Singapore",
            results_wanted=end-start, # gross, to change,
            hours_old=504, # 3 weeks
            offset=start,
            country_indeed="Singapore",
            linkedin_fetch_description=True,
            description_format="html"
        )
        if jobs.empty:
            return [] # todo: decide what to do if no results
        result = jobs[columns].replace({np.nan: None}) # thanks numpy
        return [InternshipListing(**job) for job in result.to_dict("records")]
    except Exception as e:
        raise ScraperDown from e
