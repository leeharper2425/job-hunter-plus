"""
Web scraper class for the indeed.com website
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
from collections import defaultdict
from time import sleep
import os
import boto3
from io import StringIO, BytesIO


class IndeedScraper:
    """
    A class that deploys an indeed web scraper, saving results in an S3 bucket.
    """
    def __init__(self, bucket, filename, query, location, daily=False):
        """
        Function that is called when the class is instantiated.
        An object is created for each search query and city separately.
        :param query: str, the job search term.
        :param location: str, the city to be searched.
        :param bucket: str, AWS S3 bucket where data is stored.
        :param filename: str, filename of data.
        :param daily: bool, indicates full scrape or daily update.
        """
        self.url = ''.join(["https://www.indeed.com/jobs?q=", query, "&l=",
                            location, "&radius=15&sort=date&limit=50"])
        self.query = query
        self.city = location
        self.filename = filename
        self.s3_bucket = bucket
        self.df = self._access_s3_to_df()
        self.flag = True
        self.listings = defaultdict(list)
        self.soup = None
        self.daily = daily

    def run_scraper(self):
        """
        Method that controls the core functionality of the scraper.
        """
        # Run the scraper until it runs out of pages to scrape
        while self.flag:
            self.soup = self._create_soup(self.url)
            self._check_flag()
            for div in self.soup.find_all(name="div", attrs={"class": "row"}):
                self._add_listing_info(div)
                if not self.flag:   # Stop if daily update is finished.
                    break
                sleep(2)
            # Save the file after each results page
            self.df = self.df.append(pd.DataFrame(self.listings), ignore_index=True)
            self.listings = defaultdict(list)
            self._write_file_to_s3()
            self._get_next_url()
            sleep(2)

    @staticmethod
    def _create_soup(url):
        """
        Get the HTML contents of the URL.
        If the URL does not exist, or an errors is thrown, then self.soup is
        assigned None.
        :param: url: str, the url to get the HTML from
        :return soup: a BS4 object of the webpage's HTML
        """
        try:
            page = requests.get(url)
            if page.status_code == 404:
                return None
            return BeautifulSoup(page.text, "html.parser")
        except:
            return None

    def _check_flag(self):
        """
        Check the span tags np classes to check for the next page label.
        If there is a next page, set self.flag = True, and if there is
        not, set self.flag = False.
        """
        all_np_tags = self.soup.find_all(name="span", attrs={"class": "np"})
        self.flag = any(["Next" in tag.text for tag in all_np_tags])

    def _get_next_url(self):
        """
        Update the object with the URL of the next listings page.
        """
        d = self.soup.find(name="div", attrs={"class": "pagination"})
        if d is None:  # This occurs if there is only one page of results
            return
        self.url = ''.join(["https://www.indeed.com", d.find_all("a")[-1]["href"]])

    def _add_listing_info(self, div):
        """
        Get the results of scraping a single job listing.
        :param div: BS4 div object containing the job listing
        """
        job_url = self._get_url_link(div)
        # If link is a duplicate on the current run, then don't add it
        if job_url in set(self.listings["url"]):
            return

        # Extra code checks for the daily updates:
        if self.daily:
            # We don't want sponsored links on the daily job
            if "pagead" in job_url:
                return
            # If job wasn't posted today, then skip it and stop scraping
            if not self._get_today(div):
                self.flag = False
                return

        # Add the job spec details
        self._get_job_title(div)
        self._get_location(div)
        self._get_company_name(div)
        self._get_job_description(job_url)
        self.listings["jobsite"] += ["Indeed"]
        self.listings["url"] += [job_url]
        self.listings["search_term"] += [self.query]
        self.listings["city_term"] += [self.city]

    @staticmethod
    def _get_url_link(div):
        """
        Extract the URL link from the div tag.
        :param div: tag object, the div tag from a job posting
        :return job_url: str, the URL of the job posting
        """
        a = div.find(name="a", attrs={"data-tn-element": "jobTitle"})
        return a["href"]

    @staticmethod
    def _get_today(div):
        """
        Get the day that the job was posted, and return True if today
        :param div: A single job posting
        :return flag: a Boolean indicating whether the job was posted
                      "Today" or "Just posted"
        """
        date_tag = div.find(name="span", attrs={"class": "date"})
        if date_tag.text == "Today" or date_tag.text == "Just posted":
            return True
        return False

    def get_number_of_jobs(self):
        """
        Get the number of jobs returned for the search criteria.
        Currently unused when called from run from command line.
        :return num_jobs: int, the number of jobs that the search returns.
        """
        tag = self.soup.find("div", {"id": "searchCount"})
        n_jobs = tag.text.split(" ")[-2]
        return int(n_jobs.replace(",", ""))

    def _get_job_title(self, div):
        """
        Extract the job titles from the div tag.
        :param div: tag object, the div tag from a job posting
        """
        a = div.find(name="a", attrs={"data-tn-element": "jobTitle"})
        self.listings["job_title"] += [a["title"].replace(",", "")]

    def _get_company_name(self, div):
        """
        Extract company names from the div tag.
        If no company name attached, return "N/A"
        Note company name can appear in one of a couple of different places.
        :param div: tag object, the div tag from a job posting
        """
        company = div.find(name="span", attrs={"class": "company"})
        if company is None:
            self.listings["company"] += ["N/A"]
            return
        a = div.find(name="a", attrs={"data-tn-element": "companyName"})
        if not a:
            self.listings["company"] += [' '.join(company.text.split()).replace(",", "")]
        else:
            self.listings["company"] += [' '.join(a.text.split()).replace(",", "")]

    def _get_location(self, div):
        """
        Extract the location of the job posting from the div tag.
        :param div: tag object, the div tag from a job posting
        """
        location = div.find(name="span", attrs={"class": "location"})
        self.listings["location"] += [location.text.replace(",", "")]

    def _get_job_description(self, link):
        """
        Get the raw text of the job description from the linked webpage.
        Return "N/A" if the webpage doesn't exist.
        :param link: str, the url of the job description webpage
        """
        soup = self._create_soup(''.join(["https://www.indeed.com", link]))
        if soup is None:
            self.listings["job_description"] += ["N/A"]
            return

        # Remove all script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop any blank lines
        self.listings["job_description"] += \
            ['\n'.join(chunk for chunk in chunks if chunk)]

    def _access_s3_to_df(self):
        """
        Access the project's S3 bucket and load the file into a DataFrame.
        :return df: a DataFrame containing the S3 data
        """

        s3 = boto3.client("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                          aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
        try:
            obj = s3.get_object(Bucket=self.s3_bucket, Key=self.filename)
            return pd.read_csv(BytesIO(obj["Body"].read()))
        except:
            return self._create_df_new()

    @staticmethod
    def _create_df_new():
        """
        If the S3 bucket doesn't contain the file, create an initial DataFrame.
        """
        return pd.DataFrame(columns=["job_title", "location", "company",
                                     "url", "jobsite", "job_description",
                                     "search_term" "city_term"])

    def _write_file_to_s3(self):
        """
        Save the updated DataFrame to a file on the project's AWS S3 bucket.
        """
        csv_buffer = StringIO()
        self.df.drop_duplicates(["url"], inplace=True)  # Remove any duplicate postings
        self.df.to_csv(csv_buffer, index=False)
        s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
        s3.Object(self.s3_bucket, self.filename).put(Body=csv_buffer.getvalue())


if __name__ == "__main__":
    """
    Code that runs if called from the command line
    Option 1: To run search across all job queries and cities:
    Call: python web_scraper.py <s3_bucket> <filename>
    Option 2: To run search on a single city and query:
    Call: python web_scraper.py <s3_bucket> <filename> <query> <city>
    Option 3: To run a daily scraper update:
    Call python web_scraper.py <s3_bucket> <filename> daily
    """
    # Run a single city / query combination
    if len(argv) == 5:
        scraper = IndeedScraper(argv[1], argv[2], argv[3], argv[4])
        scraper.run_scraper()
    # Run 4 selected cities and 3 relevant queries
    cities = ["Austin", "Chicago", "San+Francisco", "New+York"]
    jobs = ["Data+Scientist", "Data+Analyst", "Business+Intelligence"]
    if len(argv) == 3 or len(argv) == 4:
        for city in cities:
            for job in jobs:
                if len(argv) == 3:
                    scraper = IndeedScraper(argv[1], argv[2], job, city)
                else:
                    scraper = IndeedScraper(argv[1], argv[2], job, city, True)
                scraper.run_scraper()
