import numpy as np

def error_mitigation(temp,wind,sunrise,sunset):
    '''
    temp - array of temperature throughout the day (^o C)
    wind - array of wind speeds throughout the day (metres/s)
    sunrise/sunset to nearest hour
    '''
    
    panel_efficiency = 0.196
    pmax = -0.0037

    temp_act = 0
    eff_calc = 0

    for i in range(24):

        if i >= (sunrise + 1) and i <= (sunset +1):
            temp_act = temp[i] + 20 # accommodate for panel heating up during the day
            eff_calc = panel_efficiency - ((temp_act-25)*pmax)
        else:
            eff_calc = panel_efficiency - (temp[i]*pmax) # cool during the night

        if eff_calc > panel_efficiency:
            eff_calc = panel_efficiency

        if i < 10:
            print("0{0}:00: Solar panel efficiency = {1}%   ({2}%)".format(i,"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
        else:
            print("{0}:00: Solar panel efficiency = {1}%   ({2}%)".format(i,"%0.2f" %(eff_calc*100),"%0.2f" %((eff_calc/panel_efficiency)*100)))
                
        # Warnings
        if i > sunrise and i < sunset:
            if temp_act > 35 or temp_act < 15:
                print('`--->  Solar panel output will be affected by temperature.')

        if wind[i] < 3.5:
            print('`--->  Wind too low for turbine to work.')
        elif wind[i] > 25 and wind[i] <= 52:
            print('`--->  Wind too high for turbine to work.')
        elif wind[i] > 52:
            print('`--->  Turbine go crrrrrrack.')

        print('**********')


temp = np.array([1,0,0,0,0,0,0,1,2,4,6,-7,8,8,19,19,9,8,8,8,6,5,4,3]) # temperature degrees centigrade
wind = np.array([1,1,1,1,1,1,1,1,10,15,18,1,1,26,1,2,2,2,2,62,10,19,1,1]) # wind speed in m/s
sunrise = 7
sunset = 20

error_mitigation(temp,wind,sunrise,sunset)