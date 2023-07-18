
# Cybersecurity News Website

This repository contains the code for a cybersecurity news website. The website aggregates articles from various cybersecurity news sources, assigns scores based on the source's credibility, freshness, and engagement, and displays the articles in order of their overall score. The website also uses a machine learning model to predict the source of an article based on its summary.

## Code Overview

### Flask Application (Backend)

The Flask application provides the backend for the website. It sets up the routes for the website, retrieves articles from different sources, calculates various scores for each article, and sorts the articles by the overall score. It also provides a route to clear the cache.

### Feed Parser (Data Collection)

The script parses RSS feeds from various cybersecurity news sources, assigns scores based on the source's credibility, freshness, and engagement, and stores the articles in a MongoDB database.

### Data Cleaner (Data Preprocessing)

The script reads the articles from the database, removes duplicates, cleans the text of the articles, and stores the cleaned articles back in the database.

### Model Trainer (Machine Learning)

The script preprocesses the data, trains a Logistic Regression model with hyperparameter tuning and class balancing to predict the source of an article based on its summary, validates the model, and saves the model and necessary transformers for later use.

## Setup Instructions

The `setup.py` file is used to automate the installation of the necessary packages and dependencies to run the cybersecurity news aggregator. 

Here's how you can use it:

1. Download or clone the repository to your local machine.

2. Open a terminal window and navigate to the directory where the `setup.py` file is located.

3. Run the following command:
   
   ```python
   pip install .
   ```

1. Clone the repository.
2. Install the necessary dependencies.
3. Set up a MongoDB database.
4. Run the feed parser to collect data.
5. Run the data cleaner to preprocess the data.
6. Run the model trainer to train and validate the machine learning model.
7. Run the Flask application to start the website.
8. You can automate this process by running "python news" in the command line
