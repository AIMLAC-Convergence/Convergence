import pandas as pd
import datetime
import pvlib
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import yaml
import logging

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler=logging.FileHandler('auto_bidder.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


from utils.sql_utils import *
global model 
model = GFS()

class DataFrame:
    def __init__(self):
        self._start = pd.Timestamp(datetime.date.today())
        self._end = pd.Timestamp(datetime.date.today())
        self._location = []
        self._cycles = 1

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
    
    @property
    def location(self):
        return self._location

    @property
    def cycles(self):
        return self._cycles
    
    @start.setter
    def start(self, new_start):
        self._start = new_start

    @end.setter
    def end(self, new_end):
        self._end = new_end

    @location.setter
    def location(self, new_loc):
        self._location = new_loc

    @cycles.setter
    def cycles(self, new_cycles):
        self._cycles = new_cycles
 
    def __call__(self):
        return self.fill_df()

    def get_wind_data(self):
        lattitude, longitude = self.location[0], self.location[1]
        print("Getting wind data")
        print("Start time:", str(self.start))
        print("End time:", str(self.end))
        dataFrame = model.get_processed_data(lattitude, longitude, self.start, self.end).reset_index().rename(columns={'index':'timestamp'})
        dataFrame.drop(columns=['low_clouds', 'mid_clouds', 'high_clouds'], inplace=True)
        dataFrame.set_index(pd.to_datetime(dataFrame['timestamp'], infer_datetime_format=True), inplace=True)
        dataFrame.drop(columns=['timestamp'], inplace=True)
        dataFrame = dataFrame.resample('30T').interpolate(method='linear') #change to 30min timestamp and use linear interpolation 
        dataFrame=dataFrame.reset_index().rename(columns={'index':'timestamp'})
        return dataFrame

    def get_solar_data(self):
        lattitude, longitude = self.location[0], self.location[1]
        intervals = self.cycles * 48
        dfs = []
        time = []
        time.append(self.start)
        for i in range(1,intervals):
            time.append(time[i-1] + pd.Timedelta(minutes=30))
            dfs.append(pvlib.solarposition.get_solarposition(time[i-1], lattitude, longitude, altitude=None, pressure=None, method='nrel_numpy', temperature=12))
        df = pd.concat(dfs)
        return df.reset_index().rename(columns={'index':'timestamp'})

    def fill_df(self):
        wind_df = self.get_wind_data()
        sun_df = self.get_solar_data()
        df=wind_df.merge(sun_df, on=['timestamp'])
        return df 

def main(config):

    with open(config[0]) as file:
         content = yaml.load(file, Loader=yaml.FullLoader)
         params = content['params']

    keys = ['weather_table','location', 'username', 'password']
    for key in keys:
        try:
            params[key]
        except KeyError:
            logger.exception(f'KeyError! Must provide: {key}')
            exit()
    
    df = DataFrame()   #initialise dataframe
    location, cycles, tz = params['location'], params['period'], 'Etc/Greenwich'
    df.location = (location)
    df.cycles = cycles

    if params['time'] == 'Now':
        df.start = pd.Timestamp(datetime.date.today(), tz=tz)
    else:
        date = params['time']
        if (datetime.datetime.strptime(date, '%Y-%m-%d')) is not None:
            df.start = pd.Timestamp(datetime.datetime(int(date.split("-")[0]),int(date.split("-")[1]),int(date.split("-")[2])), tz=tz)
    df.end = (df.start + pd.Timedelta(days=df.cycles))

    logger.info('Starting:{}, ending: {}'.format(df.start, df.end))
    
    all_data = df()                      #solar and wind data 
    #wind_data = df.get_wind_data()      #wind only 
    #sun_data = df.get_sun_data()        #solar only
    dump_sql(all_data, params['weather_table'], params['username'], params['password'],params['db_address'],params['db_accesstype'])    #create MySQL table

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)