"""

The aim of this script is to request real time payment api 
to get payment informations and then store them into kafka 
confluent cluster.

To use this script, you have to copy your kafka confluent 
parameters in a python.config file.

"""


###---------------------------------------------------------
### Import useful libraries
###---------------------------------------------------------

from confluent_kafka import Producer
import json
import ccloud_lib # Library not installed with pip but imported from ccloud_lib.py
import numpy as np
import time
import requests
import pandas as pd


###---------------------------------------------------------
### Make initialisatons steps to retrieve and store data
###---------------------------------------------------------

# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "real_time_payments" 

# Create Producer instance
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
producer = Producer(producer_conf)

# Create topic if it doesn't already exist
ccloud_lib.create_topic(CONF, TOPIC)

# Paramaters to request API
url = "https://real-time-payments-api.herokuapp.com/current-transactions"
headers = {
    'accept': 'application/json'
}


###---------------------------------------------------------
### Code to request the API (every 15sec) and store data in 
### kafta confluent
###---------------------------------------------------------

try:

    # Starts an infinite while loop that requests the API and store data
    while True:

        # Request the API
        response = requests.get(url, headers=headers)
        data_json = json.loads(response.json())["data"][0]

        record_key = "Payment"

        # Prepare data to be stored as json
        my_json_string = json.dumps({'cc_num': data_json[0], 'merchant': data_json[1], 'category': data_json[2], 'amt': data_json[3], 'first': data_json[4], 'last': data_json[5], 'gender': data_json[6], 'street': data_json[7], 'city': data_json[8], 'state': data_json[9], 'zip': data_json[10], 'lat': data_json[11], 'long': data_json[12], 'city_pop': data_json[13], 'job': data_json[14], 'dob': data_json[15], 'trans_num': data_json[16], 'merch_lat': data_json[17], 'merch_long': data_json[18], 'is_fraud': data_json[19], 'current_time': data_json[20]})

        print(f"Producing record for transaction n°{data_json[16]}.")

        # Store data
        producer.produce(
            TOPIC,
            key=record_key,
            value=my_json_string,
        )

        time.sleep(15)

 # Interrupt infinite loop when hitting CTRL+C
except KeyboardInterrupt:
    pass
finally:
    producer.flush() # Finish producing the latest event before stopping the whole script
