from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.callbacks import EarlyStopping

# This python file will process the data and train it.
# No prediction will be done in here

WINDOW_SIZE = 10
scaler = MinMaxScaler(feature_range=(0, 1))  # set values between 0 and 1


def data_loader(filename):
    df = pd.read_csv(filename)  # TODO make so user can choose csv
    df['Date'] = pd.to_datetime(df['Date'])
    dataset = list(zip(df['Date'], df['Adj Close'].values))

    return df, dataset


def train_test_split(df, dataset):
    trainingRange = int(len(dataset) - 20)
    print("The training range is", trainingRange)
    train = df['Adj Close'].iloc[:trainingRange].values
    test = df['Adj Close'].iloc[trainingRange:].values
    train = np.reshape(train, (-1, 1))
    test = np.reshape(test, (-1, 1))

    return train, test


def data_scaler(train, test):
    train_scaled = scaler.fit_transform(train)
    test_scaled = scaler.transform(test)

    return train_scaled, test_scaled


def to_sequences(data, window_size):
    x = []
    y = []

    for i in range(len(data) - window_size - 1):
        window = data[i:(i + window_size), 0]
        x.append(window)
        y.append(data[i + window_size, 0])
    return np.array(x), np.array(y)


def generate_sets(train_scaled, test_scaled):
    X_train, Y_train = to_sequences(train_scaled, WINDOW_SIZE)
    X_test, Y_test = to_sequences(test_scaled, WINDOW_SIZE)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    print(X_test)
    print("=============================================================")
    print(f"X_trains shape is {X_train.shape} ; Y_Trains shape is {Y_train.shape}")
    print(f"X_tests shape is {X_test.shape} ; Y_Tests shape is {Y_test.shape}")
    print("================================================================================")
    print(X_train.shape, Y_train.shape)

    return X_train, Y_train, X_test, Y_test


def build_model(X_train, Y_train):
    model = Sequential()
    model.add(LSTM(64, input_shape=(X_train.shape[1], 1), return_sequences=True, activation='relu'))
    model.add(Dropout(.2))
    model.add(LSTM(32))
    model.add(Dropout(.2))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])  # adagrad?
    monitor = EarlyStopping(monitor='loss', patience=10, verbose=1, restore_best_weights=True)
    model.fit(X_train, Y_train, callbacks=[monitor], epochs=200)

    return model


def save_model(model):
    # TODO implement model saving
    return model


def graph_format(dataset, train_predict, test_predict):
    train_predict = scaler.inverse_transform(train_predict)
    test_predict = scaler.inverse_transform(test_predict)
    train_predict_plot = np.empty_like(dataset)
    train_predict_plot[:, :] = np.nan
    train_predict_plot[WINDOW_SIZE:len(train_predict) + WINDOW_SIZE, :] = train_predict

    test_predict_plot = np.empty_like(dataset)
    test_predict_plot[:, :] = np.nan
    test_predict_plot[len(train_predict) + (WINDOW_SIZE * 2) + 1: len(dataset) - 1, :] = test_predict

    return train_predict_plot, test_predict_plot


def graph_data(df, train_predict_plot, test_predict_plot):
    plt.title("Stocks for TSLA")

    print(f"Test predict plots shape is {test_predict_plot.shape}")
    plt.plot(df['Date'], train_predict_plot, "-b", label="Train predict")
    plt.plot(df['Date'], test_predict_plot, "-y", label="Test predict")
    plt.plot(df['Date'], df['Adj Close'], "-g", label="Original")
    plt.xlabel('Date')
    plt.ylabel('Adj Close Price')
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig('imgFile.png')

