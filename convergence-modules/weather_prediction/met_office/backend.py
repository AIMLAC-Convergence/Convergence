import requests
import json
import metoffer

from dataclasses import dataclass

@dataclass
class API:
    params: dict
    
    def __call__ (self):
       return call_api(self.params)

def call_api(params):
    """
    Function to return realtime temperature
    for each lat, lon
    """   
    # Make an API call
    base_metoffice_url = "http://datapoint.metoffice.gov.uk/public/data/"
    resource = "val/wxfcs/all/json/310149"
    key=params['apikey']
    url = base_metoffice_url + resource
    call_params={"res":"3hourly", "key":key}
    response = requests.get(url, call_params)
    if response.status_code == 200:
        location=params['location']
        api_key="1a926199-b810-46e0-a7f9-655d0189cc2a"
        M=metoffer.MetOffer(api_key)
        get_data = M.nearest_loc_forecast(location[0],location[1],metoffer.THREE_HOURLY)
        weather_data = metoffer.parse_val(get_data)
        return weather_data
    else:
        response = '<400>'
        print(f"{response} error code: check api key is valid.")
        exit()
    


