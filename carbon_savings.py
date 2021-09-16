# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 09:53:48 2021

@author: c1616132
"""

import requests
from datetime import datetime, date, timedelta
import pytz
import pytest
import os


AIMLAC_CC_MACHINE = os.getenv("AIMLAC_CC_MACHINE")
assert AIMLAC_CC_MACHINE is not None
host = f"http://{AIMLAC_CC_MACHINE}"

def carbon_intensity(date):
    
    #date = datetime.today() - timedelta(days=1)
    #date = date.strftime('%Y-%m-%d')
    url = "https://api.carbonintensity.org.uk/intensity/"
    
    response = requests.get(url + date + 'T00:00Z/fw24h')
    
    ci = []
    length = len(response.json()['data'])
    
    for i in range(1,length,1):
        ci.append(response.json()['data'][i]['intensity']['actual'])
    
    return ci
    
def test_get_average_power(date):
    #last_30m_start = datetime.now() - timedelta(minutes=30)
    when = date.astimezone(pytz.utc)
    g = requests.get(url=host + "/sim/llanwrtyd-wells/30m-average-power",
                     params=dict(
                         year=when.year,
                         month=when.month,
                         day=when.day,
                         hour=when.hour,
                         minute=when.minute,
                     ))
    return g

def main():
    date = datetime.now() - timedelta(days=1)
    date = date.strftime('%Y-%m-%d')
    ci = carbon_intensity(date)
    carbon_used = []
    date = datetime.strptime(date, '%Y-%m-%d')
    for i in range(0,len(ci),1):
        g = test_get_average_power(date)
        power = g.json()['average power']
        carbon = power*ci[i]
        carbon_used.append(carbon)
        date = date + timedelta(minutes=30)
    carbon_used = sum(carbon_used)/-1000000
    return carbon_used
    
    
if __name__ == '__main__':
    #date = '2021-09-01'
    cu = main()
    #print(day_saved)
    