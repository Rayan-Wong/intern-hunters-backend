"""Modules responsible for jobspy and post-processing"""
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from jobspy import scrape_jobs
import numpy as np

from app.schemas.internship_listings import InternshipListing
from app.exceptions.internship_listings_exceptions import ScraperDown
from app.core.timer import timed
from app.core.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

TIMEOUT = 60

columns = [
    "site",
    "job_url",
    "title",
    "company",
    "date_posted",
    "is_remote",
    "company_industry",
    "description"
]

MAX_HOURS = 24 * 7 * 3 # number of hours in a day * number of hours in a week * number of weeks in a month

@timed("Internship Scraper")
def sync_scrape_jobs(preference: str, start: int, end: int, preferred_industry: str | None = None):
    """Calls JobSpy API to produce internship listings. start, end are used to simulate pagination,
    preferred_industry to specify industry of company"""
    try:
        if preferred_industry:
            term = f"{preferred_industry} {preference} (intern OR internship OR co-op OR 'summer intern' OR 'summer analyst')"
        else:
            term = f"{preference} (intern OR internship OR co-op OR 'summer intern' OR 'summer analyst')"
        logger.info(f"Starting API call value: {start}, Ending API call value: {end}")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                scrape_jobs,
                site_name=["linkedin", "indeed"],
                search_term=term,
                location="Singapore",
                results_wanted=end-start, # gross, to change,
                hours_old=MAX_HOURS, # 3 weeks
                offset=start,
                country_indeed="Singapore",
                linkedin_fetch_description=True,
                description_format="html"
            )
            try:
                jobs = future.result(timeout=TIMEOUT)
            except TimeoutError:
                logger.error("Job Scraper API took too long to respond!")
                raise ScraperDown from TimeoutError
        if jobs.empty:
            return [] # todo: decide what to do if no results
        result = jobs[columns].replace({np.nan: None}) # thanks numpy
        logger.info(f"Internship Scraper found {len(result)} listings.")
        return list(dict.fromkeys(InternshipListing(**job) for job in result.to_dict("records")))
    except Exception as e:
        logger.error(f"Scraper encountered issue: {e}")
        raise ScraperDown from e
