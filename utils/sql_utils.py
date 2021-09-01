from sqlalchemy import create_engine
import pandas as pd

import logging

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler=logging.FileHandler('auto_bidder.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def dump_sql(df, tableName, username, password, address='localhost', accesstype='IP'):

    logging.info("Dumping to " + tableName + " at address " + address + " via " + accesstype)

    if accesstype=='UNIX':
        sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@/convergence_test?unix_socket=/cloudsql/{address}',pool_recycle=3600)
    else:
	    sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@{address}/convergence_test',pool_recycle=3600)

    dbConnection = sqlEngine.connect()
    try:
        frame = df.to_sql(tableName, dbConnection, if_exists='append', index=False)
    except ValueError as vx:
        logging.info("ValueError:" + str(vx))
    except Exception as ex:   
        logging.info("Exception:" + str(ex))
    else:
        logging.info("Table %s created successfully."%tableName);   
    finally:
        dbConnection.close()

    return 1

def load_sql(tableName, username, password, address='localhost', accesstype='IP'):

    logging.info("Reading From " + tableName + " at address " + address + " via " + accesstype)

    if accesstype=='UNIX':
        sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@/convergence_test?unix_socket=/cloudsql/{address}',pool_recycle=3600)
    else:
	    sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@{address}/convergence_test',pool_recycle=3600)
		
    dbConnection = sqlEngine.connect()
    try:
        df = pd.read_sql(tableName, dbConnection)
    except ValueError as vx:
        logging.info("ValueError:" + str(vx))
    except Exception as ex:   
        logging.info("Exception:" + str(ex))
    finally:
        dbConnection.close()
    return df
