# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 15:57:59 2021

@author: David
"""

from sqlalchemy import create_engine
import pymysql

import numpy as np
import yaml
import pandas as pd
import datetime
import os


def windEnergy(wSpd, intLength, wT):
    yval = np.exp(np.interp(wSpd , wT['PCx'], np.log(np.array(wT['PCy']) + 1))) - 1.
    energy = yval* ((wSpd > wT['Cutin']) and (wSpd < wT['Cutoff'])) * wT['Count'] * intLength
    return energy

def solarEnergy(DNI, DHI, z, A, intLength, sP):
    GTI = (DHI*np.cos((sP['Tilt']) * np.pi/180)  + (DNI*np.cos((z - sP['Tilt']) * np.pi/180) * (A > 90. and A < 270.) *np.cos((A - sP['Direction']) * np.pi/180)) ) * (z < 90.)  
    power = GTI * sP['Area'] * sP['Eff']
    power = ((power*(power <= sP['Cutoff'])) + (sP['Cutoff'] * (power > sP['Cutoff']))) * sP['Count']
    energy = power * intLength
    return energy

def get_Power(forecast, params, intLength):
    powerdict = []
    for index, ts in forecast.iterrows():
        se = solarEnergy(ts['dni'],ts['dhi'],ts['zenith'],ts['azimuth'],intLength, params['solar'])
        we = windEnergy(ts['wind_speed'], intLength, params['wind'])
        if params['units'] == 'kWh':
            se /= (3600. * 1000.)
            we /= (3600. * 1000.)
        powerdict.append({ 'timestamp':ts['timestamp'],'solar_energy':se, 'wind_energy':we, 'units':params['units']})
    pf = pd.DataFrame(data=powerdict, index = forecast.index)
    #forecast = forecast.join(pf, how='outer')  
    return pf


def main(config):
    with open(config[0]) as file:
         params = yaml.load(file, Loader=yaml.FullLoader)['params'] 
         
    #Check all the required information is in the params file
    keys = ['name','username', 'password','forecastname','wind','solar','units']
    windkeys = ['Cutoff','Cutin','Count','PCy','PCx']
    solarkeys = ['Cutoff','Eff','Count','Area','Tilt', 'Direction']
    for key in keys:
        try:
            params[key]
        except KeyError:
            print(f'KeyError! Must provide: {key}')
            exit()
    
    for key in windkeys:
        try:
            params['wind'][key]
        except KeyError:
            print(f'KeyError! Must provide: [wind][{key}]')
            exit()
    for key in solarkeys:
        try:
            params['solar'][key]
        except KeyError:
            print(f'KeyError! Must provide: [wind][{key}]')
            exit()
    #Get the forecast data from the database
    sqlEngine = create_engine(f"mysql+pymysql://{params['username']}:{params['password']}@localhost/convergence_test",pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    try:
        df = pd.read_sql(params['forecastname'], dbConnection)
    except ValueError as vx:
        print(vx)
    except Exception as ex:   
        print(ex)
    finally:
        dbConnection.close()
    #Calculate expected power production
    intLength = (df['timestamp'][1] - df['timestamp'][0]).total_seconds()
    pf = get_Power(df, params, intLength)
    #Send power production information to database
    dbConnection = sqlEngine.connect()
    try:
        frame = pf.to_sql(params['name'], dbConnection, if_exists='replace', index=False);
    except ValueError as vx:
        print(vx)
    except Exception as ex:   
        print(ex)
    else:
        print("Table %s created successfully."%params['name']);   
    finally:
        dbConnection.close()

