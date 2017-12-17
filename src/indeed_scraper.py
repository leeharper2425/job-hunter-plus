"""
Code that scrapes job listings from Indeed/com.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
import time


def run_scraper(url, dtf):
    """
    Perform the initial web scraping
    :param url: string, the URL of the first web page to scrape
    :param dtf: pandas dataframe, the high-level listings data
    :return: pandas dataframe, the updated listings data
    """
    # Create a termination tag
    flag = "Next"

    # Run the scraper until it runs out of pages
    while "Next" in flag:
        my_soup = create_soup(url)
        flag = my_soup.find(name="span", attrs={"class": "np"}).text
        for div in my_soup.find_all(name="div", attrs={"class": "row"}):
            listing = get_listing_info(div)
            dtf = dtf.append(listing, ignore_index=True)
        url = get_next_url(my_soup)
        time.sleep(5)
    return dtf


def create_soup(url):
    """
    Access a URL and create a soup object.
    :param url: string, the URL of the web page to scrape
    :return: soup object
    """
    page = requests.get(url)
    return BeautifulSoup(page.text, "html.parser")


def get_next_url(soup):
    """
    Get the URL that is obtained by clicking the "next" button
    :param soup: soup object for the web page
    :return: string, the next url for the scraper to use
    """
    linked_urls = soup.find(name="div", attrs={"class": "pagination"})
    return ''.join(["https://www.indeed.com",
                    linked_urls.find_all("a")[-1]["href"]])


def get_listing_info(div):
    """
    Get the results of scraping a single listings job listing.
    :param div: the contents of a single listing's div tag
    :return: dict, the desired scraping information
    """
    return {"job_title": [get_job_title(div)],
            "location": [get_location(div)],
            "company": [get_company_name(div)],
            "url": [get_url_link(div)]}


def get_number_of_jobs(soup):
    """
    Get the number of jobs returned for the search criteria
    :param soup: soup object for the first search page
    :return: int, the number of jobs that the search returns
    """
    tag = soup.find("div", {"id": "searchCount"})
    n_jobs = tag.text.split(" ")[-2]
    return int(n_jobs.replace(",", ""))


def get_job_title(div):
    """
    Extract the job titles from the div tag.
    :param div: tag object, the div tag from a job posting
    :return: string, the job title
    """
    a = div.find(name="a", attrs={"data-tn-element": "jobTitle"})
    return a["title"].replace(",", "")


def get_company_name(div):
    """
    Extract company names from the div tag.
    :param div: tag object, the div tag from a job posting
    :return: string, the company name
    """
    company = div.find(name="span", attrs={"class": "company"})
    a = div.find(name="a", attrs={"data-tn-element": "companyName"})
    if not a:
        return ' '.join(company.text.split()).replace(",", "")
    else:
        return ' '.join(a.text.split()).replace(",", "")


def get_url_link(div):
    """
    Extract the URL link from the div tag.
    :param div: tag object, the div tag from a job posting
    :return: string, the URL of the job posting
    """
    a = div.find(name="a", attrs={"data-tn-element": "jobTitle"})
    return a["href"]


def get_location(div):
    """
    Extract the location of the job posting from the div tag.
    :param div: tag object, the div tag from a job posting
    :return: string, the location of the job posting
    """
    location = div.find(name="span", attrs={"class": "location"})
    return location.text.replace(",", "")


if __name__ == "__main__":
    """Code that runs from the command line."""
    # Load a list of the URLs already in the database:
    # Code to go in here.

    job_url = ''.join(["https://www.indeed.com/jobs?q=data+scientist+intern&l=", str(argv[1]),
                       "&radius=50&sort=date"])
    df = pd.read_csv("data/listings_data.csv")
    df = run_scraper(job_url, df)
    df.to_csv("data/listings_data.csv", index=False)

