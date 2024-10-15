import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
# from schedule import every, repeat, run_pending

# Read the CSV file into a DataFrame
# df = pd.read_csv('valid_tickers.csv')
# sm = df[df[' market_cap'] == " HKD"]['validity']
df = pd.read_csv('hk_tickers.csv')
sm = df

# print(sm)

option = st.selectbox(
    "Stock: ",
    sm['Name'] +  " ( " + sm['Symbol'] + " )",
    index=None,
    placeholder="Select Stock...",
)


st.write("You selected:", option)


if(option != None):
    symbol_option = df[df['Name'] == (option.split(" (")[0])]['Symbol'].iloc[0]
    stock = yf.Ticker(symbol_option)

    time_placeholder = st.empty()

    interval_option = st.selectbox(
        "Interval: ",
        ["Daily","Hourly"],
    )

    # interval_placeholder = st.empty()
    if interval_option == "Hourly":
        closep_stock = stock.history(interval='1h', period='5d')
    else:
        closep_stock = stock.history(interval='1d', period='2y')
    fig = go.Figure(data=[go.Candlestick(x=closep_stock.index,
                                    open=closep_stock['Open'],
                                    high=closep_stock['High'],
                                    low=closep_stock['Low'],
                                    close=closep_stock['Close'])])
    fig.update_layout(title=f'Candle Stick of {option}', xaxis_rangeslider_visible=True)
    # closep_stock
    st.plotly_chart(fig)

    def get_current_value(symbol):
        stock = yf.Ticker(symbol)
        todayData = stock.history(period='1d')
        stock_value = todayData['Close'].iloc[0]
        return round(stock_value, 4)

    while True:
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        # Fetch the data
        stock_data = yf.Ticker(symbol_option)
        historical_data = stock_data.history(period='5d')  # Get the last 5 days of data

        # Extract the closing price for yesterday
        yesterday_close = historical_data['Close'].iloc[-2] 
        current_value = get_current_value(symbol_option)
        time_placeholder.metric(label="Latest Transaction Price", value=current_value, delta=str(round((current_value-yesterday_close)/yesterday_close*100, 2))+ "%", help="Update per minute.")
        # if interval_option == "Hourly":
        #     closep_stock = stock.history(interval='1h', period='5d')
        # else:
        #     closep_stock = stock.history(interval='1d', period='2y')
        # fig = go.Figure(data=[go.Candlestick(x=closep_stock.index,
        #                                 open=closep_stock['Open'],
        #                                 high=closep_stock['High'],
        #                                 low=closep_stock['Low'],
        #                                 close=closep_stock['Close'])])
        # fig.update_layout(title=f'Candle Stick of {option}', xaxis_rangeslider_visible=True)
        # closep_stock
        # interval_placeholder.plotly_chart(fig)
        time.sleep(60)  # Wait for 1 second

    