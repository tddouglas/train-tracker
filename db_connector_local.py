import sqlite3
import datetime


# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('trains.db')
cursor = conn.cursor()

# Create the arrivals table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS trains_arrivals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    train_number TEXT,
                    train_name TEXT,
                    destination TEXT,
                    status TEXT,
                    track TEXT,
                    date TEXT
                )''')

# Create the departures table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS trains_departures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    train_number TEXT,
                    train_name TEXT,
                    destination TEXT,
                    status TEXT,
                    track TEXT,
                    date TEXT
                )''')

conn.commit()


# Functions for writing to local instance
def upsert_train_entry(train, table_name):
    # Get current date to store with the entry
    today = datetime.date.today().isoformat()

    # Check if the train already exists in the selected table
    cursor.execute(f'''SELECT * FROM {table_name} 
                      WHERE train_number = ? AND date = ?''',
                   (train['train_number'], today))
    result = cursor.fetchone()

    # If the train doesn't exist, insert a new entry
    if result is None:
        cursor.execute(f'''INSERT INTO {table_name} (time, train_number, train_name, destination, status, track, date)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (train['time'], train['train_number'], train['train_name'], train['destination'], train['status'], train['track'], today))
    else:
        # Update the existing entry with any new or changed data
        cursor.execute(f'''UPDATE {table_name} SET time = ?, train_name = ?, destination = ?, status = ?, track = ? 
                          WHERE train_number = ? AND date = ?''',
                       (train['time'], train['train_name'], train['destination'], train['status'], train['track'], train['train_number'], today))

    conn.commit()


def close_db():
    # Close the connection when done
    conn.close()

