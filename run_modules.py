from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from subprocess import call
import yaml
import os
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from flask import Flask

from utils.sql_utils import *
from convergence_modules.weather_prediction.pvlib_to_sql import main as weather
from convergence_modules.energy_production.energy_production import main as energy

#app = Flask(__name__)

def actually_produce_plots(df, title):
    fig = go.Figure([{
    'x': df.index,
    'y': df[col],
    'name': col
    }  for col in df.columns])
    fig.update_layout(title_text = title)
    if title == 'Energy':
       fig.update_yaxes(title_text='kWh')
    fig.show()
    return True

def produce_plots(params):
    df_energy = load_sql(params['name'], params['username'], params['password']).set_index("timestamp")
    df_weather = load_sql(params['forecastname'], params['username'], params['password']).set_index("timestamp")
    df_energy.drop(columns=['units'], inplace = True)
    df_energy.rename(columns={'solar_energy':'solar_energy(kWh)', 'wind_energy':'wind_energy(kWh)'}, inplace = True)
    actually_produce_plots(df_energy, "Energy")
    actually_produce_plots(df_weather.loc[:, ['ghi', 'dni', 'dhi']], "Solar quantities")
    actually_produce_plots(df_weather.loc[:, ['zenith', 'azimuth', 'apparent_zenith']], "Solar angles")
    actually_produce_plots(df_weather.loc[:,['wind_speed']], "Wind speed")
    actually_produce_plots(df_weather.loc[:,['temp_air']], "Temperature")

def main(config):
    #run modules
    weather(config)
    energy(config)

    with open(config[0]) as file:
        content = yaml.load(file, Loader=yaml.FullLoader)
        params = content['params']
    produce_plots(params)

if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=8080)	
#	
#@app.route('/update')
#def web_run():
#    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
#    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
#    args = parser.parse_args()
#    main(args.config)