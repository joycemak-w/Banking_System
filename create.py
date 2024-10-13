import sqlite3
import hashlib

# Create a SQLite database and a users table
def create_db():
    conn = sqlite3.connect('./banking_system.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS balance_record (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            reason TEXT,
            amount REAL,
            date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_record (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            symbol TEXT,
            volume INTTEGER,
            price REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_sample_data():
    conn = sqlite3.connect('./banking_system.db')
    c = conn.cursor()
    # Sample data for the users table
    users_data = [
        ('test1', hash_password('test1')),
        ('test2', hash_password('test2')),
        ('test3', hash_password('test3')),
    ]

    # Inserting sample data into the users table
    for username, password in users_data:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))

        # Sample data for the balance_record table
        balance_records_data = [
            (1, 'Deposit', 1000.00, '2024-09-28'),
            (1, 'Withdrawal', -250.00, '2024-09-28'),
            (1, 'Deposit', 2000.00, '2024-09-28'),
            (2, 'Deposit', 1500.00, '2024-09-28'),
            (2, 'Withdrawal', -500.00, '2024-09-28'),
            (3, 'Deposit', 200.00, '2024-09-28'),
            # (3, 'Withdrawal', -50.00, '2024-09-27'),
        ]

    # Inserting sample data into the balance_record table
    for user_id, reason, amount, date in balance_records_data:
        c.execute('INSERT INTO balance_record (user_id, reason, amount, date) VALUES (?, ?, ?, ?)', (user_id, reason, amount, date))

        # Commit the changes
    conn.commit()

create_db()
# create_sample_data()