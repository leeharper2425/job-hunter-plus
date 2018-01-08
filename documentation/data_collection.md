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

It is worth noting here that, for a given PHP query string, Indeed.com will return at most 1000 job listings. Thus, for searches
that yield considerably more than 1000 results, one is better off optimizing for the quality of results rather than their quantity.

### Query Parameters

Given this finding, the next parameter to tune was the job search query that was being made to Indeed.com. The goal here was to
find a set of queries that gave a relatively high number of relevant results, subject to the 1000 result restriction. For example,
should one search for data+science (more results in general), or for data+scientist (more relevant results). After manual
investigation, the following queries were used, with a focus on relevancy rather than corpus volume:
- data+scientist
- data+analyst
- business+intelligence

Some other miscellaneous parameters were also optimized by manual inspection:
- Results were limited to a 15 mile radius of the target city.
- The maximum number of results (50) was displayed on each results page. This minimizes the number of URL requests that are made to
Indeed.com's servers, and minimizes the number of sponsored listings (which often repeat themselves).

### Data Collection Protocol

An initial csv file was generated on December 29-30 2017. In order to get more job listings than the 1000 result limit would normally
allow for, the scrape was performed in two ways:
1. Sort by relevancy (this is the Indeed default, so the sort parameter was skipped in the query)
2. Sort by date posted

This generated approximately 9000 job listings across the three target search terms and four target cities. All scraping was done using
and AWS EC2 micro instance, and the results were stored in the job-hunter-plus-data S3 bucket

Ongoing data collection was performed on a daily basis, with a unix cron job being launched at 9.30pm CST froman EC2 instance. This job
sorts the results by date, and then only scrapes the jobs that were posted on the day of the current job, identified by the "Today" or
"Just posted" text in the date posted div of the job listing.
