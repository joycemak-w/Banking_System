import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import yfinance as yf
from schedule import every, repeat, run_pending
import time
import pandas as pd


conn = sqlite3.connect('banking_system.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username = ?", (st.session_state.user,))
user_info = c.fetchone()

# st.write(st.session_state.user)
# st.subheader(f"Welcome, {st.session_state.user}!")

tab1, tab2 = st.tabs(["Balance Overview", "Cash Flow Overview"])
with tab1:
    st.subheader("Balance Overview")
    st.markdown("Current Gain / Loss in stocks", help="Refresh per minute.")
    current_gain_loss_placeholder = st.empty()

    st.markdown("Total Assets", help="Refresh per minute.")
    total_assets_placeholder = st.empty()

    # st.markdown("Total Gain / Loss in selling stocks")
    # c.execute("SELECT symbol, SUM(volume*price) AS total_amount FROM stock_record WHERE user_id = ? and volume < 0 group by symbol", (user_info[0],))
    # total_amount = pd.DataFrame(c.fetchall()).set_index(0)
    # st.write(total_amount)
    # fig=st.bar_chart(total_amount, horizontal=True)

with tab2:
    st.subheader("Cash Flow Overview")
    # st.table(df)

    query = f"""
    SELECT date, SUM(amount) AS total_amount
    FROM balance_record
    WHERE user_id = {user_info[0] }
    GROUP BY date
    ORDER BY date
    """
    # Read data into a DataFrame
    df_line_chart = pd.read_sql_query(query, conn)

    # Convert date column to datetime
    df_line_chart['date'] = pd.to_datetime(df_line_chart['date'])

    # Create a cumulative sum to plot the balance over time
    df_line_chart['cumulative_amount'] = df_line_chart['total_amount'].cumsum()

    # Streamlit line chart
    st.markdown("Cash Flow Over Time")

    df_line_chart.set_index('date', inplace=True)

    st.line_chart(df_line_chart['cumulative_amount'])

    query = "SELECT id as balance_id, reason, amount, date FROM balance_record WHERE user_id = '%s'" % user_info[0] 
    df_all = pd.read_sql(query, conn)
    st.dataframe(df_all, hide_index=True)

    query = f"""
    SELECT
        SUM(CASE WHEN reason = 'Deposit' then amount else 0 end) as deposit,
        SUM(CASE WHEN reason LIKE 'Sell%' then amount else 0 end) as sell_stock,
        SUM(CASE WHEN reason LIKE 'Interest' then amount else 0 end) as interest,
        SUM(CASE WHEN reason = 'Withdrawal' then amount else 0 end) as withdrawal,
        SUM(CASE WHEN reason LIKE 'Buy%' then amount else 0 end) as buy_stock
    FROM balance_record
    WHERE user_id = {user_info[0]} 
    """
    # Read data into a DataFrame
    df_pie_chart = pd.read_sql_query(query, conn)
    # st.write(df_pie_chart.iloc[0][:2].index)
    pie_column1, pie_column2 = st.columns([1,1])
    with pie_column1:
        # st.markdown("Increasement")
        fig=go.Figure()
        fig.add_trace(go.Pie(labels=df_pie_chart.iloc[0][:3].index, values=df_pie_chart.iloc[0][:3].values, marker=dict(colors=['#156b39', 'green', '#03fcb1']), textposition='inside',sort=False, direction='clockwise', textinfo='label+value+percent'))
        fig.update_layout(title = "Increasement in cash")
        st.plotly_chart(fig, key="increase") 
    with pie_column2:
        # st.markdown("Decreasement")
        fig=go.Figure()
        fig.add_trace(go.Pie(labels=df_pie_chart.iloc[0][3:5].index, values=-df_pie_chart.iloc[0][3:5].values, marker=dict(colors=['red', '#e88780']), textposition='inside', sort=False, direction='clockwise', textinfo='label+value+percent'))
        fig.update_layout(title = "Decreasement in cash")
        st.plotly_chart(fig, key="decrease") 

    # query = f"""
    # SELECT
    #     SUM(CASE WHEN volume >= 0 then volume*price else 0 end) as p_value,
    #     SUM(CASE WHEN volume < 0 then volume*price else 0 end) as n_value
    # FROM stock_record
    # WHERE user_id = {user_info[0]} 
    # """
    # # Read data into a DataFrame
    # df_gain_loss_chart = pd.read_sql_query(query, conn)

    # fig=go.Figure()
    # values = df_gain_loss_chart.iloc[0].values
    # max_value = max(abs(min(values)), abs(max(values)))
    # colors = ['green' if v < 0 else 'red' for v in values]
    # fig.add_trace(go.Bar(
    #     x=-values,  # Individual values
    #     y=['Loss/Gain'] * len(values),  # Same label for all sections
    #     orientation='h',
    #     customdata=-values,  # Adjust customdata accordingly
    #     hovertemplate="$%{customdata}<extra></extra>",
    #     marker_color=colors  # Set colors based on value
    # ))
    # fig.update_layout(
    #     title='Loss / Gain on stock trading',
    #     barmode='relative',
    #     height=400,
    #     width=700,
    #     yaxis_autorange='reversed',
    #     bargap=0.5,
    #     legend_orientation='v',
    #     legend_x=1,
    #     legend_y=0,
    #     xaxis=dict(
    #         range=[-max_value, max_value],  # Set x-axis range to center 0
    #         zeroline=True,  # Add a line at x=0
    #         zerolinewidth=2  # Width of the zero line
    #     )
    # )
    # fig.update_xaxes(title_text = "HKD ($)", )
    # st.plotly_chart(fig) 


    query = f"""
    SELECT
        symbol,
        SUM(price*volume) as total,
        SUM(volume) as volume
    FROM stock_record
    WHERE user_id = {user_info[0]} 
    GROUP BY symbol
    """
    df_current_gain_loss = pd.read_sql_query(query, conn)
    df_current_gain_loss = df_current_gain_loss.set_index('symbol')
    # st.write(df_current_gain_loss)

def get_current_value(symbol):
    stock = yf.Ticker(symbol)
    # stock.info.get('currentPrice')
    todayData = stock.history(period='1d')
    if todayData.empty:
        return 0
    else:
        stock_value = todayData['Close'].iloc[0]
        return round(stock_value, 2)
        

while True:
    query = f"""
    SELECT
        SUM(CASE WHEN reason = 'Deposit' then amount else 0 end) as deposit,
        SUM(CASE WHEN reason LIKE 'Interest' then amount else 0 end) as interest
    FROM balance_record
    WHERE user_id = {user_info[0]} 
    """
    # Read data into a DataFrame
    cash = pd.read_sql_query(query, conn)
    totalvalue = 0
    for symbol_option in df_current_gain_loss.index:
        if df_current_gain_loss.loc[symbol_option, 'volume'] != 0:
            if symbol_option != 'Total':
                df_current_gain_loss.loc[symbol_option, 'p_price'] = round(df_current_gain_loss.loc[symbol_option, 'total'] / df_current_gain_loss.loc[symbol_option, 'volume'], 2)
                current_price = get_current_value(symbol_option)
                df_current_gain_loss.loc[symbol_option, 'c_price'] = current_price
                cash.loc[0, symbol_option] = round(current_price * df_current_gain_loss.loc[symbol_option, 'volume'], 2)
                df_current_gain_loss.loc[symbol_option, 'gain / loss (%)'] = str(round((df_current_gain_loss.loc[symbol_option,'c_price'] - df_current_gain_loss.loc[symbol_option, 'p_price']) / df_current_gain_loss.loc[symbol_option, 'p_price']*100,2)) + "%"
                actualvalue = round(df_current_gain_loss.loc[symbol_option,'c_price'] * df_current_gain_loss.loc[symbol_option,'volume'] - df_current_gain_loss.loc[symbol_option,'total'], 2)
                df_current_gain_loss.loc[symbol_option, 'gain / loss ($)'] = actualvalue
                totalvalue += actualvalue
        else:
            df_current_gain_loss.drop(symbol_option)
    df_current_gain_loss.loc['Total', 'gain / loss ($)'] = totalvalue 
    current_gain_loss_placeholder.dataframe(df_current_gain_loss, key="gain_loss")

    fig=go.Figure()
    fig.add_trace(go.Pie(labels=cash.columns, values=cash.iloc[0].tolist(), textposition='auto', sort=False, textinfo='label+percent'))
    # fig.update_layout(title = "Total Assets")
    # st.plotly_chart(fig)
    total_assets_placeholder.plotly_chart(fig) 
    # total_assets_placeholder.write(cash.values)
    
    # closep_stock = yf.Ticker("1810.HK").history(interval='1d', period='2y')
    # fig = go.Figure(data=[go.Candlestick(x=closep_stock.index,
    #                                 open=closep_stock['Open'],
    #                                 high=closep_stock['High'],
    #                                 low=closep_stock['Low'],
    #                                 close=closep_stock['Close'])])
    # # closep_stock
    # total_assets_placeholder.plotly_chart(fig)

    time.sleep(60)  # Wait for 60 second

