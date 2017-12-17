import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
import time


def run_scraper(current_url, dft):
    """
    Run the web scraper that will scrape Indeed
    :param current_url: string, the initial URL to scrape
    :param dft: Pandas dataframe, the listings data from previous scrapings
    :return: dft: Pandas dataframe containing scraped information
    """
    flag = "Next"
    # Run the scraper until it runs out of pages to scrape
    while "Next" in flag:
        my_soup = create_soup(current_url)
        flag = my_soup.find(name="span", attrs={"class": "np"}).text
        print(flag)
        for div in my_soup.find_all(name="div", attrs={"class": "row"}):
            listing = get_listing_info(div)
            dft = dft.append(listing, ignore_index=True)
        current_url = get_next_url(my_soup)
        time.sleep(5)
    return dft


def create_soup(url):
    """
    Get the HTML contents of the URL.
    :param url: string, the url to scrape
    :return: soup: a BeautifulSoup object
    """
    page = requests.get(url)
    return BeautifulSoup(page.text, "html.parser")


def get_next_url(soup):
    """
    Get the URL of the next listings page.
    :param soup: Beautiful soup object
    :return: string, the URL of the next webpage
    """
    d = soup.find(name="div", attrs={"class": "pagination"})
    return ''.join(["https://www.indeed.com", d.find_all("a")[-1]["href"]])


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
    """
    Code that runs if called from the command line
    """
    df = pd.read_csv("data/listings_data.csv")
    first_url = ''.join(["https://www.indeed.com/jobs?q=data+scientist+intern&l=",
                         argv[1], "&radius=50&sort=date"])
    df = run_scraper(first_url, df)
    df.to_csv("data/listings_data.csv", index=False)
