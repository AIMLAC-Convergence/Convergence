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

    report = [[0 for c in range(4)] for r in range(48)]
    warn1=''
    warn2=''

    for i in range(48):

        report[i][0] = i

        # Calculate the actual temperature of panel
        if i >= (sunrise*2 + 1) and i <= ((sunset*2) +1):
            temp_act = temp[i] + 20 # accommodate for panel heating up during the day
            eff_calc = panel_efficiency - ((temp_act-25)*pmax)
        else:
            eff_calc = panel_efficiency - (temp[i]*pmax) # cool during the night

        if eff_calc > panel_efficiency:
            eff_calc = panel_efficiency # Can't be more efficient than rated in negative temp

        report[i][1] = eff_calc

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
                warn1 = '`--->  Solar panel output will be affected by temperature.'
                print(warn1)

        report[i][2] = warn1

        if wind[i] < 3.5:
            warn2 = '`--->  Wind too low for turbine to work.'
        elif wind[i] > 25 and wind[i] <= 52:
            warn2 = '`--->  Wind too high for turbine to work.'
        elif wind[i] > 52:
            warn2 = '`--->  Turbine go crrrrrrack.'
            print(warn2)

        report[i][3] = warn2

        print('**********')

    return report



'''
Sample values
temp = np.array([7,7,6,6,6,6,6,6,6,6,5,5,5,5,5,5,5,5,5,5,5,5,6,6,6,6,7,7,7,7,7,7,7,7,7,7,7,7,6,6,6,6,5,5,5,5,5,5]) # temperature degrees centigrade
wind = np.array([2,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,4,4,5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,5,4,4,5,5,4,4,4,4,4,4,4,4]) # wind speed in m/s
sunrise = 7 # 7am
sunset = 20 # 8pm
'''

print(error_mitigation(temp,wind,sunrise,sunset))