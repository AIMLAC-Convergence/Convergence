# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 09:31:49 2021

@author: c1616132
"""

import numpy as np
import pandas as pd
import holidays 
import datetime
from matplotlib import dates
import matplotlib.pyplot as plt
import sys
import yaml
#sys.path.insert(1,'C:/Users/c1616132/Documents/phd_stuff/coding_challenge/Convergence/utils')
sys.path.insert(1,'/Convergence/utils')
from sql_utils import dump_sql
from sqlalchemy import create_engine
import pymysql

def load_sql(tableName, username, password):

    sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@localhost/convergence_test',pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    try:
        df = pd.read_sql(tableName, dbConnection)
    except ValueError as vx:
        print(vx)
    except Exception as ex:   
        print(ex)
    finally:
        dbConnection.close()

    return df

def work_time(dates):
    at_work = np.zeros(len(dates))
    for d, i in zip(dates, range(len(dates))):
        holiday = holidays.Wales().get(datetime.datetime(d.year, d.month, d.day))
        work_day = (int(d.day_of_week)<5)
        xmas_holiday = (int(d.month) == 12 and (21<= d.day <=31))
        work_hours = ((9*60)<=((d.hour*60) + d.minute)<= (17*60 + 30)) 
        at_work[i] = (not holiday) and work_day and (not xmas_holiday) and work_hours
    return at_work

def energy_pcs():
    return 10*0.5

def energy_lighting():
    return 20*0.5

def energy_data_centre():
    return 200*0.5

def energy_heating(T):
    heating = np.array([-6*t+90 for t in T])
    heating[heating>120] = 120
    heating[heating<0] = 0
    return heating
    

# Calculate energy if it's a work day
def total_energy_sum(at_work,T):
    pcs = energy_pcs()
    lighting = energy_lighting()
    t = energy_heating(T)
    #Data_centre energy
    data_centre = energy_data_centre()
    
    total_energy = np.zeros(len(T)) + data_centre + at_work*(pcs + lighting + t)
    return total_energy


def main(config):
    with open(config[0]) as file:
         content = yaml.load(file, Loader=yaml.FullLoader)
         params = content['params']

    keys = ['consumptionname', 'forecastname','username', 'password']
    for key in keys:
        try:
            params[key]
        except KeyError:
            print(f'KeyError! Must provide: {key}')
            exit()
    
    weather_table = params['forecastname']
    this_table = params['consumptionname']
    username = params['username']
    password = params['password']
    
    frame = load_sql(weather_table,username,password)
    
    T = frame['temp_air'].values
    at_work = work_time(frame.timestamp)
    #Is it Christmas break?
    #date1 = datetime.date.today() + datetime.timedelta(days=1)
    #date2 = int(date1.strftime('%m'))
    #date3 = int(date1.strftime('%d'))
    energy_use = total_energy_sum(at_work,T)
    df = pd.DataFrame(data=energy_use,columns=['energy_use'])
    
    dump_sql(df, this_table,username,password)
    
    
    dates = frame.timestamp
    # plt.figure(figsize = (10,15))
    # plt.subplot(2,1,1)
    # plt.title('Energy Total')
    # plt.plot(dates,energy_use)
    # plt.subplot(2,1,2)
    # plt.title('Energy Breakdown')
    # at_work = work_time(dates)
    # plt.plot(dates, at_work*energy_pcs(),label='PCS')
    # plt.plot(dates, np.ones(len(dates))*energy_data_centre(),label='Data Centre')
    # plt.plot(dates, at_work*energy_lighting(),label='Lighting')
    # plt.plot(dates, at_work*energy_heating(T),label='Heating')
    # plt.fill_between(dates, -1, energy_use.max(), where=at_work,
    #             facecolor='yellow', alpha=0.5,label='Work hours')
    # plt.legend()
    # plt.ylim([-1, energy_use.max()])