# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 09:31:49 2021

@author: c1616132
"""

import numpy as np
import pandas as pd
import holidays 
from datetime import datetime
from matplotlib import dates


date = datetime.today().strftime('%Y-%m-%d') #Date
T = [1,1,-7,1,2,16,2,3,3,4,5,6,6,5,4,3,3,2,2,2,1,1,1,1] #Temperature for next 24 hours
#Is it a weekday?
weekday = pd.bdate_range(date,date)
#Is it a bank holiday?
hol = holidays.Wales()
f = hol.get(date)
#Is it Christmas break?
date2 = int(datetime.now().strftime('%m'))
date3 = int(datetime.now().strftime('%d'))

#Data_centre energy
data_centre = 200*24
total_energy = data_centre

def temp_cost(T):
    T2 = np.array(T[:8])
    def y(T): return -6*T + 90
    T3 = y(T2)
    T4 = y(T[8])*0.5
    T3 = np.append(T3,T4)
    T3[T3>120] = 120
    T3[T3<0] = 0
    print(T3)
    return np.sum(T3)
    

# Calculate energy if it's a work day
if (len(weekday) == 1) and f is None:
    if (date2 == 12):
        if (21<=date3<=31):
            exit
        else:
            pcs = 10*8.5
            lighting = 20*8.5
            t = temp_cost(T)
            total_energy += pcs + lighting + t
    else:
        pcs = 10*8.5
        lighting = 20*8.5
        t = temp_cost(T)
        print(t)
        total_energy += pcs + lighting + t
else:
    exit

print(total_energy)