#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import ast
import time
from datetime import date, timedelta
import requests
from Model.scripts.rnn_model import RNN_Model
from google.cloud import storage
  
# if the rebuild has actually worked you should see this comment in the cat output

import os


def get_clearout_prices(start, end):
    AIMLAC_CC_MACHINE = "34.72.51.59"
    if AIMLAC_CC_MACHINE is not None:
        pass
    else:
        print("error")
    host = f"http://{AIMLAC_CC_MACHINE}"
    start_date = start
    end_date = end
    g = requests.get(url=host + f"/auction/market/clearout-prices",
                    params=dict(start_date=start_date.isoformat(),
                                end_date=end_date.isoformat()))
    print("Calling AIMLAC URL:" + str(g.url))
    assert len(g.json()) > 0   
    if g.status_code != 200:
        print("error")  
    prices = g.json()
    return prices


# In[ ]:


d0 = date(2021, 4, 21)
d1 = date.today()
delta = d1 - d0
start_date = date.today() - timedelta(days=delta.days)
end_date = date.today() + timedelta(days=0)
data = get_clearout_prices(start_date, end_date)


# In[ ]:


data = str(data)


# In[ ]:


contents = data
dictionary = ast.literal_eval(contents)
df_raw = pd.DataFrame.from_dict(dictionary)

df_raw['price'] = df_raw['price'] * 4

print(df_raw.head(5))
print(df_raw.tail(5))
print(df_raw.dtypes)
print(df_raw.shape)


# In[ ]:




# In[ ]:


model = RNN_Model(df_raw, time_lag=12)


# In[ ]:


model(save=True)


# In[ ]:


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket("convergence-public")
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        ))


# In[ ]:


#from google_auth_oauthlib import flow

# TODO: Uncomment the line below to set the `launch_browser` variable.
# launch_browser = True
#
# The `launch_browser` boolean variable indicates if a local server is used
# as the callback URL in the auth flow. A value of `True` is recommended,
# but a local server does not work if accessing the application remotely,
# such as over SSH or from a remote Jupyter notebook.

#appflow = flow.InstalledAppFlow.from_client_secrets_file(
#    "client_secrets.json", scopes=["https://www.googleapis.com/auth/bigquery"]
#)

#if launch_browser:
#    appflow.run_local_server()
#else:
#    appflow.run_console()
#
#credentials = appflow.credentials


# In[ ]:


upload_blob('model/saved_model.pb', 'model/saved_model.pb')
upload_blob('model/keras_metadata.pb.pb', 'model/keras_metadata.pb.pb')

# In[ ]:




