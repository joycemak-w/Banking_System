import streamlit as st
import sqlite3
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to validate user login
def validate_user(username, password):
    conn = sqlite3.connect('./banking_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    return c.fetchone() is not None

def login():
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if validate_user(username, password):
            st.session_state.user = username
            st.success("Login in successfully!")
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password.")

def main():
    st.title("Banking System")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    login_page = st.Page(login, title="Log in", icon=":material/login:")
    signup_page = st.Page("signup.py", title="Sign Up", icon=":material/person_add:")

    dashboard = st.Page("reports/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
    alerts = st.Page("reports/alerts.py", title="System alerts", icon=":material/notification_important:")

    search = st.Page("tools/search.py", title="Search", icon=":material/query_stats:")
    analysis = st.Page("tools/analysis.py", title="Stock Analysis", icon=":material/search_insights:")
    
    balance = st.Page("transitions/balance.py", title="Balance", icon=":material/currency_exchange:")
    transaction= st.Page("transitions/transaction.py", title="Stock Transaction", icon=":material/candlestick_chart:")



    if st.session_state.logged_in:
        pg = st.navigation(
            {
                "Reports": [dashboard, alerts],
                "Tools": [search, analysis],
                "Transitions": [balance, transaction],
            }
        )
        if st.sidebar.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        pg = st.navigation([login_page, signup_page])

    pg.run()

if __name__ == "__main__":
    main()