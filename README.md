# Helping new data scientists narrow their job search

## Objectives
In this project, I intend to use the job postings from multiple online job search
websites to do the following:
- Identify the skills and/or technologies that can be used to differentiate between
different job markets.
- Use those findings to build a model that predicts the locations where a data
scientist with specific expertise might most easily find work.
- Combine these findings and the model into a usable web application.

## Background and motivation
Data science is seen by many independent bodies as one of the most rapidly growing
"hot" jobs of the 21$^{st}$ century. Despite the need, there is still a dearth of
professionals with the requisite skill sets to fill all the growing need. In
response to this, many Universities and for-profit education institutions are
offering courses in topics such as "data science" and "data analytics".

However, there is a lack of consensus as to what "data science" really means - and
job postings vary tremendously in the skills that they emphasize. In addition,
many companies offer relocation packages for these roles, meaning that new, skilled
graduates have tremendous choice in the job market. Such choice can be overwhelming,
and this project seeks to help alleviate some of this burden, by helping to narrow
a graduate's job search.

While there is little in the academic literature on key data science job skills,
building a web scraper for America's most popular job search engine, indeed.com, to
perform exploratory data analysis on this topic is a common project for aspiring
data scientists. Several such projects have uncovered some evidence for geographic
differences in desired skill sets. Other common projects include trying to scrape
salary data for use in regression analysis, or scraping jobs for simple keyword
matching to help in a user's job search.

This project is differentiated from these prior projects in two ways. Firstly,
job data will be aggregated from multiple sites. Initially:
- Indeed.com
- Jobs2Careers.com
- Dice.com
- ZipRecruiter.com (if time allows)

Secondly, the data collected will be used to build an unsupervised predictive model
based on the text from the job descriptions.

## Specific Challenges
There are several potential hurdles to the success of this project:
- Having a web scraper's IP address get blocked from one of the websites. To mitigate this,
the web scrapers will run on Amazon Web Services (AWS) ec2 instances, so that should one
get blocked, another can be spun up.
- Detecting a small "signal" on a large background. It is likely that many jobs are of a
"cookie cutter" nature, and might well have the same skills listed (such as Python or R)
regardless of geography. To mitigate this, as many job descriptions as possible should
be collected. Extremely common terms (which are probably also highly correlated) can be
de-emphasized using techniques like Term Frequency - Inverse Document Frequency (TF-IDF), and
by certain dimensionality reduction techniques, such as principal components analysis.

## Data Requirements and Analysis
In order to keep this problem tractable within 2 and a half weeks, data collection
will be limited to three common data science geographies - Austin, New York and San
Francisco. The search radius will be 50 miles. In order to ensure a large corpus,
the search term "data" will be used, and irrelevant job titles will be removed.

The raw information that will be needed in order to explore the differences between
data science job markets is the text of job descriptions. These will be obtained
by running web scrapers using several (AWS) ec2 instances. During this process,
javascript page elements and page formatting will be removed, so that only the
visible on-page text remains. The results of the web scraping will be stored in an
AWS S3 bucket.

It is likely that certain jobs will be posted on multiple sites, or might appear
multiple times on the same site (for example in sponsored listings). This will be
dealt with by checking for precise duplicates (to remove same-site duplication)
or checking the similarity between count vectors of each pair of documents from
different websites (without stopwords). Extremly similar documents (criteria to
be established) shall be removed.

The raw information will then be converted into a form that can be used to build
machine learning models using natural language processing (NLP) techniques. To
emphasize the differences between cities, rather than their similarities TF-IDF
vectorization or Count Vectorization on a per-geography basis will be used.

Topic modelling for each geography will be performed using non-negative matrix
factorization (NMF) or Latent Dirichlet Allocation (LDA). This will help to uncover
the differences and similarities.

The final model will be build by projecting a set of user-entered keywords onto
the identified topics.

There are two MOEs/MOPs for this project, based around two outcomes:
- Is there a difference in skills/technologies between geographies?
- Are new data scientists happy with the recommendations given to them?

Due to the qualitative nature of the model output it is difficult to quantify a
the second of these. One could consider that a good model would be one where 90%
of surveyed individual stakeholders felt that the returned skill or technology
"topics" were well-aligned with their skill set. However, getting a large enough
sample size to accurately validate this will be difficult.

The first MOE can be assessed through cross-validation. In this process, I will
tune model parameters (such as the number of retained topics, and the stop word
list that is used in the tokenization process) and try and predict
the geography that specific job descriptions relate to. A good model of this
nature would be have sensitivity and specificity of at least 80% of the time.
If the MOEs were less than around 50% for the three geographies, this would
indicate the model had little predictive power over a random guess, and that
there is generally little detectable difference between the job markets. I expect
that, as a minimum, this determination will possible within the 2.5 week timeframe.

I should be able to build a good model with a few thousand examples of job descriptions
from each location. I anticipate being able to scrape of the order of 50,000 job
descriptions from the internet using the "data" search in the three locations
being considered. Once filtering out irrelevant posting, I still anticipate having
more than enough to meet these criteria.

A proof of concept scraped data csv can be found in the data folder in this
repository.
