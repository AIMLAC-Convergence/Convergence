import numpy as np
import keras
from sklearn.preprocessing import MinMaxScaler
import logging

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler=logging.FileHandler('auto_bidder.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class Predictor:
    def __init__(self, model, input_data):
        self._model = model                #path to model dir
        self._input_data = input_data 

    def predict(self):
        scaler = MinMaxScaler(feature_range=(0, 1))
        logger.info("---CHECKPOINT: Compiling model with TensorFlow backend---")
        reconstructed_model = keras.models.load_model(self._model)
        reconstructed_model.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
        try:
           data = np.array(self._input_data).reshape(24,1,1)
        except ValueError:
           logger.exception(f"{ValueError(self._input_data.shape)}, have to be able to reshape data to: {24,1,1}")
        else:
            data = scaler.fit_transform(data.reshape(-1,1))
            pred = scaler.inverse_transform(reconstructed_model.predict(data.reshape(-1,1,1)))
            return pred