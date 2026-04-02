import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'museum.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            otp TEXT,
            is_verified BOOLEAN DEFAULT 0,
            full_name TEXT
        )
    ''')

    # Create Exhibitions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exhibitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            availability_status TEXT DEFAULT 'Open'
        )
    ''')
    
    # Create Bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            visitor_name TEXT,
            exhibition_id INTEGER,
            num_tickets INTEGER,
            total_price REAL,
            ticket_hash TEXT,
            status TEXT DEFAULT 'Confirmed',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(exhibition_id) REFERENCES exhibitions(id)
        )
    ''')
    
    # Insert some mock exhibitions
    c.execute('SELECT COUNT(*) FROM exhibitions')
    if c.fetchone()[0] == 0:
        exhibitions = [
            ("Ancient Artifacts", "Explore the wonders of ancient civilizations.", 150.0),
            ("Modern Science Gallery", "Interactive science exhibits and experiments.", 200.0),
            ("Space Exploration", "Discover the universe, planetarium show included.", 300.0)
        ]
        c.executemany('INSERT INTO exhibitions (title, description, price) VALUES (?, ?, ?)', exhibitions)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
