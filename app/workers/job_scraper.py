from jobspy import scrape_jobs
import numpy as np

from app.schemas.internship_listings import InternshipListing
from app.exceptions.internship_listings_exceptions import ScraperDown

columns = ["site", "job_url", "title", "company", "date_posted", "description"]

def sync_scrape_jobs(preference: str, start: int, end: int):
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=f"{preference}",
            location="Singapore",
            results_wanted=end-start, # gross, to change,
            hours_old=168,
            offset=start,
            country_indeed="Singapore",
            linkedin_fetch_description=True,
            description_format="html"
        )
        if jobs is None:
            return [] # todo: decide what to do if no results
        result = jobs[columns].replace({np.nan: None}) # thanks numpy
        return [InternshipListing(**job) for job in result.to_dict("records")]
    except Exception as e:
        raise ScraperDown from e