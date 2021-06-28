# -*- coding: utf-8 -*-
"""
Created on Thu May 27 11:37:32 2021

@author: c1616132
"""

import requests
from datetime import date, timedelta, datetime
import pytest
import os

import numpy as np
import pandas as pd
import holidays 
import datetime
from matplotlib import dates
import sys
import yaml

with open('path.yaml') as file:
         content = yaml.load(file, Loader=yaml.FullLoader)
         path = content['path']

sys.path.insert(1, path['direct'] + 'Convergence/utils')
sys.path.insert(1, path['direct'] + 'Convergence/convergence-modules')
#sys.path.insert(1,'/Convergence/utils')
from sql_utils import *
from sqlalchemy import create_engine
import pymysql
from weather_prediction.pvlib_to_sql import main as weather
from energy_production.energy_production import main as energy
from energy_consumption.Energy_use import main as energy_use
#import run_modules

AIMLAC_CC_MACHINE = os.getenv("AIMLAC_CC_MACHINE")
assert AIMLAC_CC_MACHINE is not None
host = f"http://{AIMLAC_CC_MACHINE}"

"""Call Clearout prices for API"""

start_date = date.today() - timedelta(days=1)
end_date = date.today() + timedelta(days=1)
g = requests.get(url=host + f"/auction/market/clearout-prices",
                 params=dict(start_date=start_date.isoformat(),
                             end_date=end_date.isoformat()))

assert len(g.json()) > 0

print(f"Getting data (clearout-prices):")
print("GET JSON reply:")
if g.status_code == 200:
    print('Status code = 200, request OK')

prices = g.json()
prices2 = []
for i in range(0,len(prices)):
    prices2 = np.append(prices2,prices[i]['price'])
    
         
"""Run prediction for next day"""

"""Run production module, energy use module"""

weather(['weather_params.yaml']) # dumps into a forcast table
energy(['production_params.yaml']) # dumps into an energy production table
energy_use(['consumption_params.yaml']) # will dump into a energy use table

"""Calc energy left"""

# Will take the tables from energy production and energy use subtract


"""Produce API bid and submit to API"""

# Will take the left over energy, the predicted clearout prices and
#create array of 24 bids for the next day, and then sumbit to the API