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

def correlation(symbol_options):
    hsi_df = pd.read_csv('hang_seng_index.csv')
    hsi_sm = hsi_df['Symbol'].to_list()

    for symbol_option in symbol_options:
        if symbol_option not in hsi_sm:
            hsi_sm.append(symbol_option)

    # Initialize an empty DataFrame to store successful downloads
    hsi_data = pd.DataFrame()

    # Fetch historical stock data, ignoring stocks that fail to download
    for symbol in hsi_sm:
        try:
            stock_data = yf.download(symbol, period='2y')['Adj Close']
            if not stock_data.empty:
                hsi_data[symbol] = stock_data
        except Exception as e:
            print(f"Failed to download data for {symbol}: {e}")

    # Drop rows with missing values
    hsi_data.dropna(inplace=True)

    # Calculate correlation with search_s
    strong_positive_correlation = {}
    strong_negative_correlation = {}
    strong_correlation = {}
    
    for symbol_option in symbol_options:
        correlation_series = hsi_data.corr()[symbol_option]
        strong_positive_correlation[symbol_option] = correlation_series[correlation_series >= 0.8]
        strong_negative_correlation[symbol_option] = correlation_series[correlation_series <= -0.8]

    return strong_positive_correlation, strong_negative_correlation

# Example usage
symbol_list = ['0005.HK', '0700.HK']
p, n = correlation(symbol_list)
st.write(p.get('0005.HK', 'No strong positive correlations'))
st.write(n.get('0005.HK', 'No strong negative correlations'))