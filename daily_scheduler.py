# is not used

import sqlite3
from datetime import datetime
import schedule
import time

# Connect to the database
conn = sqlite3.connect('banking_system.db')
c = conn.cursor()

# Constants
ANNUAL_INTEREST_RATE = 0.00626  # 0.62600%
DAILY_INTEREST_RATE = ANNUAL_INTEREST_RATE / 365

# Function to calculate and insert daily interest
def calculate_and_insert_interest():
    # Get current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Fetch current balances for each user
    c.execute('''
        SELECT user_id, SUM(amount) as total_balance
        FROM balance_record
        GROUP BY user_id
    ''')
    
    user_balances = c.fetchall()

    # Calculate interest for each user and insert the record
    for user_id, total_balance in user_balances:
        interest = total_balance * DAILY_INTEREST_RATE
        
        # Insert interest record
        c.execute('''
            INSERT INTO interest_record (user_id, amount, date)
            VALUES (?, ?, ?)
        ''', (user_id, interest, current_date))
    conn.commit()
    if datetime.now().day == 1:
        # c.execute('''
        #     INSERT INTO balance_record (user_id, amount, date)
        #     VALUES (?, ?, ?)
        # ''', (user_id, interest, current_date))
        pass

    # Commit changes
    conn.commit()
    print(f"Interest calculated and recorded for date: {current_date}")

# calculate_and_insert_interest()
# Schedule the function to run daily at a specific time (e.g., 00:00)

schedule.every().day.at("00:00").do(calculate_and_insert_interest)

# Keep the script running
try:
    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait one minute before checking again
except KeyboardInterrupt:
    print("Scheduler stopped.")

# Close the connection (this line won't be reached in normal operation)
conn.close()
