from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import datetime
import pvlib
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP
import os
import yaml

def get_sun_pos(start, latitude, longitude, tz):
    dfs = []
    time = []
    time.append(start)
    for i in range(1,48):
        time.append(time[i-1] + pd.Timedelta(minutes=30))
        dfs.append(pvlib.solarposition.get_solarposition(time[i-1], latitude, longitude, altitude=None, pressure=None, method='nrel_numpy', temperature=12))
    df = pd.concat(dfs)
    return (df)

def main(config):

    with open(config[0]) as file:
         content = yaml.load(file, Loader=yaml.FullLoader)
         params = content['params']

    keys = ['name','location', 'username', 'password']
    for key in keys:
        try:
            params[key]
        except KeyError:
            print(f'KeyError! Must provide: {key}')
            exit()
   
   
    tableName = params['name']   
    latitude, longitude, tz = params['location'][0],params['location'][1], 'Etc/Greenwich'
    
    if params['time'] == 'Now':
        start = pd.Timestamp(datetime.date.today(), tz=tz)
    else:
        date = params['time']
        start = pd.Timestamp(datetime.datetime(int(date.split("-")[0]),int(date.split("-")[1]),int(date.split("-")[2])), tz=tz)
    end = start + pd.Timedelta(days=params['period'])

    print(f"starting:{start},ending:{end}")
    df_sun_pos = get_sun_pos(start, latitude, longitude, tz).reset_index().rename(columns={'index':'timestamp'})
   
    model = GFS()
    dataFrame = model.get_processed_data(latitude, longitude, start, end).reset_index().rename(columns={'index':'timestamp'})
    dataFrame.drop(columns=['low_clouds', 'mid_clouds', 'high_clouds'], inplace=True)
    dataFrame.set_index(pd.to_datetime(dataFrame['timestamp'], infer_datetime_format=True), inplace=True)
    dataFrame.drop(columns=['timestamp'], inplace=True)
    dataFrame = dataFrame.resample('30T').interpolate(method='linear') #change to 30min timestamp and use linear interpolation 
    dataFrame=dataFrame.reset_index().rename(columns={'index':'timestamp'})
    df=dataFrame.merge(df_sun_pos, on=['timestamp'])
     
    sqlEngine = create_engine(f"mysql+pymysql://{params['username']}:{params['password']}@localhost/convergence_test",pool_recycle=3600)

    dbConnection = sqlEngine.connect()

    try:
        frame = df.to_sql(tableName, dbConnection, if_exists='replace', index=False);
    except ValueError as vx:
        print(vx)
    except Exception as ex:   
        print(ex)
    else:
        print("Table %s created successfully."%tableName);   
    finally:
        dbConnection.close()
   

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)