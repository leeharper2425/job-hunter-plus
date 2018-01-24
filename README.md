# Using Natural Language Processing to Help New Data Scientists Narrow Their Job Search

## 1. Background and motivation
Data science is seen by many independent bodies as one of the most rapidly growing
"hot" jobs of the 21$^{st}$ century. Despite the need, there is still a dearth of
professionals with the requisite skill sets. In response to this, many Universities
and for-profit education institutions are offering courses in topics such as "data
science" and "data analytics".

However, there is a lack of consensus as to what "data science" really means - and
job postings vary tremendously in the skills that they emphasize. In addition,
many companies offer relocation packages for these roles, meaning that new, skilled
graduates have a high level of choice in the job market. Such choice can be overwhelming,
and this project seeks to help alleviate some of this burden, by helping to narrow
a graduate's job search.

While there is little in the academic literature on key data science job skills,
building a web scraper for America's most popular job search engine, Indeed.com, to
perform exploratory data analysis on this topic is a common project for aspiring
data scientists. Several such projects have uncovered some evidence for geographic
differences in desired skill sets, and this project extends this work to build
inferential machine learning models to gain further insight into this.

To limit the scope of this project, the following cities were chosen:
- San Francisco, CA
- New York, NY
- Chicago, IL
- Austin, TX

And the following job description search queries were used:
- Data Scientist
- Data Analyst
- Business Intelligence

## 2. Methodology and Technology Stack

![Technologies](/images/TechStack.PNG?raw=true "TechnologyStack")

Fig. 1: Schematic of the technology stack used in this project.

Data was collected by web scraping job descriptions from Indeed.com, using the
Beautiful Soup package. The scraper ran on an Amazon Web Services (AWS) EC2 instance,
and the results were stored in CSV format in an S3 bucket. More details about the
process and the data can be found [here](/documentation/data_collection.md).

Data processing was performed using Pandas and Numpy. There were significant data cleaning
issues, and these were resolved by creating a 2-step model building process. A vocabulary
was trained using a subset of cleaned job descriptions, and then a model fitted on the entire
corpus using this vocabulary. More information about the processing pipeline can be found
[here](/documentation/data_processing.md).

Another challenge that had to be overcome was the similarity of job descriptions. Whilst there
are detectable differences, many of the words and phrases are somewhat "cookie cutter". Thus, any
inferential model must be able to successfully zoom in on the key words and phrases that differentiate
between cities. This requirement makes decision tree based methods, for example random forests and
extreme gradient boosting, ideal candidates.

Project outputs come in two forms. Firstly, I developed a simple Flask web app to predict the
city where a job seeker might have the highest chance of success using a brief written paragraph
about themselves. In addition, I used Matplotlib and Seaborn to produce visualizations, particularly
of the results of topic modeling.

## 3. Model Results

Since the classes were not hugely unbalanced, model optimization was done using the accuracy metric. This is the
proportion of times that the model predicted the correct city from the text of the processed job description.
Scoring was performed using 5-fold cross-validation.

The results of the best model for each target city are shown below. This model used extreme gradient boosted trees
(XGBoost algorithm), with 2000 estimators, and a maximum tree depth of three. This model had an overall cross-validated
accuracy of 73.1%. By way of comparison, the optimal random forest model achieved 71.8% accuracy.

![ModelResults](/images/ModelResults.PNG?raw=true "ModelResults")

Figure 2: Cross-validated classification scores of the XGBoost model.

The confusion matrix from which these results is derived is shown below:

![ConfusionMatrix](/images/ConfusionMatrix.PNG?raw=true "ConfusionMatrix")

Figure 3: Cross-validated aggregate confusion matrix for the XGBoost model

These results show two things:
1. For every city considered, the model shows significantly more inferential power than randomly assigning a city.
2. In absolute terms, job descriptions are more likely to be misclassified as San Francisco or New York. This is a result
of a larger number of jobs being scraped for these cities.

## 4. Topic Modeling

To try and understand the underlying reasons for the good levels of discrimination between cities, topic modeling was performed.
In order to try and capture the spirit of the model, non-negative matrix factorization was used, applied to the TFIDF vectorized
matrix for each city in turn. A notebook detailing the actual vocabulary from each topic can be found here.

A visualization of the distribution of topics in each target city is shown in Fig. 5. In this visualization, each city's distribution of
topics can be viewed as lines in a "topic barcode" that represents the city. It is clear from the visualization that these barcodes are
substantially different to each other.

![CityBarcodes](/images/topic_barcodes.png "TopicBarcodes")

Figure 5: "Topic Barcodes" illustrating the differences between cities at a high level.

A more in depth comparison between New York and San Francisco is shown in Fig. 6. This visualization shows that both cities have several
topics in common, for example EEO and digital marketing. It also clearly shows that New York uniquely has a large number of appearances
of the "medical" topic - this includes words such as "physician" and "hospital". By contrast, San Francisco uniquely shows appearances
of the "SalesForce" and "Qualifications" topics.

![InDepthTopics](/images/two_city_comparison.png "TwoCityComparison")

Figure 6: Topic distributions for New York and San Francisco.
