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
import sys
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



def temp_cost(T):
    heating = np.array([-6*t+90 for t in T])
    heating[heating>120] = 120
    heating[heating<0] = 0
    return heating
    

# Calculate energy if it's a work day
def total_energy_sum(weekday2,date2,date3,f,total_energy,T):
    pcs = 10*0.5
    lighting = 20*0.5
    t = temp_cost(T)
    if (weekday2 == 1) and f is None:
        if (date2 == 12):
            if (21<=date3<=31):
                exit
            else:
                total_energy[18:35] = total_energy[18:35] + pcs + lighting + t[18:35]
        else:
            total_energy[18:35] = total_energy[18:35] + pcs + lighting + t[18:35]
    else:
        exit
    return total_energy


def main():
    
    #tablename = 'test2'
    #username = 'root'
    #password = 'Trust4rooT'
    
    frame = load_sql(tablename,username,password)
    
    T = frame['temp']
    
    date = datetime.date.today() + datetime.timedelta(days=1) 
    date = date.strftime('%Y-%m-%d') #Date
    #Is it a weekday?
    weekday = pd.bdate_range(date,date)
    weekday2 = len(weekday)
    #Is it a bank holiday?
    hol = holidays.Wales()
    f = hol.get(date)
    #Is it Christmas break?
    date1 = datetime.date.today() + datetime.timedelta(days=1)
    date2 = int(date1.strftime('%m'))
    date3 = int(date1.strftime('%d'))
    
    #Data_centre energy
    data_centre = 200*0.5
    
    total_energy = np.zeros(len(T)) + data_centre
    
    total_energy = total_energy_sum(weekday2,date2,date3,f,total_energy,T)
    
    df = pd.DataFrame(data=total_energy,columns=['energy_use'])
    df2 = frame.join(df)
    
    dump_sql(df2, tablename,username,password)