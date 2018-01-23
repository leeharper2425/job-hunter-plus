# NLP Processing

This document outlines the methodology that was used to process the the raw scraped data into forms
that could be used in machine learning models. This document relates to the following modules:
- dataframe_processing.py
- nlp_processing.py

## 1: nlp_processing.py

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
