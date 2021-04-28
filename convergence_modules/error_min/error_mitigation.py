import numpy as np
import math

def error_mitigation(temp,wind,sunrise,sunset):
    '''
    temp - array of temperature semihourly for 24hrs (Centigrade)
    wind - array of wind speeds semihourly for 24hrs (metres/sec)
    sunrise/sunset to nearest half hour
    '''
    
    panel_efficiency = 0.196 # Output efficiency of panel
    pmax = -0.0037 # Percentage output lost per degree above nominal operating temp

    temp_act = 0
    eff_calc = 0

    for i in range(48):

        # Calculate the actual temperature of panel
        if i >= (sunrise*2 + 1) and i <= ((sunset*2) +1):
            temp_act = temp[i] + 20 # accommodate for panel heating up during the day
            eff_calc = panel_efficiency - ((temp_act-25)*pmax)
        else:
            eff_calc = panel_efficiency - (temp[i]*pmax) # cool during the night

        if eff_calc > panel_efficiency:
            eff_calc = panel_efficiency # Can't be more efficient than rated in negative temp

        # Calculate panel efficiency throughout the day accounting for temp
        if i%2 == 0:
            if i>24:
                print("{0}:00: Solar panel efficiency = {1}%   ({2}%)".format(math.floor(i/2),"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
            elif i<19:
                print("0{0}:00: Solar panel efficiency = {1}%   ({2}%)".format(math.floor(i/2),"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
            else:
                print("{0}:00: Solar panel efficiency = {1}%   ({2}%)".format(math.floor(i/2),"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
        else:
            if i>20:
                print("{0}:30: Solar panel efficiency = {1}%   ({2}%)".format(math.floor(i/2),"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
            else:
                print("0{0}:30: Solar panel efficiency = {1}%   ({2}%)".format(i-math.ceil(i/2),"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
                   
        # Warnings
        if i > sunrise*2 and i < sunset*2:
            if temp_act > 35 or temp_act < 15:
                print('`--->  Solar panel output will be affected by temperature.')

        if wind[i] < 3.5:
            print('`--->  Wind too low for turbine to work.')
        elif wind[i] > 25 and wind[i] <= 52:
            print('`--->  Wind too high for turbine to work.')
        elif wind[i] > 52:
            print('`--->  Turbine go crrrrrrack.')

        print('**********')


temp = np.array([7,7,6,6,6,6,6,6,6,6,5,5,5,5,5,5,5,5,5,5,5,5,6,6,6,6,7,7,7,7,7,7,7,7,7,7,7,7,6,6,6,6,5,5,5,5,5,5]) # temperature degrees centigrade
wind = np.array([2,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,4,4,5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,5,4,4,5,5,4,4,4,4,4,4,4,4]) # wind speed in m/s
sunrise = 7
sunset = 20

error_mitigation(temp,wind,sunrise,sunset)