""" 

The function of this script is to provide an API (deployed 
using a docker environment) that can be queried directly or 
by using the website set up at the front-end.

This API is used to predict the open or closed status of the
user's eyes on the photo he has downloaded or taken directly
with his camera (from the website).

"""


###---------------------------------------------------------
### Import useful libraries
###---------------------------------------------------------

import mlflow 
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import numpy as np
import tensorflow as tf
import cv2
import dlib
from imutils import face_utils
from mlxtend.image import extract_face_landmarks


###---------------------------------------------------------
### Initialize your FastaPI
###---------------------------------------------------------

description = """ 
  Welcome to the Wake Up API demo! \n
  This app allows you to upload your picture to make a prediction! Try it out 🕹️\n

  ## Machine Learning Endpoints

  This is a Machine Learning endpoint that predicts wether your eyes are opened or closed. Here is the endpoint:

  * `/predict` that accepts a picture (jpeg, jpg or png) 

  Check out documentation below 👇 for more information on each endpoint. 
 """

tags_metadata = [
    {
        "name": "Machine Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title="WakeUp",
    description=description,
    version="0.1",
    openapi_tags=tags_metadata
)


###---------------------------------------------------------
### Define functions
###---------------------------------------------------------

# Function to detect eyes in a picture
def eyes_recognition(image):

  # Prepare image for eyes detection
  color = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
  gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)

  # Extract landmarks coordinates
  landmarks = extract_face_landmarks(gray)

  # Calculate a margin around the eye
  extractmarge = int(len(gray)*0.05)

  # Left eye maximal coordinates
  lx1 = landmarks[36][0]
  lx2 = landmarks[39][0]
  ly1 = landmarks[37][1]
  ly2 = landmarks[40][1]
  lefteye = color[ly1 - extractmarge : ly2 + extractmarge, lx1 - extractmarge : lx2 + extractmarge]

  # Right eye maximal coordinates
  rx1 = landmarks[42][0]
  rx2 = landmarks[45][0]
  ry1 = landmarks[43][1]
  ry2 = landmarks[46][1]
  righteye = color[ry1 - extractmarge : ry2 + extractmarge, rx1 - extractmarge : rx2 + extractmarge]

  bonus = int(extractmarge/2)
  # Draw rectangles on color
  cv2.rectangle(color, (lx1-bonus,ly1-bonus), (lx2+bonus,ly2+bonus), (255,0,0), 2)
  cv2.rectangle(color, (rx1-bonus,ry1-bonus), (rx2+bonus,ry2+bonus), (255,0,0), 2)
  
  # Return eyes images
  return lefteye, righteye, color

# Function to preprocess eye informations extract with eye_detection function before launching the prediction
def eye_preprocess(eye):

  # Resize your image to fit model entry
  resize = tf.image.resize(
    eye,
    size = (52, 52),
    method = tf.image.ResizeMethod.BILINEAR
  )

  # Switch to grayscale
  grayscale = tf.image.rgb_to_grayscale(
      resize
  )

  # Normalize your data
  norm = grayscale / 255

  # Add one dimension to fit model entry
  final = tf.expand_dims(
      norm, axis = 0
  )

  # Return the final image to make your prediction
  return final

# Function to predict if eyes are opened, closed, or wink
def prediction(lefteye, righteye, model):

  class_labels = ["close", "open"]

  # Predict and return predictions
  # For lefteye
  preds_left = model.predict(lefteye)
  pred_left = np.argmax(preds_left, axis = 1)
  # For righteye
  preds_right = model.predict(righteye)
  pred_right = np.argmax(preds_right, axis = 1)

  if pred_left == pred_right:
    state = class_labels[pred_left[0]]
  else:
    state = "wink"

  return state

###---------------------------------------------------------
### Configure your FastAPI page
###---------------------------------------------------------

@app.get("/", tags=["Introduction Endpoints"])
async def index():
  
    """
    Simply returns a welcome message!
    """
    
    message = "Hello world! This `/` is the most simple and default endpoint of our WakeUp API. If you want to learn more, check out documentation of the api at `/docs`"
    return message

@app.post("/predict", tags=["Machine Learning"])
async def predict(file: UploadFile= File(...)):
  
    """
    In this section you can upload your picture (jpeg, jpg, png) and launch a prediction (directly or via a web app).
    """
    
    # Import image
    image = await file.read()

    try:
        
      # Launch eye recognition
      lefteye, righteye, detected_eyes = eyes_recognition(image)

      # Launch eye preprocessing on both eyes extracted with eye recognition
      lefteye = eye_preprocess(lefteye)
      righteye = eye_preprocess(righteye)

      # Import and load your model
      tf.keras.utils.get_file("/home/app/CNN_model_2_gray_import.h5",
                                        origin="https://wakeup-jedha.s3.eu-west-3.amazonaws.com/wakeup/model/CNN_model_2_gray.h5")
      modelconv = tf.keras.models.load_model("/home/app/CNN_model_2_gray_import.h5")

      # Make your prediction and return eye state
      response = prediction(lefteye, righteye, modelconv)
      detected_eyes = detected_eyes.tolist()
  
      predicted_image = {'response':response, 'image':detected_eyes}

      return predicted_image
    
    except:
        
        response = "Error"
        predicted_image = {'response':response, 'image':image}
        
        return predicted_image


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)