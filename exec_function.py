import requests
from datetime import date, timedelta
import os
import numpy as np
import pandas as pd
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging

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
    assert len(g.json()) > 0   
    if g.status_code != 200:
        logger.error(f"Status code {g.status_code}, request failed")      
    prices = g.json()
    prices2 = []
    for i in range(0,len(prices)):
        prices2 = np.append(prices2,prices[i]['price'])
    return prices2
    
def energy_surplus(params):
    df_energy = load_sql(params['production_table'], params['username'], params['password'])
    df_energy_cons = load_sql(params['consumption_table'],params['username'], params['password'])
    surplus = df_energy['solar_energy'] +  df_energy['wind_energy'] - df_energy_cons['energy_use']
    return np.array(surplus)

"""Produce API bid and submit to API"""
def submit_bid(prices, to_sell):
    pass

"""Get weather data from PVLib"""

# Will take the left over energy, the predicted clearout prices and
#create array of 24 bids for the next day, and then sumbit to the API

def main(config):
    #run modules
    weather(config) #hacky, needs changing
    logger.info("---CHECKPOINT: Calculating energy produced---")
    energy(config)
    logger.info("---CHECKPOINT: Calculating energy consumed---")
    energy_cons(config)

    with open(config[0]) as file:
        content = yaml.load(file, Loader=yaml.FullLoader)
        params = content['params']
    
    logger.info("---CHECKPOINT: Clear-out prices---")
    start_date = date.today() - timedelta(days=1)
    end_date = date.today() + timedelta(days=1)
    clearout_prices = get_clearout_prices(start_date, end_date)
    price_predictor = Predictor(params['model'],clearout_prices)
    market_prices = price_predictor.predict()
    to_sell = energy_surplus(params)
    #submit_bid(market_prices, to_sell)

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)