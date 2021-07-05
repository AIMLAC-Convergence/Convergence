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

app = Flask(__name__, static_url_path='', static_folder='web/static', template_folder='web/templates')

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler=logging.FileHandler('auto_bidder.log', 'w+')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

#import user modules
from utils.sql_utils import *
from convergence_modules.weather_prediction.pvlib_to_sql import main as weather
from convergence_modules.energy_production.energy_production import main as energy
from convergence_modules.energy_consumption.Energy_use import main as energy_cons
from Model.scripts.make_prediction import Predictor

def actually_produce_plots(df, title):
    fig = go.Figure([{
    'x': df.index,
    'y': df[col],
    'name': col
    }  for col in df.columns])
    fig.update_layout(title_text = title)
    if title == 'Energy':
       fig.update_yaxes(title_text='kWh')
	
    fig.write_html("web/static/" + title.replace(" ", "") + ".html")
    #fig.write_image("web/static/images/" + title.replace(" ", "") + ".png")
    return True

def produce_plots(params):
    df_energy = load_sql(params['production_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).set_index("timestamp")
    df_weather = load_sql(params['weather_table'], params['username'], params['password'], params['db_address'],params['db_accesstype']).set_index("timestamp")
    df_energy.drop(columns=['units'], inplace = True)
    df_energy.rename(columns={'solar_energy':'solar_energy(kWh)', 'wind_energy':'wind_energy(kWh)'}, inplace = True)
    actually_produce_plots(df_energy, "Energy")
    actually_produce_plots(df_weather.loc[:, ['ghi', 'dni', 'dhi']], "Solar quantities")
    actually_produce_plots(df_weather.loc[:, ['zenith', 'azimuth', 'apparent_zenith']], "Solar angles")
    actually_produce_plots(df_weather.loc[:,['wind_speed']], "Wind speed")
    actually_produce_plots(df_weather.loc[:,['temp_air']], "Temperature")


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
def submit_bid(prices, to_sell):
    pass

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
		
    produce_plots(params)
    
    logger.info("---CHECKPOINT: Clear-out prices---")
    start_date = date.today() - timedelta(days=2)
    end_date = date.today() + timedelta(days=0)
    clearout_prices = get_clearout_prices(start_date, end_date)
    price_predictor = Predictor(params['model'],clearout_prices)
    market_prices = price_predictor.predict()
    to_sell = energy_surplus(params)
	
    #submit_bid(market_prices, to_sell)

@app.route('/hello')
def web_hello():
	return 'hi'

@app.route('/update')
def web_update():
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    run_main(args.config)
	
    return 'Update complete!'

@app.route('/', methods=['GET'])
def redirect_to_index():
    return send_from_directory('web/static', 'index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)	
	