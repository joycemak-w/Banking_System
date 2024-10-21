import streamlit as st
import sqlite3
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, date, timedelta
import pytz

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
        if datetime.fromisoformat(str(closep_stock.index[i])).date() >= date.today() - timedelta(days=30):
            if closep_stock['Signal'].iloc[i] == 1 and closep_stock['Signal'].iloc[i-1] == 0:
                cross_points.append((closep_stock.index[i], closep_stock['Close'].iloc[i], 'up'))
            elif closep_stock['Signal'].iloc[i] == -1 and closep_stock['Signal'].iloc[i-1] == 0:
                cross_points.append((closep_stock.index[i], closep_stock['Close'].iloc[i], 'down'))
    if cross_points != []:
        return cross_points[-1]
    else:
        pass

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
    # overbought_dates = []
    # oversold_dates = []
    over_dates = []

    # Loop through the RSI DataFrame to check conditions
    for index, row in rsi.items():
        if datetime.fromisoformat(str(index)).date() >= date.today() - timedelta(days=30):
            if row > 70:
                over_dates.append((datetime.fromisoformat(str(index)).date(),'overbought'))
            if row < 30:
                over_dates.append((datetime.fromisoformat(str(index)).date(),'oversold'))
    if over_dates != []:
        return over_dates[-1]
    else:
        pass
    # return over_dates

# def correlation(symbol_options):
#     hsi_df = pd.read_csv('hang_seng_index.csv')
#     hsi_sm = hsi_df['Symbol'].to_list()

#     for symbol_option in symbol_options:
#         if symbol_option not in hsi_sm:
#             hsi_sm.append(symbol_option)

#     # Initialize an empty DataFrame to store successful downloads
#     hsi_data = pd.DataFrame()

#     # Fetch historical stock data, ignoring stocks that fail to download
#     for symbol in hsi_sm:
#         try:
#             stock_data = yf.download(symbol, period='1mo')['Adj Close']
#             if not stock_data.empty:
#                 hsi_data[symbol] = stock_data
#         except Exception as e:
#             print(f"Failed to download data for {symbol}: {e}")

#     # Drop rows with missing values
#     hsi_data.dropna(inplace=True)

#     # Calculate correlation with search_s
#     strong_positive_correlation = {}
#     strong_negative_correlation = {}
#     strong_correlation = {}
    
#     for symbol_option in symbol_options:
#         correlation_series = hsi_data.corr()[symbol_option]
#         strong_positive_correlation[symbol_option] = correlation_series[correlation_series >= 0.8]
#         strong_negative_correlation[symbol_option] = correlation_series[correlation_series <= -0.8]

#     return strong_positive_correlation, strong_negative_correlation

def correlation_a(symbol_options):
    hsi_df = pd.read_csv('hang_seng_index.csv')
    hsi_sm = hsi_df['Symbol'].to_list()

    for symbol_option in symbol_options:
        if symbol_option not in hsi_sm:
            hsi_sm.append(symbol_option)

    hsi_data = pd.DataFrame()

    # Fetch historical stock data, ignoring stocks that fail to download
    for symbol in hsi_sm:
        try:
            stock_data = yf.download(symbol, period='2y')['Adj Close']
            if not stock_data.empty:
                hsi_data[symbol] = stock_data
        except Exception as e:
            print(f"Failed to download data for {symbol}: {e}")

    hsi_data.dropna(inplace=True)

    strong_correlation = {}
    
    for symbol_option in symbol_options:
        strong_correlation[symbol_option] = {'positive': [], 'negative': []}
        if symbol_option in hsi_data.columns:
            correlation_series = hsi_data.corr()[symbol_option]
            strong_correlation[symbol_option]['positive'] = correlation_series[correlation_series >= 0.8].index.tolist()
            strong_correlation[symbol_option]['negative'] = correlation_series[correlation_series <= -0.8].index.tolist()

    return strong_correlation

symbol_list = ['0388.HK', '0700.HK']
conn = sqlite3.connect('banking_system.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username = ?", (st.session_state.user,))
user_info = c.fetchone()
query = """
SELECT DISTINCT r.symbol, r.date
FROM stock_record r
JOIN (
    SELECT symbol, MAX(date) AS latest_date
    FROM stock_record
    WHERE user_id = ?
    GROUP BY symbol
) AS latest_records ON r.symbol = latest_records.symbol AND r.date = latest_records.latest_date
WHERE r.user_id = ? ORDER BY r.date desc
"""
df_user_symbol = pd.read_sql(query, conn, params=(user_info[0],user_info[0]))
sm = pd.read_csv('hk_tickers.csv')
# st.write(df_user_symbol)
symbol_list = df_user_symbol['symbol']
name_list = {}
for s in symbol_list:
    name_list[s] = sm[sm['Symbol']==s]['Name']
# st.write(name_list['2318.HK'].iloc[0])
# for s in df_user_symbol['symbol']:
#     symbol_list.append(s)
with st.spinner(text="Loading the notifications..."):
    # p, n = correlation(symbol_list)
    # st.write(p.get('0388.HK', 'No strong positive correlations'))
    # st.write(n.get('0388.HK', 'No strong negative correlations'))
    correlation_results = correlation_a(symbol_list)
    for symbol_option, correlations in correlation_results.items():
        # st.write(correlations)
        sma_user_stock = sma_cross(symbol_option)
        rsi_user_stock = rsi_over(symbol_option)
        if sma_user_stock is not None or rsi_user_stock is not None:
            st.subheader(f"{name_list[symbol_option].iloc[0]} ({symbol_option})")
            if sma_user_stock is not None:
                if sma_user_stock[2] == 'up':
                    st.write(f":green[**{symbol_option}** may increase] as there is a golden cross on {datetime.fromisoformat(str(sma_user_stock[0])).date()}.")
                elif sma_user_stock[2] == 'down':
                    st.write(f":red[**{symbol_option}** may decrease] as there is a death cross on {datetime.fromisoformat(str(sma_user_stock[0])).date()}.")
            if rsi_user_stock is not None:
                if rsi_user_stock[1] == 'overbought':
                    st.write(f":red[**{symbol_option}** may decrease] as there is overbought on {rsi_user_stock[0]}.")
                elif rsi_user_stock[1] == 'oversold':
                    st.write(f":green[**{symbol_option}** may decrease] as there is oversold on {rsi_user_stock[0]}.")
            # st.write(sma_user_stock)
            # st.write(rsi_user_stock)

            in_de = []
            for correlation in correlations['positive']:
                sma = sma_cross(correlation)
                rsi = rsi_over(correlation)
                if sma is not None:
                    if sma[2] == 'up':
                        in_de.append('in')
                    elif sma[2] == 'down':
                        in_de.append('de')

            for correlation in correlations['negative']:
                sma = sma_cross(correlation)
                rsi = rsi_over(correlation)
                if sma is not None:
                    if sma[2] == 'down':
                        in_de.append('in')
                    elif sma[2] == 'up':
                        in_de.append('de')

            # Determine summary message based on in_de
            if in_de:
                if in_de.count('in') / len(in_de) >= 0.7:
                    summary = "Overall related stocks indicate an :green[INCREASE]."
                elif in_de.count('de') / len(in_de) >= 0.7:
                    summary = "Overall related stocks indicate a :red[DECREASE]."
                else:
                    summary = "Low similarity among related stocks."
                with st.expander(summary):
                    # st.write("Positive")
                    for correlation in correlations['positive']:
                        sma  = sma_cross(correlation)
                        rsi = rsi_over(correlation)
                        if sma is not None:
                            # st.write(correlation)
                            # st.write(sma)
                            st.write(f"**{symbol_option}** have a positive correlation with **{correlation}**.")
                            if sma[2] == 'up':
                                st.write(f":green[**{symbol_option}** may increase] as there is a golden cross on {correlation} on {datetime.fromisoformat(str(sma[0])).date() }.")
                            elif sma[2] == 'down':
                                st.write(f":red[**{symbol_option}** may decrease] as there is a death cross on **{correlation}** on {datetime.fromisoformat(str(sma[0])).date() }.")
                            st.markdown('----')
                    # st.write("Negative")
                    for correlation in correlations['negative']:
                        sma  = sma_cross(correlation)
                        rsi = rsi_over(correlation)
                        if sma is not None:
                            # st.write(correlation)
                            # st.write(sma)
                            st.write(f"**{symbol_option}** have a negative correlation with **{correlation}**.")
                            if sma[2] == 'down':
                                st.write(f":green[**{symbol_option}** may increase] due there is death cross on {correlation} on {datetime.fromisoformat(str(sma[0])).date() }.")
                            elif sma[2] == 'up':
                                st.write(f":red[**{symbol_option}** may decrease] due there is golden cross on **{correlation}** on {datetime.fromisoformat(str(sma[0])).date() }.")
                            st.markdown('----')
                
                # summary = ""
                # if in_de.count('in')/ len(in_de) >= 0.7:
                #     # st.write(in_de.count('in')/ len(in_de))
                #     summary = "Overall related stocks cause increasement."
                # elif in_de.count('de')/ len(in_de) >= 0.7:
                #     summary = "Overall related stocks cause decreasement."
                # else:
                #     summary = "Low similarity among related stocks"
                # st.write(summary)
            st.markdown('----')

