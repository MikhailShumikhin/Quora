"""
NN baseline model
layers:
    1. embedding layer (no-pretrain)
    2. bidirectional_lstm
    3. global_max_pooling1d
    4. dense
    5. output (sigmoid)
"""
import os
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import (Input, Embedding, Bidirectional,
                          LSTM, GlobalMaxPool1D, Dense)
from keras.models import Model

from neural_networks import NeuralNetworkClassifier
from nlp import preprocess
from tqdm import tqdm
tqdm.pandas()


# # toy configs
# MAX_FEATURES = int(5e3)
# MAX_LEN = 20
# EMBED_SIZE = 30
# LSTM_UNITS = 16
# DENSE_UNITS = 4

# model configs
MAX_FEATURES = int(1.5e5)  # total word count = 227,538; clean word count = 186,551   # noqa
MAX_LEN = 65    # mean_len = 12; Q99_len = 40; max_len = 189;
EMBED_SIZE = 300
LSTM_UNITS = 64
DENSE_UNITS = 16

# file configs
MODEL_FILEPATH = os.path.join(
    os.environ['DATA_PATH'],
    'models',
    'model_v2.hdf5'
)


def get_network():
    input_layer = Input(shape=(MAX_LEN, ), name='input')
    # 1. embedding layer (no-pretrain)
    x = Embedding(
        input_dim=MAX_FEATURES,
        output_dim=EMBED_SIZE,
        name='embedding'
    )(input_layer)
    # 2. bidirectional_lstm
    x = Bidirectional(
        layer=LSTM(LSTM_UNITS, return_sequences=True),
        name='bidirectional_lstm'
    )(x)
    # 3. global_max_pooling1d
    x = GlobalMaxPool1D(name='global_max_pooling1d')(x)
    # 4. dense
    x = Dense(units=DENSE_UNITS, activation='relu', name='dense')(x)
    # 5. output (sigmoid)
    output_layer = Dense(units=1, activation='sigmoid', name='output')(x)
    return Model(inputs=input_layer, outputs=output_layer)


def get_model():
    model = get_network()
    print('build network ......')
    print(model.summary())
    return NeuralNetworkClassifier(
        model,
        balancing_class_weight=False,
        filepath=MODEL_FILEPATH)


def transform(df_text):
    # preprocess
    df_text = df_text.progress_apply(preprocess)
    # tokenize the sentences
    tokenizer = Tokenizer(num_words=MAX_FEATURES)
    tokenizer.fit_on_texts(list(df_text))
    X = tokenizer.texts_to_sequences(df_text)

    # pad the sentences
    X = pad_sequences(X, maxlen=MAX_LEN)
    return X
