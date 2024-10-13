import streamlit as st
import sqlite3
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime 

def sma_cross(symbol_option):
    stock = yf.Ticker(symbol_option)
    closep_stock = stock.history(period="2y")

    # Calculate moving averages
    short_window = 20
    long_window = 100

    closep_stock['MA_Short'] = closep_stock['Close'].rolling(window=short_window).mean()
    closep_stock['MA_Long'] = closep_stock['Close'].rolling(window=long_window).mean()

    # Identify crosses
    closep_stock['Cross'] = np.where(closep_stock['MA_Short'] > closep_stock['MA_Long'], 1, 0)
    closep_stock['Signal'] = closep_stock['Cross'].diff()

    # Create a list to store cross points
    cross_points = []

    # Loop to collect cross points
    for i in range(1, len(closep_stock)):
        if closep_stock['Signal'].iloc[i] == 1 and closep_stock['Signal'].iloc[i-1] == 0:
            cross_points.append((closep_stock.index[i], closep_stock['Close'].iloc[i], 'up'))
        elif closep_stock['Signal'].iloc[i] == -1 and closep_stock['Signal'].iloc[i-1] == 0:
            cross_points.append((closep_stock.index[i], closep_stock['Close'].iloc[i], 'down'))
    return cross_points

def rsi_over(symbol_option):
    stock = yf.Ticker(symbol_option)
    closep_stock = stock.history(period="2y")
    change = closep_stock["Close"].diff()
    change.dropna(inplace=True)
    # Create two copies of the Closing price Series
    change_up = change.copy()
    change_down = change.copy()

    #
    change_up[change_up<0] = 0
    change_down[change_down>0] = 0

    # Verify that we did not make any mistakes
    change.equals(change_up+change_down)

    # Calculate the rolling average of average up and average down
    avg_up = change_up.rolling(14).mean()
    avg_down = change_down.rolling(14).mean().abs()

    rsi = 100 * avg_up / (avg_up + avg_down)
    rsi = rsi.sort_index()
        # Initialize lists to store overbought and oversold dates
    overbought_dates = []
    oversold_dates = []

    # Loop through the RSI DataFrame to check conditions
    for index, row in rsi.items():
        # st.write(index)
        if row > 70:
            overbought_dates.append(datetime.fromisoformat(str(index)).strftime('%Y-%m-%d'))
        elif row < 30:
            oversold_dates.append(datetime.fromisoformat(str(index)).strftime('%Y-%m-%d'))

    return overbought_dates, oversold_dates

