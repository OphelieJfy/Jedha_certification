# Block 5 - Deployment
# Project: GetAround analysis


This project is the project submitted for the validation of block 5 of my Designer Developer certification in data science following my training at Jedha

## Deliverables

Personal video presentation : 

In complement of this video and the code provided here, you'll find :
- A web dashboard for delay analysis and simulation, as well as for daily rental price estimation : https://ojo-getaround-streamlit-188f61c1d4a6.herokuapp.com/
- A web API for car daily rental price prediction : https://ojo-getaround-api-fa638883c2ea.herokuapp.com/docs
- A web app hosting the MLFlow tracking server : https://ojo-getaround-mlflow-7508b1c17441.herokuapp.com/

## Goal of the project and repository architecture

The goal of this project is to develop and deploy several online apps for: data analysis, machine learning training, and predictions for GetAround.

For this project, you'll find several repository:
- a data repository containing the two datasets used in this project,
- an EDA repository with two notebooks containing the explorayory data analysis for each of the two datasets,
- a ML repository containing the MLFlow tracking server configuration and the machine learning training notebook,
- an API repository with all the scripts required for the deployment of the prediction API,
- a dashboard repository with all the scripts required for the deployment of a complete Streamli web dashboard.

## Usage

The source code is written in Python 3.

If you want to deploy some of the apps provided here you will need to install and create accounts for:
- Docker (https://docs.docker.com/get-docker/),
- and Heroku (https://signup.heroku.com/login and https://devcenter.heroku.com/articles/heroku-cli)

