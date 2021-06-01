from collections import defaultdict
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from keras_preprocessing import sequence

import tensorflow as tf
from keras.models import load_model

from decimal import Decimal

import io


SEQLEN = 100  # define length of sequences -> timesteps

label_encoder = LabelEncoder()
label_encoder.classes_ = np.load('classes.npy', allow_pickle=True)

class ModelEval:
    def __init__(self, model_name="lstm_ints_3"):
        self.model = load_model(model_name)

    def evaluate(self, csv_data):
        data = io.StringIO(csv_data)

        array_of_sequences = self.col_to_array(
            data, "template"
        )  # template is the column of interest in the csv

        encoded_sequences = self.encode_sequences(
            encoder=label_encoder, array_of_sequences=array_of_sequences
        )

        windowed_sequences = np.array(self.subsequences(encoded_sequences, SEQLEN))

        padded_sequences = sequence.pad_sequences(
            windowed_sequences, maxlen=SEQLEN, padding="post"
        )

        reshaped_sequences = self.reshape_inputs(padded_sequences)
        reshaped_sequences = tf.cast(reshaped_sequences, tf.float32)

        prediction = self.model.predict(reshaped_sequences)
        y_class_predict = [x for x in prediction]
        max_arg_prediction = [int(x) for x in np.argmax(prediction, axis=-1)]

        predictions = self._group_max_arg_predictions(max_arg_prediction)
        return {
            "predictions": self._predictions_map(predictions),
            "sequences": max_arg_prediction
        }

    def _group_predictions(self, class_predict):
        res = {
            "normal": 0,
            "machine_down": 0,
            "disk_full":0,
            "network_disconnect": 0,
        }
        for predict_array in class_predict:
            res["normal"] += predict_array[0]
            res["machine_down"] += predict_array[1]
            res["disk_full"] += predict_array[2]
            res["network_disconnect"] += predict_array[3]
        return res

    def _group_max_arg_predictions(self, class_predict):
        res = defaultdict(int)
        for prediction in class_predict:
            res[prediction] += 1
        return {
            "normal": res[0],
            "machine_down": res[1],
            "disk_full": res[2],
            "network_disconnect": res[3],
        }

    def _predictions_map(self, predictions):
        summ = sum(x for x in predictions.values())
        return {
            k: Decimal(str(v/summ)) for k, v in predictions.items()
        }

    def col_to_array(self, file, column_name):
        df = pd.read_csv(file)  # put csv into dataframe format
        return df[
            column_name
        ].to_numpy()  # extract the selected column -> for the log templates: "templates"

    def encode_sequences(self, encoder, array_of_sequences):
        return [y for y in encoder.fit_transform(array_of_sequences).flat]

    def subsequences(self, seq, window):
        seq = np.array(seq)
        shape = (max(seq.size - window + 1, window), window)
        strides = seq.strides * 2
        return np.lib.stride_tricks.as_strided(seq, shape=shape, strides=strides)

    def reshape_inputs(self, array):
        flat = np.array(array).reshape(-1)
        return np.array(flat).reshape((len(array), SEQLEN, 1))


if __name__ == "__main__":
    pass
    # file = "/app/container_1445144423722_0022_01_000001.csv"

    # array_of_sequences = col_to_array(
    #     file, "template"
    # )  # template is the column of interest in the csv
    # encoded_sequences = encode_sequences(
    #     encoder=label_encoder, array_of_sequences=array_of_sequences
    # )
    # print(encoded_sequences[:10], len(encoded_sequences))
    # windowed_sequences = np.array(
    #     subsequences(encoded_sequences, SEQLEN)
    # )
    # padded_sequences = sequence.pad_sequences(
    #     windowed_sequences, maxlen=SEQLEN, padding="post"
    # )
    # print(len(padded_sequences[0]))
    # print(len(padded_sequences))

    # reshaped_sequences = reshape_inputs(padded_sequences)
    # print(reshaped_sequences.shape)

    # reshaped_sequences = tf.cast(reshaped_sequences, tf.float32)
    # print(reshaped_sequences.shape)

    # model = load_model('lstm_ints_1')

    # #classify input sequences (X)
    # # y_predict = model.predict(reshaped_sequences)
    # #or
    # y_class_predict = np.argmax(model.predict(reshaped_sequences), axis=-1)
    # print(y_class_predict)
    # print([x for x in y_class_predict if x != 1])
