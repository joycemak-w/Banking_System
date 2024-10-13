import sqlite3
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta

def calculate_monthly_interest(balance, records, start_date, end_date, daily_rate):
    total_interest = 0.0
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    records.sort(key=lambda x: x['date'])
    prev_date = start_date

    for record in records:
        record_date = datetime.strptime(record['date'], '%Y-%m-%d')
        days = (record_date - prev_date).days
        if days > 0 and balance > 0:
            interest = balance * days * daily_rate
            total_interest += interest
        balance += record['amount']
        prev_date = record_date

    if prev_date < end_date:
        remaining_days = (end_date - prev_date).days
        if balance > 0:
            interest = balance * remaining_days * daily_rate
            total_interest += interest

    return total_interest

# today = datetime(2024, 10, 1)
today = datetime.now().date()
def get_previous_month_dates():
    first_day_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    return first_day_of_last_month.strftime('%Y-%m-%d'), last_day_of_last_month.strftime('%Y-%m-%d')

def fetch_monthly_balance_records(start_date, end_date):
    connection = sqlite3.connect('./banking_system.db')  # Update with your database file
    cursor = connection.cursor()

    cursor.execute("""
        SELECT date, user_id, SUM(amount) as total FROM balance_record
        WHERE strftime('%Y-%m-%d', date) BETWEEN ? AND ? GROUP BY date, user_id
        """, (start_date, end_date))

    records = cursor.fetchall()
    connection.close()

    # Convert records to a list of dictionaries
    return [{'date': record[0], 'user_id': record[1], 'amount': record[2]} for record in records]

def fetch_pre_balance_records(start_date):
    connection = sqlite3.connect('./banking_system.db')  # Update with your database file
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, SUM(amount) as total FROM balance_record
        WHERE strftime('%Y-%m-%d', date) < ? GROUP BY date, user_id
        """, (start_date,))

    records = cursor.fetchall()
    connection.close()

    # Convert records to a list of dictionaries
    return [{'user_id': record[0], 'amount': record[1]} for record in records]

def job():
    # balance_records = [
    #     {'user_id': 1, 'reason': 'Deposit', 'amount': 3000.0, 'date': '2024-08-24'},
    #     {'user_id': 1, 'reason': 'Deposit', 'amount': 1000.0, 'date': '2024-09-24'},
    #     {'user_id': 1, 'reason': 'Withdrawal', 'amount': -250.0, 'date': '2024-09-25'},
    #     {'user_id': 1, 'reason': 'Deposit', 'amount': 2000.0, 'date': '2024-09-28'}
    # ]

    daily_rate = 0.00626 / 365
    start_date, end_date = get_previous_month_dates()

    # Fetch balance records from the database
    balance_records = fetch_monthly_balance_records(start_date, end_date)
    pre_balance_records = fetch_pre_balance_records(start_date)
    user_ids = {item['user_id'] for item in balance_records}
    conn = sqlite3.connect('./banking_system.db')  # Update with your database file
    cursor = conn.cursor()
    for i in user_ids:
      user_balance_records = [ item for item in balance_records if item.get('user_id') == i ]
      # pre_balance = [ item.get('amount') for item in pre_balance_records if item.get('user_id') == i ]
      pre_balance_list = [item.get('amount') for item in pre_balance_records if item.get('user_id') == i]
      # print(pre_balance_list)
      pre_balance = 0
      if pre_balance_list:  # Check if the list is not empty
          pre_balance = pre_balance_list[0]
          print(pre_balance)
      monthly_interest = calculate_monthly_interest(pre_balance, user_balance_records, start_date, end_date, daily_rate)
      # cursor.execute('''
      #   INSERT INTO balance_record (user_id, reason, amount, date)
      #   VALUES (?, ?, ?, ?)
      # ''', (i, "Interest", round(monthly_interest, 2), (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')))
      cursor.execute('''
        INSERT INTO balance_record (user_id, reason, amount, date)
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
          SELECT 1 FROM balance_record 
          WHERE reason = ? 
            AND date = ? 
            AND user_id = ?
        )
      ''', (i, "Interest", round(monthly_interest, 2), (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d'), "Interest", (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d'), i))
      # Commit the transaction and close the connection
      conn.commit()
      print("user: " + str(i))
      print(f"Total Monthly Interest for {start_date} to {end_date}: {monthly_interest:.4f}")
      # print(balance_records)
    conn.close()

def check_and_run_job():
    if today.day == 1:  # Check if it's the first day of the month
        job()

# Schedule the check to run every day at 00:00
schedule.every().day.at("00:00").do(check_and_run_job)

while True:
    schedule.run_pending()
    time.sleep(1)  # Wait for 1 second before checking again