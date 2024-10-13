import streamlit as st
import sqlite3
from datetime import date
import pandas as pd



option = st.selectbox(
    "Deposit / Withdrawal: ",
    ("Deposit", "Withdrawal"),
)

st.subheader(option)
conn = sqlite3.connect('banking_system.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username = ?", (st.session_state.user,))
user_info = c.fetchone()
amount = st.number_input(option + " Amount: ")
formatted_date = date.today().strftime('%Y-%m-%d')
if st.button("Confirm", key='d_confirm'):
    if option == "Deposit":
        if amount > 0:
            c.execute("INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)", 
                    (user_info[0], 'Deposit', amount, formatted_date))
            conn.commit()
            st.success(f"Deposit ${str(amount)} successfully!")
        else:
            st.error(f"Deposit should be larger than $0")
    elif option == "Withdrawal":
        if amount > 0:
            c.execute("SELECT SUM(amount) FROM balance_record WHERE user_id = ?", (user_info[0],))
            total_amount = c.fetchone()[0]
            if total_amount < amount:
                c.execute("INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)", 
                        (user_info[0], 'Withdrawal', -amount, formatted_date))
                conn.commit()
                st.success(f"Withdraw ${str(amount)} successfully!")
            else:
                st.error(f"Withdrawal ${str(amount)} is larger than your Deposit(${str(total_amount)}).")
        else:
            st.error(f"Withdrawal should be larger than $0")




# if option == "Deposit":
#     dAmount = st.number_input("Deposit Amount: ")
#     if st.button("Confirm", key='d_confirm'):
#         formatted_date = date.today().strftime('%Y-%m-%d')
#         c.execute("INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)", 
#                 (user_info[0], 'Deposit', dAmount, formatted_date))
#         conn.commit()
#         st.success(f"Deposit ${dAmount} successfully!")
# elif option == "Withdrawal":
#     wAmount = st.number_input("Withdrawal Amount: ")
#     # print(user_info[0])
#     if st.button("Confirm", key="w_confirm"):
#         formatted_date = date.today().strftime('%Y-%m-%d')
#         c.execute("INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)", 
#                 (user_info[0], 'Withdrawal', -wAmount, formatted_date))
#         conn.commit()
#         st.success(f"Withdraw ${wAmount} successfully!")