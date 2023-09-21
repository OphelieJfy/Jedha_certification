"""
This script provide en API (deployed using a Docker 
environment) that can be queried with curl in a script or 
terminal, directly into the API or via a website.

This API is used to estimate the per day rental price of a
car, evaluated from the Getaround pricing data.
"""


###---------------------------------------------------------
### Import useful libraries
###---------------------------------------------------------

import mlflow 
import uvicorn
import pandas as pd 
import numpy as np
from pydantic import BaseModel, ConfigDict
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder


###---------------------------------------------------------
### Initialize your FastaPI
###---------------------------------------------------------

description = """
<h3> Welcome to my car rental price predictor API! </h3>

<br/> This API allows you to estimate the daily rental price of your car based on its characteristics! Try it out 🕹️\n
<br/>

<b> Price prediction endpoint </b>

This is a Machine Learning endpoint that predicts the daily rental price of your car. Here is the endpoint:
* `/predict` in which you describe your car's characteristics

<br/> Check out documentation below 👇 for more information on each endpoint. 
"""

tags_metadata = [
    {
        "name": "Price prediction",
        "description": "Use this endpoint to estimate your daily rental price."
    }
]

app = FastAPI(
    title = "💸 Fair Price - Car Rental Price Predictor",
    description = description,
    version = "0.1",
    openapi_tags = tags_metadata
)


###---------------------------------------------------------
### Configure your FastAPI page
###---------------------------------------------------------


class Car(BaseModel):
    model_key: Literal["Citroën", "Peugeot", "PGO", "Renault", "Audi", "BMW", "Mercedes", "Opel", "Volkswagen", "Ferrari", "Mitsubishi", "Nissan", "SEAT", "Subaru", "Toyota", "other"]
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: Literal["diesel", "petrol", "other"]
    paint_color: Literal["black", "grey", "white", "red", "silver", "blue", "beige", "brown", "other"]
    car_type: Literal["convertible", "coupe", "estate", "hatchback", "sedan", "subcompact", "suv", "van"]
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

# Redirect automatically to /docs
@app.get("/", include_in_schema = False)
async def docs_redirect():
    
    return RedirectResponse(url = '/docs')

@app.post("/predict", tags = ["Price prediction"])
async def predict(cars: List[Car]):

    # Load model
    mlflow.set_tracking_uri("https://ojo-getaround-mlflow-7508b1c17441.herokuapp.com/")
    logged_model = 'runs:/a461ccb3c7224b36a75afa6737b1c809/car_rental_price_predictor'
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    
    # Read input
    car_features = pd.DataFrame(jsonable_encoder(cars))
    
    # Predict, format and return response
    prediction = loaded_model.predict(car_features)
    resp = {"prediction": prediction.tolist()}
    return resp

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4004)