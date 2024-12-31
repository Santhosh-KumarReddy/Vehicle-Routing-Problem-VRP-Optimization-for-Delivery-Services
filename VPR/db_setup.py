import sqlite3
import pandas as pd

# Load data
path = r"C:\Users\madha\Desktop\sem 7\OR\archive\19MDVRP Problem Sets.xlsx"

# Prepare depots data
data = pd.read_excel(path, sheet_name='Problem 8')
depots = data[['Number of Depots', 'Depot x coordinate', 'Depot y coordinate']].dropna().reset_index(drop=True)
depots.columns = ['DepotID', 'X_Coordinate', 'Y_Coordinate']
depots['DepotID'] = depots['DepotID'].astype(int)

# Prepare customers data
customers = data[['Customer Number', 'x coordinate', 'y coordinate']].dropna().reset_index(drop=True)
customers.columns = ['CustomerID', 'X_Coordinate', 'Y_Coordinate']
customers['CustomerID'] = customers['CustomerID'].astype(int)
customers['DepotID'] = -1  # Placeholder DepotID, update based on assignment logic

# Connect to SQLite
conn = sqlite3.connect(r"C:\Users\madha\Desktop\sem 7\OR\VRP\vrp.db")
cursor = conn.cursor()

# Enable Write-Ahead Logging for better concurrency
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Depots (
    DepotID INTEGER PRIMARY KEY,
    X_Coordinate REAL,
    Y_Coordinate REAL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY,
    DepotID INTEGER,
    X_Coordinate REAL,
    Y_Coordinate REAL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS OptimalPaths (
    PathID INTEGER PRIMARY KEY,
    DepotID INTEGER,
    Path TEXT
)
""")

# Insert data into SQLite
depots.to_sql('Depots', conn, if_exists='replace', index=False)
customers.to_sql('Customers', conn, if_exists='replace', index=False)

# Commit changes and close connection
conn.commit()
conn.close()
print("Database setup completed.")
