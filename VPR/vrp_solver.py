import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Database path
DB_PATH = "vrp.db"

# Step 1: Fetch depots and customers data
def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    depots = pd.read_sql_query("SELECT DepotID, X_Coordinate AS x, Y_Coordinate AS y FROM Depots", conn)
    customers = pd.read_sql_query("SELECT CustomerID, X_Coordinate AS x, Y_Coordinate AS y FROM Customers", conn)
    conn.close()
    return depots, customers

# Step 2: Assign each customer to the nearest depot using K-means clustering
def assign_customers_to_depots(depots, customers):
    num_depots = len(depots)
    kmeans = KMeans(n_clusters=num_depots, random_state=0)
    customers['Depot Assignment'] = kmeans.fit_predict(customers[['x', 'y']])
    return customers

# Step 3: Solve VRP for a single depot
def solve_vrp(customers_data, depot_location, depot_number):
    locations = np.vstack([[depot_location['x'], depot_location['y']], customers_data[['x', 'y']].values])
    num_locations = len(locations)

    def distance(x, y):
        return int(np.linalg.norm(locations[x] - locations[y]))

    distance_matrix = [[distance(i, j) for j in range(num_locations)] for i in range(num_locations)]

    # OR-Tools setup
    manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)  # 1 vehicle, starting at the depot
    routing = pywrapcp.RoutingModel(manager)
    transit_callback_index = routing.RegisterTransitCallback(
        lambda i, j: distance_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)]
    )
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set distance dimension
    routing.AddDimension(transit_callback_index, 0, 100000, True, "Distance")
    distance_dimension = routing.GetDimensionOrDie("Distance")
    distance_dimension.SetGlobalSpanCostCoefficient(1)

    # Solve
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)

    # Retrieve and save solution
    if solution:
        route = []
        index = routing.Start(0)
        route_distance = 0

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            if 0 <= previous_index < num_locations and 0 <= index < num_locations:
                route_distance += distance_matrix[previous_index][index]

        route.append(manager.IndexToNode(index))
        route_representation = " -> ".join(
            str(customers_data.iloc[node - 1]['CustomerID']) if node > 0 else "Depot" for node in route
        )
        return route_representation, route_distance
    return "No solution found", 0

# Step 4: Solve VRP for all depots
def solve_vrp_for_all_depots(depots, customers):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM OptimalPaths")

    for depot_index, depot in depots.iterrows():
        depot_customers = customers[customers['Depot Assignment'] == depot_index].reset_index(drop=True)
        if not depot_customers.empty:
            route, distance = solve_vrp(depot_customers, depot, depot_index + 1)
            cursor.execute("INSERT INTO OptimalPaths (DepotID, Path) VALUES (?, ?)", (depot['DepotID'], route))
            print(f"Depot {depot['DepotID']}: {route} | Distance: {distance}")
        else:
            print(f"No customers assigned to Depot {depot['DepotID']}")
    conn.commit()
    conn.close()

# Step 5: Main function
def main():
    depots, customers = fetch_data()
    customers = assign_customers_to_depots(depots, customers)
    solve_vrp_for_all_depots(depots, customers)

if __name__ == "__main__":
    main()
