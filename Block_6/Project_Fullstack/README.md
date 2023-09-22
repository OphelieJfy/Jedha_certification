# Block 6 - Lead a Data Project
# Project: Wake Up!


This project is the project submitted for the validation of block 6 of my Designer Developer certification in data science following my training at Jedha

## Deliverables

- DemoDay video presentation : https://www.youtube.com/watch?v=5qngzP4DGGU&t=2867s (from minute 48)

- My personal [video](https://share.vidyard.com/watch/VuVxhTMgpmh6wa3aZeG31K?) presentation

- the Powerpoint presentation in this repository : Slides_presentation.pptx

## Project context and objective

This project was carried out in the context of the final Bootcamp Fullstack project proposed by Jedha, in a team with the following people: Olivier Tardella, Yann Van Isacker and Thibaut Gallice.

The objective was to carry out a Machine Learning project ranging from the choice of theme and data, to the deployment of a solution, through the implementation of a high-performance model (with monitoring of the models by tracking on MLFlow), an API as well as a Streamlit website.

The project chosen here has security as its theme. Indeed the final objective of this project would be to develop an on-board tool for detecting drowsiness at the wheel, both in cars, trucks, construction or agricultural machinery...
This project, to be completed in just 10 days being ambitious, we chose to first develop an intermediate solution capable of detecting whether a user's eyes are open or closed, and triggering an alarm, if their eyes remain closed for too long (in the case of a video test).

## Dataset

The dataset used to train the Machine Learning model is available  [here on Kaggle](https://www.kaggle.com/datasets/dheerajperumandla/drowsiness-dataset). Only Eyes pictures have been used in this project.

## Usage

The source code is written in Python 3.
To locally run the app and API, you need Docker and Heroku to be installed.

Data were stored in a 'data' folder.
Model's training was performed on Google Collab (GPU usage). 

The MLFlow server was deployed online through the use of Heroku services.

The API and the website are deployed independently using Docker environments.

Facial landmarks dat file used for predictions can be upload [here](https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat) and shoud be available in folders '2_API_to_request' and '3_Streamlit_app'.
