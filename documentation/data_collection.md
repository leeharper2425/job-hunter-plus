# Data Collection

This document outlines the methodology of the data collection process for this project. It includes instructions
for the use of the web scraper, information about the data schema that is used and a description of the data collection
methodology.

## 1: Using the web scraper

The source code for the web scraper class is located in the src folder. In order to run it, you must have an Amazon Web
Services (AWS) S3 bucket set up to receive the results of the scrape in .csv format. You will need to set the
AWS_ACCESS_KEY_ID and the AWS_SECRET_ACCESS_KEY in your bash profile, so that the scraper can easily access them.  In
addition, you will need the following packages in Python 3 to be installed:
- Requests
- BeautifulSoup (BS4)
- Pandas
- Boto3

The calls for running the web scraper script from its root directory using the command line are below

### Option 1: Scraping on a single query and city
`python web_scraper.py s3_bucket filename query city`
For example: `python web_scraper.py bucket_1 file.csv data+science austin`

### Option 2: Performing a complete scrape (see below):
`python web_scraper.py <s3_bucket> <filename>`
For example: `python web_scraper.py bucket_1 file.csv`

### Option 3: Getting all jobs that were added on the current day
`python web_scraper.py <s3_bucket> <filename> daily`
For example: `python web_scraper.py bucket_1 file.csv daily`

## 2: Data Dictionary

During the scraping process, the following fields are obtained. Note that the fields are exactly as they appear in the
indeed HTML or on the advertiser's website, with no standardization performed besides removing duplicate entries based on URL.

- company: String, the name of the company that posted the job.
- job_description: String, all of the raw text that is present on the website that the job posting links to, with any HTML tags,
javascript code and CSS removed.
- job_title: String, the name of the job that has been posted.
- jobsite: String, the name of the website from which the job was scraped.
- location: String, the location of the job. The job always has a city attached, and may additionally have a state and/or zip code.
- search_term: String, the query parameter that was used for a particular instance of the scraper.
- url: String, the path part of the URL that links to the job description page.

For additional clarity, the image below shows which part of the indeed search page each of these fields (apart from the
job_description) come from.

## 3: Data Collection Methodology

For this project, four well known internet job boards were considered. These were Indeed.com, Dice.com, Ziprecruiter.com and
Jobs2Careers.com. After some experimentation, it appeared that Indeed.com has the widest selection of relevant data
related jobs for the cities that this project is targeting. In addition, since Indeed.com is an aggregator in addition to
hosting its own postings, many of the jobs that appeared on the other boards were also present there. Thus, the decision was
made to only consider Indeed.com.

The next parameter to tune was the job search query that was being made to Indeed.com. The goal here was to find a set of queries
that gave high numbers of relevant results. For example, should one search for data+science (more results in general), or for
data+scientist (more relevant results). After manual investigation, the following queries were used, with a focus on relevancy
rather than corpus volume:
- data+scientist
- data+analyst
- business+intelligence
