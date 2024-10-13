import streamlit as st
import sqlite3
import pandas as pd

# st.write(st.session_state.user)
st.subheader(f"Welcome, {st.session_state.user}!")
conn = sqlite3.connect('banking_system.db')
c = conn.cursor()
st.header("Balance Report")
c.execute("SELECT * FROM users WHERE username = ?", (st.session_state.user,))
user_info = c.fetchone()
query = "SELECT id as balance_id, reason, amount, date FROM balance_record WHERE user_id = '%s'" % user_info[0] 
df_all = pd.read_sql(query, conn)
st.dataframe(df_all, hide_index=True)
# st.table(df)
query = f"""
SELECT date, SUM(amount) AS total_amount
FROM balance_record
WHERE user_id = {user_info[0] }
GROUP BY date
ORDER BY date
"""
# Read data into a DataFrame
df_chart = pd.read_sql_query(query, conn)

# Convert date column to datetime
df_chart['date'] = pd.to_datetime(df_chart['date'])

# Create a cumulative sum to plot the balance over time
df_chart['cumulative_amount'] = df_chart['total_amount'].cumsum()

# Streamlit line chart
st.title("Your Balance Over Time")

df_chart.set_index('date', inplace=True)

st.line_chart(df_chart['cumulative_amount'])