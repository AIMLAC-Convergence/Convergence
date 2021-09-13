import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import save_model
import ast
import time
from datetime import date, timedelta
import requests

class RNN_Model:
    def __init__(self, dataframe, time_lag):
        self._dataframe = dataframe
        self._time_lag = time_lag
        self._dataset = None
        self._scaler = None
        
    def __call__(self, save=False):
        df_proc = RNN_Model.tidy_df(self._dataframe)
        RNN_Model.plot(df_proc)
        self._dataset = self._dataframe.iloc[:,0:2].values
        self._scaler = MinMaxScaler(feature_range=(0, 1))
        X = self._dataset[:,0]
        y = self._dataset[:,1]
        y = self._scaler.fit_transform(y.reshape(-1,1))
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25)
        train_X, train_y =  self.create_dataset(y_train)
        train_X_conv, train_y_conv = RNN_Model.split_sequence(y_train, 3)
        #ic(train_X_conv.shape, train_y_conv.shape)
        test_X, test_y   =  self.create_dataset(y_test)
        train_X = np.reshape(train_X, (train_X.shape[0], 1, train_X.shape[1]))
        test_X = np.reshape(test_X, (test_X.shape[0], 1, test_X.shape[1]))
        #ic(test_X.shape)
        #ic(train_X.shape, train_y.shape)
        print("---CHECKPOINT: Training model with TensorFlow backend---")
        time.sleep(1)
        model, model_history = self.train(train_X, train_y)
        RNN_Model.plot_loss(model_history)
        y_pred_test  = RNN_Model.stretch(self._scaler.inverse_transform(model.predict(test_X)))
        #ic(y_pred_test.shape)
        test_results = RNN_Model.make_dataframe(self,test_X, y_pred_test)
        RNN_Model.plot(test_results, pred=True)
        if save == True:
            save_model(model,'model') 
            print("Model Saved")
            
    @staticmethod
    def stretch(array):
        for i in range (1, len(array)):
            if array[i-1] > array[i]:
                array[i-1] = array[i-1] * 1.5
            elif array[i-1] < array[i]:
                array[i-1] = array[i-1] * 0.5
        return array
        
    @staticmethod
    def split_sequence(sequence, n_steps):
        X, y = list(), list()
        for i in range(len(sequence)):
            end_ix = i + n_steps
            if end_ix > len(sequence)-1:
                break
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)

    def create_dataset(self, y_train):
        X_data = []
        y_data = []
        for i in range(self._time_lag, len(y_train)):
            X_data.append(list(y_train[i-self._time_lag]))
            y_data.append(list(y_train[i]))
        return np.array(X_data), np.array(y_data)
    
    def train(self, train_X, train_y):
        model = Sequential()
        model.add(LSTM(4, input_shape=(1, 1)))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        history = model.fit(train_X, train_y, epochs=10, batch_size=1, verbose=2)
        return model, history
    
    def make_dataframe(self,test_X, y_pred_test):
        pred_df = pd.DataFrame(columns = ['date', 'test_set','prediction'])
        low_lim = len(self._dataframe) - test_X.shape[0]
        date_ind = np.array(self._dataframe.loc[low_lim:len(self._dataframe),'date'])
        period = np.array(self._dataframe.loc[low_lim:len(self._dataframe),'period'])
        pred_df['date'] = date_ind
        pred_df['period'] = period
        pred_df['test_set'] = np.array(self._scaler.inverse_transform(test_X.reshape(test_X.shape[0],1))).reshape(test_X.shape[0])
        pred_df['prediction'] = np.array(y_pred_test.reshape(test_X.shape[0],1)).reshape(test_X.shape[0])
        df_to_plot = RNN_Model.tidy_df(pred_df)
        return df_to_plot

    @staticmethod
    def plot_loss(model_history):
        plt.figure()
        plt.plot(np.arange(1,11), model_history.history['loss'], label="loss function")
        plt.xlabel("epoch")
        plt.ylabel('loss')
        plt.legend()
        plt.show()
    
    @staticmethod
    def reshape_data(train_x, test_x):
        train_X = np.reshape(train_X, (train_X.shape[0], 1, train_X.shape[1]))
        test_X = np.reshape(test_X, (test_X.shape[0], 1, test_X.shape[1]))
        return train_X, test_X
    
    @staticmethod
    def tidy_df(df):
        df_proc = df.copy()
        for i in range (0,len(df)):
                df.loc[i,'date']= pd.to_datetime(pd.to_datetime(df.loc[i,'date']) + pd.Timedelta(hours=int(df.loc[i,'period'])))
        df_proc['date'] = pd.DatetimeIndex(df['date'])
        df_proc.drop(columns=['period'], inplace = True)
        df_proc.set_index('date', inplace = True)
        df_proc.resample('W').mean()
        df_proc.fillna(df.mean())
        return df_proc  
    
    @staticmethod
    def plot(df, pred = False):
        plt.figure(figsize=(15,12))
        plt.style.use('fivethirtyeight')
        if pred == True:
            df.plot()
        else:
            df.plot(y='price')
        plt.legend()
        plt.title("Clearning Price")
        plt.ylabel('Clear out price')
        plt.show() 
