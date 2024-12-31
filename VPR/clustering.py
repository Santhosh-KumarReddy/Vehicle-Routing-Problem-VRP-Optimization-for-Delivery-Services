from sklearn.cluster import KMeans
import pandas as pd
import sqlite3

def assign_customers_to_depots(db_path, n_clusters):
    # Load data
    conn = sqlite3.connect(db_path)
    customers = pd.read_sql_query("SELECT * FROM Customers", conn)
    depots = pd.read_sql_query("SELECT * FROM Depots", conn)
    
    # Prepare customer coordinates
    customer_coords = customers[['X_Coordinate', 'Y_Coordinate']].values
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    customers['DepotID'] = kmeans.fit_predict(customer_coords)
    
    # Optionally: Print out how customers are assigned
    print(customers[['CustomerID', 'DepotID']].head())
    
    # Update database
    customers.to_sql('Customers', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Clustering completed and updated in the database.")
