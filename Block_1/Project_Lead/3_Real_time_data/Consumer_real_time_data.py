"""

The aim of this script is to take data stored in kafta 
confluent, normalize them, make a prefiction (either it's a
fraud or not) and save datas in a local csv file every 5min.

To use this script, you have to copy your kafka confluent 
parameters in a python.config file.

"""


###---------------------------------------------------------
### Import useful libraries
###---------------------------------------------------------

from confluent_kafka import Consumer
import json
import ccloud_lib
import time
import pandas as pd
import numpy as np
from datetime import datetime
import mlflow
import pickle
import boto3


###---------------------------------------------------------
### Initialize custom functions
###---------------------------------------------------------

# Calculate distance between merchant and client
def haversine(lon_1, lon_2, lat_1, lat_2):
    
    lon_1, lon_2, lat_1, lat_2 = map(np.radians, [lon_1, lon_2, lat_1, lat_2])  # Convert degrees to Radians
    
    diff_lon = lon_2 - lon_1
    diff_lat = lat_2 - lat_1

    distance_km = 2*6371*np.arcsin(np.sqrt(np.sin(diff_lat/2.0)**2 + np.cos(lat_1) * np.cos(lat_2) * np.sin(diff_lon/2.0)**2)) # earth radius: 6371km
    
    return distance_km



###---------------------------------------------------------
### Load pre-trained model and preprocessor
###---------------------------------------------------------

model = mlflow.sklearn.load_model(model_uri = "s3://lead-project-bucket-ojo/1/b47377ffb02d4222b724731f36ed36cd/artifacts/model")

s3 = boto3.resource('s3')
preprocessor = pickle.loads(s3.Bucket("lead-project-bucket-ojo").Object("preprocessor.pkl").get()['Body'].read())


###---------------------------------------------------------
### Make initialisatons steps to retrieve data from kafka
###---------------------------------------------------------

# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "real_time_payments" 

# Create Consumer instance
# 'auto.offset.reset=earliest' to start reading from the beginning of the
# topic if no committed offsets exist
consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
consumer_conf['group.id'] = 'real_time_payment_consumer'
consumer_conf['auto.offset.reset'] = 'earliest' # This means that you will consume latest messages that your script haven't consumed yet!
consumer = Consumer(consumer_conf)

# Subscribe to topic
consumer.subscribe([TOPIC])


###---------------------------------------------------------
### Section to read data from kafka, prepare them and make 
### prediction, and finally save raw data and prediction in
### a csv local file.
###---------------------------------------------------------

i = 0

# Process messages and prediction
try:
    while True:

        msg = consumer.poll(5.0)

        if msg is None:
            print("Waiting for message or event/error in poll()")
            continue

        elif msg.error():
            print('error: {}'.format(msg.error()))

        else:
            record_key = msg.key()
            record_value = msg.value()
            data_json = json.loads(record_value)
            
            # Prepare data for prediction

            timestamp = datetime.fromtimestamp(int(str(data_json['current_time'])[:-3]))
            date = pd.to_datetime(timestamp)

            age = pd.to_datetime(data_json['dob'])
            today = datetime.now()

            data_for_pred = pd.DataFrame({"merchant": [data_json['merchant']], 
                                "category": [data_json['category']], 
                                "amt": [data_json['amt']], 
                                "gender": [data_json['gender']], 
                                "lat": [data_json['lat']], 
                                "long": [data_json['long']], 
                                "city_pop": [data_json['city_pop']], 
                                "unix_time": [int(str(data_json['current_time'])[:-3])], 
                                "merch_lat": [data_json['merch_lat']], 
                                "merch_long": [data_json['merch_long']], 
                                "day": [date.day], 
                                "month": [date.month], 
                                "year": [date.year], 
                                "weekday": [date.weekday()], 
                                "age": [int((today - age) / pd.Timedelta(days=365.25))], 
                                "transaction_distance": [haversine(data_json['long'], data_json['merch_long'], data_json['lat'], data_json['merch_lat'])]})
            data_for_pred['gender'] = data_for_pred['gender'].apply(lambda x: 1 if x =='F' else 0)
            print("Data are ready for prediction")

            # Prediction

            data_for_pred_norm = preprocessor.transform(data_for_pred)
            pred = model.predict(data_for_pred_norm)

            # Save data locally in a csv every 1 minutes (5 calls to the API)

            df = pd.json_normalize(data_json)
            df.loc[:, ["trans_date_trans_time"]] = [date]
            df.loc[:, ["unix_time"]] = [[int(str(data_json['current_time'])[:-3])]]
            df.loc[:, ["prediction"]] = [pred]
            df.drop(columns = ["current_time"])

            if i == 0:
                now = time.time()
                df.to_csv(f"../4_Airflow/data/data_logs/Real_time_payments_{now}.csv", index = False)
                i += 1
        
            elif i == 4:
                df.to_csv(f"../4_Airflow/data/data_logs/Real_time_payments_{now}.csv", mode = "a", index = False, header = False)
                i = 0
                print(f"Local csv Real_time_payments_{now}.csv finalized")

            else: 
                df.to_csv(f"../4_Airflow/data/data_logs/Real_time_payments_{now}.csv", mode = "a", index = False, header = False)
                i += 1
            
            time.sleep(5.0)

except KeyboardInterrupt:
    pass
finally:
    # Leave group and commit final offsets
    consumer.close()

