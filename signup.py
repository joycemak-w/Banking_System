import streamlit as st
import sqlite3
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create a new user
def create_user(username, password):
    conn = sqlite3.connect('banking_system.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

st.subheader("Create an Account")
username = st.text_input("Username")
password = st.text_input("Password", type='password')
confirm_password = st.text_input("Confirm Password", type='password')

if st.button("Sign Up"):
    if confirm_password == password:
        if create_user(username, password):
            st.success("Account created successfully!")
            st.rerun()
        else:
            st.error("Username already exists. Please choose another.")
    else:
        st.error("Please make sure your confirmed password and password are the same.")