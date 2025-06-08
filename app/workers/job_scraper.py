from jobspy import scrape_jobs
import numpy as np

from app.schemas.internship_listings import InternshipListing

columns = ["site", "job_url", "title", "company", "date_posted", "description"]

def sync_scrape_jobs(preference: str):
    jobs = scrape_jobs(
        site_name=["linkedin", "indeed", "google"],
        search_term=f"{preference}",
        google_search_term=f"{preference} in Singapore since yesterday",
        location="Singapore",
        results_wanted=20,
        hours_old=72,
        country_indeed="Singapore",
        linkedin_fetch_description=True,
        description_format="html"
    )
    result = jobs[columns].replace({np.nan: None}) # thanks numpy
    return [InternshipListing(**job) for job in result.to_dict("records")]