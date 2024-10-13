import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, timedelta, datetime
import yfinance as yf
import math
from schedule import every, repeat, run_pending
import time
# import numpy as np
# import plotly.graph_objects as go

# Read the CSV file into a DataFrame
# df = pd.read_csv('valid_tickers.csv')
# sm = df[df[' market_cap'] == " HKD"]['validity']
df = pd.read_csv('hk_tickers.csv')
sm = df

# print(sm)

col1, col2= st.columns([2,1])
with col1:
    stock_option = st.selectbox(
        "Stock: ",
        sm['Name'] +  " ( " + sm['Symbol'] + " )",
        placeholder="Select Stock...",
    )
with col2:
    # Create a placeholder for the current time
    time_placeholder = st.empty()

# st.write("You selected:", stock_option)

option = st.selectbox(
    "Buy / Sell Stock: ",
    ("Buy","Sell"),
)

st.subheader(option + " " + stock_option)

conn = sqlite3.connect('banking_system.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username = ?", (st.session_state.user,))
user_info = c.fetchone()

def get_current_value(symbol):
    stock = yf.Ticker(symbol)
    # stock.info.get('currentPrice')
    todayData = stock.history(period='1d')
    stock_value = todayData['Close'].iloc[0]
    return round(stock_value, 4)
    # total_value = round(stock_value*volume, 2)
    # return total_value

volume = st.number_input(option + " Volume: ", min_value=100, value=100)
formatted_date = date.today().strftime('%Y-%m-%d')
symbol_option = df[df['Name'] == (stock_option.split(" ")[0])]['Symbol'].iloc[0]
stock_current_price = get_current_value(symbol_option)
# stock_current_value = round(get_current_value(symbol_option) * volume, 2)
stock_current_value = math.ceil((stock_current_price * volume) * 100) / 100
if st.button("Confirm", key='d_confirm'):
    if stock_option != None:
        if option == "Buy":
            if volume >= 100:
                c.execute("SELECT SUM(amount) FROM balance_record WHERE user_id = ?", (user_info[0],))
                total_amount = c.fetchone()[0]
                if total_amount >= volume * stock_current_price:
                    c.execute("INSERT INTO stock_record (user_id, symbol, volume, price, date) VALUES (?, ?, ?, ?, ?)", 
                            (user_info[0], stock_option, volume, stock_current_value, formatted_date))
                    c.execute("INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)", 
                            (user_info[0], f'Buy {stock_option}', -stock_current_value, formatted_date))
                    conn.commit()
                    st.success(f"Buy " + str(volume) + " of " + stock_option + "successfully!")
                else:
                    st.error(f"Your bank account do not have enough balance.")
            else:
                st.error(f"Volume should be larger than or equal to 100.")
        elif option == "Sell":
            if volume >= 100:
                c.execute("SELECT SUM(volume) FROM stock_record WHERE user_id = ? AND symbol = ?", (user_info[0], stock_option,))
                total_volume = c.fetchone()[0]
                if total_volume >= volume:
                    c.execute("INSERT INTO stock_record (user_id, symbol, volume, price, date) VALUES (?, ?, ?, ?, ?)", 
                            (user_info[0], stock_option, -volume, stock_current_price, formatted_date))
                    c.execute("INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)", 
                            (user_info[0], f'Sell {stock_option}', (volume * stock_current_price), formatted_date))
                    conn.commit()
                    st.success(f"Sell " + str(volume) + " of " + stock_option + "successfully!")
                else:
                    st.error(f"Your selected volume {str(volume)} is larger than your owned volume {str(total_volume)}.")
            else:
                st.error(f"Volume should be larger than or equal to 100.")
    else:
        st.error(f"You should select a stock.")
# Update the time every second
while True:
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    # Fetch the data
    stock_data = yf.Ticker(symbol_option)
    historical_data = stock_data.history(period='5d')  # Get the last two days of data

    # Extract the closing price for yesterday
    yesterday_close = historical_data['Close'].iloc[-2] 
    current_value = get_current_value(symbol_option)
    time_placeholder.metric(label="Latest Transaction Price", value=current_value, delta=str(round((current_value-yesterday_close)/yesterday_close*100, 2))+ "%")
    # time_placeholder.text(f"Latest Transaction Price: {current_value}")
    time.sleep(60)  # Wait for 1 second

