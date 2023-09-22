# Block 1 - Build & Manage a Data Infrastructure
# Project: Automatic Fraud Detection 

  
This project is the project submitted for the validation of block 1 of my Designer Developer certification in data science following my training at Jedha

## Deliverables

- [My personnal video presentation](https://share.vidyard.com/watch/7RryeFvWQrsySjfUPybaS1?)

- The support presentation in this repository: Slides_presentation.pptx

## Project context and objective

In a context where many purchases are made online, fraudulent credit card payments are more and more numerous. Artificial intelligence can help detect these frauds automatically and accurately.

The objective of this project, carried out as an end-of-training project for the Bootcamp Lead proposed by Jedha, is to set up an infrastructure capable, using a pre-trained machine learning model, of detecting in real time fraudulent payments and send an alert to the user. But also to store all the data automatically and accessible for further analysis.

The system is composed as followed (each part interacting with others):
- a dataset (see dataset section)
- a monitoring system to track various Machine Learning models with MLfow
    - source code in 1_MLFlow_tracking/
    - linked to PostgreSQL on Heorku and S3 Bucket on AWS
- a trained model with scikit-learn for fraudulent payment detection
    - source code in 2_ML/
- an infrastructure that ingest real-time payments
    - use the real-time payment API provided by Jedha
    - source code in 3_Real_time_data/ with:
        - Producer_real_time_data.py - requests the real time data API and stores the results in Kafka Confluent
        - Consumer_real_time_data.py - take data loaded in Kafka Confluent, load the model and preprocessing pickle from S3 and give out a prediction of a transaction
    - prediction results are stored in a csv file in 4_Airflow/data/data_logs/*
- a Airflow dag to orchestrate all the actions:
    - source code in 4_Airflow

This project was carried out as a team with two other people from the training session: Céline Tang and Samba

## Dataset

The dataset used to build the Machine Learning model is avaialble [here on Kaggle](https://www.kaggle.com/datasets/kartik2112/fraud-detection).
They can't be add on GitHub due to their size. They should be add to a 'data' folder in order to use the ML notebook.

Real-time payments have been retrieve from the real-time payment API provided by Jedha.
Examples of data saved after processing these real-time payments are available in the '4_airflow/data/data_logs' folder.

## Usage

The source code of this project in written in Python 3.
To locally run the different parts, you need Docker and Heroku to be installed.
To run Kafka, you need to create a confluent cluster account.
A requirement.txt file is included in each folder and list all the required librairies.

The models trained during this project having been saved directly on MLFlow and S3, a copy of the selected model (in pkl format) has been added to the 'ML' folder.
The same goes for the data pre-processing stage.
To use these files directly, modifications are to be expected in the 'Consumer_real_time_data.py' script which is coded to retrieve them directly from the associated S3.

The MLFlow server as well as the Postgresql database have been deployed on Heroku.
The MLFlow server was directly linked to the S3 bucket in order to save the generated models there.

Airflow was deployed locally and linked to both the S3 bucket and the Postgresql database available on Heroku.
