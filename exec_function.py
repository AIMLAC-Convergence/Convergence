import requests
from datetime import date, timedelta
import os
import numpy as np
import pandas as pd
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging

import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from flask import Flask, send_from_directory

import scipy.signal as sgnl

app = Flask(__name__, static_url_path='', static_folder='web/static', template_folder='web/templates')

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler=logging.FileHandler('auto_bidder.log', 'w+')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

update_result_state = "Update Completed OK"

#import user modules
from utils.sql_utils import *
from convergence_modules.weather_prediction.pvlib_to_sql import main as weather
from convergence_modules.energy_production.energy_production import main as energy
from convergence_modules.energy_consumption.Energy_use import main as energy_cons
from Model.scripts.make_prediction import Predictor
from google.cloud import storage
import datetime

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
        )
    )


def download_blob(remote_blob_name, local_file_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket("convergence-public")
    blob = bucket.blob(remote_blob_name)

    blob.download_to_filename(local_file_name)



def actually_produce_plots(df, title):
    fig = go.Figure([{
    'x': df.index,
    'y': df[col],
    'name': col
    }  for col in df.columns])
    fig.update_layout(title_text = title)
    if title == 'Energy' or title == 'Energy Usage':
       fig.update_yaxes(title_text='kWh')

    filename = title.replace(" ", "") + ".html"
    	
    #fig.write_html("web/static/" + title.replace(" ", "") + ".html")
    fig.write_html(filename)
    upload_blob(filename,filename)
    #fig.write_image("web/static/images/" + title.replace(" ", "") + ".png")
    return True

def produce_plots(params):
    df_energy = load_sql(params['production_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).set_index("timestamp")
    df_weather = load_sql(params['weather_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).set_index("timestamp")
    df_usage = load_sql(params['consumption_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).tail(24)
    df_energy.drop(columns=['units'], inplace = True)
    df_energy.rename(columns={'solar_energy':'solar_energy(kWh)', 'wind_energy':'wind_energy(kWh)'}, inplace = True)
    df_price = load_sql(params['market_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).set_index("timestamp")
    df_bid = load_sql(params['bid_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).set_index("timestamp")
    df_bid.to_html('df_bid.html',index=False)
    upload_blob('df_bid.html','df_bid.html')
    actually_produce_plots(df_price, "Market Price")
    actually_produce_plots(df_energy, "Energy")
    actually_produce_plots(df_weather.loc[:, ['ghi', 'dni', 'dhi']], "Solar quantities")
    actually_produce_plots(df_weather.loc[:, ['zenith', 'azimuth', 'apparent_zenith']], "Solar angles")
    actually_produce_plots(df_weather.loc[:,['wind_speed']], "Wind speed")
    actually_produce_plots(df_weather.loc[:,['temp_air']], "Temperature")
    actually_produce_plots(df_usage, "Energy Usage")

def plot_prices(market_prices):
    fig=go.Figure({
        'x' : market_prices['TimeStamps'].values,
        'y' : market_prices['MarketPrices'].values
    })
    fig.update_layout(title_text = "Market Prices")
    fig.update_xaxes(title_text='Hour of the day')
    fig.update_yaxes(title_text='Price')
    filename =  "Market_Price.html"
    fig.write_html(filename)
    upload_blob(filename,filename)
    return True

def get_clearout_prices(start, end):
    AIMLAC_CC_MACHINE = os.getenv("AIMLAC_CC_MACHINE")
    if AIMLAC_CC_MACHINE is not None:
        pass
    else:
        logger.error(f"{AIMLAC_CC_MACHINE} is invalid")
    host = f"http://{AIMLAC_CC_MACHINE}"
    start_date = start
    end_date = end
    g = requests.get(url=host + f"/auction/market/clearout-prices",
                    params=dict(start_date=start_date.isoformat(),
                                end_date=end_date.isoformat()))
    print("Calling AIMLAC URL:" + str(g.url))
    assert len(g.json()) > 0   
    if g.status_code != 200:
        logger.error(f"Status code {g.status_code}, request failed")      
    prices = g.json()
    prices2 = []
    for i in range(0,24):
        prices2 = np.append(prices2,prices[i]['price'])
    return prices2
    
def energy_surplus(params):
    df_energy = load_sql(params['production_table'], params['username'], params['password'],params['db_address'],params['db_accesstype'])
    df_energy_cons = load_sql(params['consumption_table'],params['username'], params['password'], params['db_address'],params['db_accesstype'])
    surplus = df_energy['solar_energy'] +  df_energy['wind_energy'] - df_energy_cons['energy_use']
    return np.array(surplus)

"""Produce API bid and submit to API"""
def submit_bid(prices, to_sell, params):
    AIMLAC_CC_MACHINE = os.getenv("AIMLAC_CC_MACHINE")
    if AIMLAC_CC_MACHINE is not None:
        pass
    else:
        logger.error(f"{AIMLAC_CC_MACHINE} is invalid")
    host = f"http://{AIMLAC_CC_MACHINE}"
    applying_date = date.today() + timedelta(days=1)

    hourly_prices = prices[::2]
    hourly_to_sell = to_sell[::2]

    hourly_prices = hourly_prices - 0.1*np.mean(hourly_prices)
    json1 = []
    for i in range(0,len(hourly_prices)-1):
        json1.append({
                     "applying_date": applying_date.isoformat(),
                     "hour_ID": i+1,
                     "type": "BUY",
                     "volume": str(hourly_to_sell[i]),
                     "price": str(hourly_prices[i])
                     })
    
    p = requests.post(url=host + "/auction/bidding/set",
                  json={
                      "key":
                      "TESTKEY",
                      "orders": json1
                  })
    result_code = "Result Code:" + str(p.status_code) + ", " + p.text
    logger.info(result_code)

    if(p.status_code<400):
        d = p.json()
        if d['accepted'] == len(prices):
            logger.info('---Posted bids, {} bids accepted---'.format(d['accepted']))
        else:
            logger.error('---Failed to post bids, only {} accepted---'.format(d['accepted']))
    else:
        update_result_state = "Failed to post bids to server; stats are still available"

    df_bid = pd.DataFrame(columns={'timestamp','Bid_Price', 'Energy(KwH)'})
    dates = pd.date_range(date.today(), date.today() + timedelta(days=1), freq='H').to_list()
    dates = dates[:-1]
    df_bid['timestamp'] = dates
    df_bid['Bid_Price'] = hourly_prices
    df_bid['Energy(KwH)'] = hourly_to_sell
    dump_sql(df_bid, params['bid_table'], params['username'], params['password'],params['db_address'],params['db_accesstype'])
    return True
    
"""Get weather data from PVLib"""

# Will take the left over energy, the predicted clearout prices and
#create array of 24 bids for the next day, and then sumbit to the API

def run_main(config):
   
    #run modules
    weather(config) #hacky, needs changing
    logger.info("---CHECKPOINT: Calculating energy produced---")
    energy(config)
    logger.info("---CHECKPOINT: Calculating energy consumed---")
    energy_cons(config)

    with open(config[0]) as file:
        content = yaml.load(file, Loader=yaml.FullLoader)
        params = content['params']
		
    logger.info("---CHECKPOINT: Pulling Clear-out prices---")
    start_date = date.today() - timedelta(days=2)
    end_date = date.today() + timedelta(days=0)
    clearout_prices = get_clearout_prices(start_date, end_date)

    logger.info("---CHECKPOINT: Pulling most recent market prediction model---")
    local_model_filename = "Model/saved_model.pb"
    local_model_path = "Model"
    download_blob("model/saved_model.pb", "Model/saved_model.pb")
    download_blob("model/keras_metadata.pb", "Model/keras_metadata.pb")
    price_predictor = Predictor(local_model_path,clearout_prices)
    market_prices = price_predictor.predict()
    times = pd.date_range(date.today(), periods=48, freq='30T')
    #resample price_preditor to 30 minute 
    #Has problems at last time stamp as it is interpolating past its boundary
    market_prices_interp = sgnl.resample(market_prices, 48)
    #market_prices_interp = np.interp(np.arange(0., 24., 0.5), np.arange(0., 24., 1.), market_prices)
    
    logger.info("---CHECKPOINT: Calculating power to sell---")
    to_sell = energy_surplus(params)
    #get last 48 entries (if this runs multiple times it gets larger)
    to_sell = to_sell[-48:]
    logger.info("---CHECKPOINT: Submitting bid to API---")
    submit_bid(market_prices_interp, to_sell, params)
    #Puts stuff in a dataframe why not
    df_market_price = pd.DataFrame(data={'MarketPrices':market_prices_interp, 'TimeStamps':times})
    df_market_price.set_index('TimeStamps', inplace=True)
    dump_sql(df_market_price, params['market_table'], params['username'], params['password'],params['db_address'],params['db_accesstype'])
    
    produce_plots(params)
  
@app.route('/hello')
def web_hello():
	return 'hi'

@app.route('/update')
def web_update():
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    run_main(args.config)
	
    return update_result_state

@app.route('/', methods=['GET'])
def redirect_to_index():
    return send_from_directory('web/static', 'index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)	
	
