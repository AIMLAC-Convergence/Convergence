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
from utils.sql_utils import dump_sql
from sqlalchemy import create_engine
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

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

    frame = load_sql(params['weather_table'],params['username'],params['password'])

    T = frame['temp_air'].values
    at_work = work_time(frame.timestamp)
    #Is it Christmas break?
    #date1 = datetime.date.today() + datetime.timedelta(days=1)
    #date2 = int(date1.strftime('%m'))
    #date3 = int(date1.strftime('%d'))
    energy_use = total_energy_sum(at_work,T)
    df = pd.DataFrame(data=energy_use,columns=['energy_use'])
    
    dump_sql(df, params['consumption_table'],params['username'],params['password'])
    
    
if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)