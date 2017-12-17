import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
from collections import defaultdict
from time import sleep


def run_scraper(current_url, dft):
    """
    Run the web scraper that will scrape Indeed
    :param current_url: string, the initial URL to scrape
    :param dft: Pandas dataframe, the listings data from previous scrapings
    :return: dft: Pandas dataframe containing scraped information
    """
    flag = "Next"
    listings = defaultdict(list)

    # Run the scraper until it runs out of pages to scrape
    while "Next" in flag:
        my_soup = create_soup(current_url)
        flag = my_soup.find(name="span", attrs={"class": "np"}).text
        for div in my_soup.find_all(name="div", attrs={"class": "row"}):
            listings = add_listing_info(div, listings)
            sleep(5)
        current_url = get_next_url(my_soup)
        sleep(5)
    dft = dft.append(pd.DataFrame(listings), ignore_index=True)
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


def add_listing_info(div, lst_dict):
    """
    Get the results of scraping a single listings job listing.
    :param div: the contents of a single listing's div tag
    :param lst_dict: the currently scraped listings
    :return: lst_dict, the desired scraping information
    """
    lst_dict["job_title"] += [get_job_title(div)]
    lst_dict["location"] += [get_location(div)]
    lst_dict["company"] += [get_company_name(div)]
    lst_dict["jobsite"] += ["Indeed"]
    spec_link = get_url_link(div)
    lst_dict["url"] += [spec_link]
    lst_dict["job_description"] += [get_job_description(spec_link)]
    return lst_dict


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


def get_job_description(link):
    """
    Get the raw text of the job description from the linked webpage.
    :param link: str, the url of the job description webpage
    :return: str, the text from the webpage
    """
    soup = create_soup(''.join(["https://www.indeed.com", link]))

    # Remove all script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop any blank lines
    return '\n'.join(chunk for chunk in chunks if chunk)


if __name__ == "__main__":
    """
    Code that runs if called from the command line
    """
    df = pd.read_csv("data/listings_data.csv")
    first_url = ''.join(["https://www.indeed.com/jobs?q=data+scientist+intern&l=",
                         argv[1], "&radius=50&sort=date"])
    df = run_scraper(first_url, df)
    df.to_csv("data/listings_data.csv", index=False)
