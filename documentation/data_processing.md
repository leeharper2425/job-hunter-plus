# Data Processing

This document outlines the methodology that was used to process the the raw scraped data into forms
that could be used in machine learning models. This document relates to the following modules:
- dataframe_processing.py
- nlp_processing.py

## 1: Motivation

The data for this project consisted of the raw text scraper directly from the web page on which a
job description is located. Sometimes the job would be posted directly by an employer on the Indeed.com
website, but often the job would link to the employer's website. It is straightforward to remove any
javascript and CSS elements from the page, but this still leaves a few problems

1. Some words are combined together due to the stripping of elements
2. There is a lot of text that is not part of the job description on the web page
3. The HTML structure of the pages are not the same, so there is no standard way of removing
the irrelevant text,

An illustration of the problem is shown below. The image shows an example observation, and the red box
highlights the actual text that we want to extract - in this case less than 50% of the total text. This
issue was resolved using a 2-step process for data processing, which is described in the next section.

![alt text](https://github.com/leeharper2425/job-hunter-plus/tree/master/images/MessyData.PNG "Messy Data Example")


## 2: Standard Workflow

The following steps make up the data processing workflow.

1. Import data from the job-hunter-plus AWS S3 bucket
2. Remove unusable job descriptions (eg 403 errors, timeout errors, null values)
3. Filter out the required number of cities
4. Select the direct job postings on Indeed.com ("clean subset")
5. Select the job description text from these postings
6. Perform additional cleaning to subset (eg remove special unicode characters, split joined words)
7. Stemmatize/lemmatize the text
8. Fit vocabularly using the clean subset
9. Clean text in the entire corpus
10. Vectorize corpus using previously trained vocabulary

## 3: nlp_processing.py

This modules contains the NLPProcessing class. Within the standard data processing workflow for the model
building process, this class controls all preprocessing.

### Input Parameters

**stemlem**: string or list of strings (default "")

The stemming or lemmatizing processing to perform.

- If "". no stemming or lemmatization will occur.
- If "porter", will apply a porter stemmatizer to each document in the corpus.
- If "snowball", will apply a snowball stemmatizer to each document in the corpus.
- If "wordnet", will apply a wordnet lemmatizer to each document in the corpus.

If a list is passed, lemmatization will be applied prior to stemmatization.

**min_df**: int or float (default=1)

The minimum document frequency of any word or phrase that is to be used in the vocabulary.

**max_df**: int or float (default = 1.0)

The maxiumum document frequency of any word or phrase that is to be used in the vocabulary.

**num_cities**: int (default=2)

The number of cities to retain in the model.
- If num_cities = 2, San Francisco and New York will be retained.
- If num_cities = 3, Chicago will be added.
- If num_cities = 4, Austin will be added.

**n_grams**: tuple (default (1, 1))

A tuple containing the minimum and maximum number of n-grams to consider. The input (1, 1)
will only consider unigrams, whereas (1, 2) will consider unigrams and bigrams.

**use_stopwords**: boolean (default True)

Boolean indicating whether to remove stopwords from the corpus.

**tokenize**: str (default "tfidf")

Indicates which text tokenization method to use.
- "tfidf" - applies SKLearn's TFIDF vectorizer.
- "count" - applies SKLearn's Count vectorizer.

### Methods

**fit([data, bucket, filename])**
Fits NLP processing object to the scraped data, using a clean subset of the corpus.
Input can be a dataframe, or the name of an AWS S3 bucket and filename that you
have read access to.

**transform([data, bucket, filename])**
Applies NLP processing to the complete corpus. Input can be a dataframe, or the
name of an AWS S3 bucket and filename that you have read access to. Returns an ndarray
that can be used in machine learning models.

**fit_transform([data, bucket, filename])**
Simultaneously applies fitting and transformation to the corpus, yielding some performance
benefits.

**wordnet_lemmatizer(documents)**
Apply wordnet_lemmatizer to the ndarray of documents. Returns a list. Also performs stopword
removal if class instantiated with stopwords=True

**do_stem(documents, stemmer)**
Apply stemmitization to the ndarray of documents, using an instantiated instance of SnowballStemmer("english") or
PorterStemmer. Also perform stopword removal if class instantiated with stopwords=True

**count_vectorize(documents)**
Fit SKLearn's count vectorizer to the ndarray or list of documents.

**tfidf_vectorize(documents**)
Fit SKLearn's TFIDF vectorizer to the ndarray or list of documents.
