# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 16:15:44 2021

@author: c1616132
"""


import requests
from datetime import date, timedelta, datetime
import pytz
import pytest
import os
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, send_from_directory, render_template
import pandas as pd
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt


AIMLAC_CC_MACHINE = os.getenv("AIMLAC_CC_MACHINE")
assert AIMLAC_CC_MACHINE is not None
host = f"http://{AIMLAC_CC_MACHINE}"

#date = datetime.now() - timedelta(days=10)

app = Flask(__name__)

def avg_power(date):
    #last_30m_start = datetime.now() - timedelta(minutes=30)
    last_30m_start = date
    when = last_30m_start.astimezone(pytz.utc)
    g = requests.get(url=host + "/sim/llanwrtyd-wells/30m-average-power",
                     params=dict(
                         year=when.year,
                         month=when.month,
                         day=when.day,
                         hour=when.hour,
                         minute=when.minute,
                     ))
    return g

#date2 = date.today() + timedelta(days=2)

def get_bids(n):
    #applying_date = date2
    applying_date = date.today() - timedelta(days=n)
    g = requests.get(url=host + "/auction/bidding/get",
                     params=dict(
                         key="TESTKEY",
                         applying_date=applying_date.isoformat(),
                     ))
    return g #print(g.json())

def compare():
    comp_date_avg = datetime.now() - timedelta(days=10)
    comp_date_bid = date.today() - timedelta(days=20)
    when = comp_date_avg.astimezone(pytz.utc)
    bids = requests.get(url=host + "/auction/bidding/get",
                     params=dict(
                         key="TESTKEY",
                         applying_date=comp_date_bid.isoformat(),
                     ))
    bids = bids.json()[-24:]
    vol_pred = []
    vol_real = []
    for i in range(0,len(bids),1):
        pred = bids[i]['volume']
        vol_pred = np.append(vol_pred,pred)
        real1 = requests.get(url=host + "/sim/llanwrtyd-wells/30m-average-power",
                         params=dict(
                             year=when.year,
                             month=when.month,
                             day=when.day,
                             hour=i,
                             minute=0,
                         ))
        real2 = requests.get(url=host + "/sim/llanwrtyd-wells/30m-average-power",
                         params=dict(
                             year=when.year,
                             month=when.month,
                             day=when.day,
                             hour=i,
                             minute=30,
                         ))
        real = real1.json()['average power'] + real2.json()['average power']
        vol_real = np.append(vol_real,real)
    
    #plt.plot(range(0,24,1),vol_pred,'r')
    #plt.plot(range(0,24,1),vol_real/1000,'b')
    vol_pred = np.reshape(vol_pred,(len(vol_pred),1))
    vol_real = np.reshape(vol_real,(len(vol_real),1))
    array = np.hstack((vol_pred,vol_real))
    df = pd.DataFrame(array)
    actually_produce_plots(df, "Comparison")
    
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
    #fig.write_html(filename)
    plotly.offline.plot(fig, filename="templates/" + filename)
    #upload_blob(filename,filename)
    #fig.write_image("web/static/images/" + title.replace(" ", "") + ".png")
    return True
        

#float(''.join(tuple(price)[1:-1]))
@app.route('/hello')
def web_hello():
    return 'hi'

@app.route('/comp')
def comp():
    compare()
    return render_template('Comparison.html')

@app.route('/')
def home():
    return 'This is the home page.'

if __name__ == "__main__":
    app.run(debug=True)

