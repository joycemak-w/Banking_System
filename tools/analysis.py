import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

# # Read the CSV file into a DataFrame
# df = pd.read_csv('valid_tickers.csv')
# sm = df[df[' market_cap'] == "HKD"]['validity']

# # print(sm)

# option = st.selectbox(
#     "Stock: ",
#     sm,
#     index=None,
#     placeholder="Select Stock...",
# )

# st.write("You selected:", option)
df = pd.read_csv('hk_tickers.csv')
sm = df

# print(sm)

option = st.selectbox(
    "Stock: ",
    sm['Name'] + " ( " + sm['Symbol'] + " )",
    index=None,
    placeholder="Select Stock...",
)

st.write("You selected:", option)


if(option != None):
    symbol_option = df[df['Name'] == (option.split(" (")[0])]['Symbol'].iloc[0]
    name_option = df[df['Name'] == (option.split(" (")[0])]['Name'].iloc[0]
    # st.write(name_option)
    stock = yf.Ticker(symbol_option)
    closep_stock = stock.history(period="2y")
    # # st.dataframe(closep_stock)
    # # st.line_chart(closep_stock['Close'], x_label='Date', y_label='Close Price')

    # # st.subheader("Candle Stick")
    # fig = go.Figure(data=[go.Candlestick(x=closep_stock.index,
    #                                 open=closep_stock['Open'],
    #                                 high=closep_stock['High'],
    #                                 low=closep_stock['Low'],
    #                                 close=closep_stock['Close'])])
    # fig.update_layout(title='Candle Stick', xaxis_rangeslider_visible=True)
    # # closep_stock
    # st.plotly_chart(fig, theme='streamlit')

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

    # Set up the Streamlit app
    # st.subheader("Stock Closing Price and Moving Averages")

    # Plotting SMA
    fig = go.Figure()

    # Add close price line
    fig.add_trace(go.Scatter(x=closep_stock.index, y=closep_stock['Close'], mode='lines', name='Close Price', line=dict(color='blue')))

    # Add short moving average line
    fig.add_trace(go.Scatter(x=closep_stock.index, y=closep_stock['MA_Short'], mode='lines', name=f'{short_window}-Day MA', line=dict(color='orange')))

    # Add long moving average line
    fig.add_trace(go.Scatter(x=closep_stock.index, y=closep_stock['MA_Long'], mode='lines', name=f'{long_window}-Day MA', line=dict(color='green')))

    # Highlight the crosses with dots
    for i, (date, price, direction) in enumerate(cross_points):
        if i != 0:
            if direction == 'up':
                fig.add_trace(go.Scatter(x=[date], y=[price], mode='markers', marker=dict(symbol="triangle-up", color='green', size=10), showlegend=False))
            elif direction == 'down':
                fig.add_trace(go.Scatter(x=[date], y=[price], mode='markers', marker=dict(symbol="triangle-down", color='red', size=10), showlegend=False))

    # Update layout for better readability and scrolling
    fig.update_layout(
        title='Stock Prices and Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=True,
        xaxis_tickformat='%Y-%m-%d',
        hovermode='x unified'
    )

    col_chart, col_cross = st.columns([3,1], vertical_alignment="center")
    with col_chart:
        # Show the plot in Streamlit
        st.plotly_chart(fig)

    # Display cross points in Streamlit (optional)
    if cross_points:
        up = {}
        down = {}
        # st.subheader("Cross Points Detected")
        for date, price, direction in cross_points:
            if direction == 'up':
                # st.write(f"UP **Date:** {date.date()} - **Close Price:** {price:.2f}")
                up[date.date()] = round(price, 2)
            elif direction == 'down':
                # st.write(f"DOWN **Date:** {date.date()} - **Close Price:** {price:.2f}")
                down[date.date()] = round(price, 2)
        up = pd.DataFrame.from_dict(up, orient="index", columns=["Close Price"])
        down = pd.DataFrame.from_dict(down, orient="index", columns=["Close Price"])
        with col_cross:
            st.write(':green[Golden Cross: ]')
            st.dataframe(up)
            st.write(":red[Death Cross: ]")
            st.dataframe(down)
    else:
        st.write("No cross points found.")

    

    # Calculating the RSI
    def get_rsi():
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
        # rsi['2022-09-13 00:00:00+08:00'] = 0.000000
        # rsi.loc[pd.Timestamp('2022-09-13 00:00:00+08:00')] = 0
        # new_row = pd.DataFrame({0: [0.0]}, index=pd.to_datetime(['2022-09-13 00:00:00+08:00']))
        rsi = rsi.sort_index()
        # rsi = rsi.fillna(0)
        return rsi
    
    # Plotting SMA
    fig = go.Figure()
    rsi = get_rsi()
    # st.write(rsi)

    # Add the RSI line
    fig.add_trace(go.Scatter(x=rsi.index, y=rsi, mode='lines', name='RSI'))
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    # Update layout for better readability and scrolling
    fig.update_layout(
        title='Stock Prices and Moving Averages',
        xaxis_title='Date',
        yaxis_title='RSI',
        xaxis_rangeslider_visible=True,
        xaxis_tickformat='%Y-%m-%d',
        hovermode='x unified'
    )

    # Show the plot in Streamlit
    st.plotly_chart(fig)

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

    # # Now you can use these lists as needed
    # st.write("Overbought Dates:", overbought_dates)
    # st.write("Oversold Dates:", oversold_dates)

    def get_date_ranges(dates):
        # Sort the dates
        dates = sorted(set(datetime.fromisoformat(date) for date in dates))
        ranges = []
        
        if not dates:
            return ranges

        # Initialize the first date range
        start_date = dates[0]
        end_date = start_date

        for current_date in dates[1:]:
            # Check if the current date is continuous with the end_date
            if current_date == end_date + timedelta(days=1):
                end_date = current_date  # Extend the range
            else:
                # Save the current range
                ranges.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
                # Start a new range
                start_date = current_date
                end_date = start_date

        # Append the last range
        ranges.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        return ranges
    
    new_names = {0:"Start Date",1:"End Date"}
    overbought = pd.DataFrame(get_date_ranges(overbought_dates)).rename(index=int, columns=new_names)
    oversold = pd.DataFrame(get_date_ranges(oversold_dates)).rename(index=int, columns=new_names)

    col_oversold, col_overbought = st.columns([1,1])
    with col_oversold:
        st.write(":green[Oversold Date Range: ]")
        st.dataframe(oversold, hide_index=True, use_container_width=True)
    with col_overbought:
        st.write(":red[Overbought Date Range: ]")
        st.dataframe(overbought, hide_index=True, use_container_width=True)

    # Load stock symbols from CSV
    hsi_df = pd.read_csv('hang_seng_index.csv')
    hsi_sm = hsi_df['Symbol'].to_list()

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
    correlation = hsi_data.corr()[symbol_option]
    strong_positive_correlation = correlation[correlation >= 0.8]
    strong_negative_correlation = correlation[correlation <= -0.8]
    

    col_positive_correlation, col_negative_correlation = st.columns([1,1])
    with col_positive_correlation:
        st.write(":green[Strongly positive correlated stocks: ]")
        st.dataframe(strong_positive_correlation, use_container_width=True)
    with col_negative_correlation:
        st.write(":red[Strongly negative correlated stocks: ]")
        st.dataframe(strong_negative_correlation, use_container_width=True)
        
        