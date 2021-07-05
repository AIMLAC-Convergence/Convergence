from sqlalchemy import create_engine
import pandas as pd

def dump_sql(df, tableName, username, password, address='localhost', accesstype='IP'):

    print("Dumping to " + tableName)

    if accesstype=='UNIX':
        sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@/convergence_test?unix_socket=/cloudsql/{address}',pool_recycle=3600)
    else:
	    sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@{address}/convergence_test',pool_recycle=3600)

    dbConnection = sqlEngine.connect()
    try:
        frame = df.to_sql(tableName, dbConnection, if_exists='replace', index=False);
    except ValueError as vx:
        print("ValueError:" + str(vx))
    except Exception as ex:   
        print("Exception:" + str(ex))
    else:
        print("Table %s created successfully."%tableName);   
    finally:
        dbConnection.close()

    return 1

def load_sql(tableName, username, password, address='localhost', accesstype='IP'):

    print("Reading From " + tableName)

    if accesstype=='UNIX':
        sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@/convergence_test?unix_socket=/cloudsql/{address}',pool_recycle=3600)
    else:
	    sqlEngine = create_engine(f'mysql+pymysql://{username}:{password}@{address}/convergence_test',pool_recycle=3600)
		
    dbConnection = sqlEngine.connect()
    try:
        df = pd.read_sql(tableName, dbConnection)
    except ValueError as vx:
        print("ValueError:" + str(vx))
    except Exception as ex:   
        print("Exception:" + str(ex))
    finally:
        dbConnection.close()
    return df