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


date = datetime.date.today() + datetime.timedelta(days=1) 
date = date.strftime('%Y-%m-%d') #Date
#Temperature for next 24 hours in 48 hal hour chunks
T = [1,1,-7,1,2,16,2,3,3,4,5,6,6,5,4,3,3,2,2,2,1,1,1,1,
     1,1,-7,1,2,16,2,3,3,4,5,6,6,5,4,3,3,2,2,2,1,1,1,1]
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

def temp_cost(T):
    heating = np.array([-6*t+90 for t in T])
    heating[heating>120] = 120
    heating[heating<0] = 0
    return heating
    

# Calculate energy if it's a work day
def total_energy_sum(weekday2,date2,date3,f,total_energy):
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


total_energy2 = total_energy_sum(weekday2,date2,date3,f,total_energy)
