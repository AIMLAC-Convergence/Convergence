from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import datetime
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP
import os
import yaml

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

    model = GFS()
    dataFrame = model.get_processed_data(latitude, longitude, start, end).reset_index().rename(columns={'index':'timestamp'})

    sqlEngine = create_engine(f"mysql+pymysql://{params['username']}:{params['password']}@localhost/convergence_test",pool_recycle=3600)

    dbConnection = sqlEngine.connect()

    try:
        frame = dataFrame.to_sql(tableName, dbConnection, if_exists='replace', index=False);
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