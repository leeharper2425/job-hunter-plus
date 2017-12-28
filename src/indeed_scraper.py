import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
from collections import defaultdict
from time import sleep
import os
import boto3
from io import StringIO, BytesIO


def run_scraper(current_url, dft):
    """
    Run the web scraper that will scrape Indeed
    :param current_url: string, the initial URL to scrape
    :param dft: Pandas dataframe, the listings data from previous scrapings
    :return: dft: Pandas dataframe containing scraped information
    """
    flag = True
    listings = defaultdict(list)
    # Run the scraper until it runs out of pages to scrape
    while flag:
        my_soup = create_soup(current_url)
        flag = check_flag(my_soup)
        for div in my_soup.find_all(name="div", attrs={"class": "row"}):
            listings = add_listing_info(div, listings)
            sleep(4)
        # Save the file after each results page, in case of failure
        dft2 = dft.append(pd.DataFrame(listings), ignore_index=True)
        write_file_to_s3(dft2)
        current_url = get_next_url(my_soup)
        sleep(4)
    dft = dft.append(pd.DataFrame(listings), ignore_index=True)
    return dft


def create_soup(url):
    """
    Get the HTML contents of the URL. It the URL doesn't exist, return None
    :param url: string, the url to scrape
    :return: soup: a BeautifulSoup object
    """
    try:
        page = requests.get(url)
        if page.status_code == 404:
            return None
        return BeautifulSoup(page.text, "html.parser")
    except:
        return None


def check_flag(soup):
    """
    Check the span tags np classes to check for the next page label
    :param soup: Beautiful soup object to check
    :return: flag, a Boolean indicating the presence of the next page
    """
    all_np_tags = soup.find_all(name="span", attrs={"class": "np"})
    return any(["Next" in tag.text for tag in all_np_tags])


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
    spec_link = get_url_link(div)
    # If link is a duplicate on the current run, then don't add it
    if spec_link in set(lst_dict["url"]):
        return lst_dict

    # Add the job spec details
    lst_dict["job_title"] += [get_job_title(div)]
    lst_dict["location"] += [get_location(div)]
    lst_dict["company"] += [get_company_name(div)]
    lst_dict["jobsite"] += ["Indeed"]
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
    if soup is not None:
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
    return "N/A"


def create_df_new():
    """
    If it doesn't exist, create the initial indeed_data file
    :return: None
    """
    df_new = pd.DataFrame(columns=["job_title", "location", "company",
                                   "url", "jobsite", "job_description"])
    return df_new


def write_file_to_s3(df_write):
    """
    Save the updated dataframe to a file on the project's AWS S3 bucket.
    :param df_write: DataFrame to write to file
    :return: None
    """
    csv_buffer = StringIO()
    df_write.drop_duplicates(["url"], inplace=True)  # Remove any duplicate postings
    df_write.to_csv(csv_buffer, index=False)
    s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    s3.Object("job-hunter-plus-data", "indeed_data_dsa.csv").put(Body=csv_buffer.getvalue())


def access_s3_to_df():
    """
    Access the project's S3 bucket and load the file into a dataframe for appending.
    :return: df: a pandas dataframe containing the data.
    """

    s3 = boto3.client("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    try:
        obj = s3.get_object(Bucket="job-hunter-plus-data", Key="indeed_data_dsa.csv")
        return pd.read_csv(BytesIO(obj["Body"].read()))
    except:
        return create_df_new()


if __name__ == "__main__":
    """
    Code that runs if called from the command line
    Call: python indeed_scraper.py "<city>" "<query>"
    Or to run all cities and queries: indeed_scraper.py
    Look for jobs within a 15 mile radius of the location, show 50 results per page.
    """
    df = access_s3_to_df()
    # Run a single city / query combination
    if len(argv) > 1:
        first_url = ''.join(["https://www.indeed.com/jobs?q=", argv[2], "&l=",
                             argv[1], "&radius=15&sort=date&limit=50"])
        df = run_scraper(first_url, df)
        write_file_to_s3(df)
    # Run 4 selected cities and 3 relevant queries
    else:
        cities = ["Austin", "Chicago", "San+Francisco", "New+York"]
        jobs = ["Data+Scientist", "Data+Analyst", "Business+Intelligence"]
        for city in cities:
            for job in jobs:
                first_url = ''.join(["https://www.indeed.com/jobs?q=", job, "&l=",
                                     city, "&radius=15&sort=date&limit=50"])
                df = run_scraper(first_url, df)
                write_file_to_s3(df)
