import pandas as pd
import numpy as np
from datetime import datetime

from backend import API 


def fill_df(params):
    df = pd.DataFrame(columns=['timestamp'] + params['fields'])
    api = API(params)  #API object which contains weather data
    weather_data = api()
    for i, j in zip (weather_data.data, np.arange(0,len(weather_data.data))):
        for col in df.columns:
            df.loc[j, col] = (i[col][0])
    df.loc[:,'location'] = str(params['location'])
    df = df.set_index(['timestamp', 'location'])
    return df

def df_to_sql(df):
    pass
    