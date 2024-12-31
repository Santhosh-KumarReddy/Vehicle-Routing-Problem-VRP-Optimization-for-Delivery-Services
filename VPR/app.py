from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Path to the SQLite database
DB_PATH = 'vrp.db'

# Home route to render the DepotID selection page
@app.route('/')
def index():
    # Get all DepotID values from the database to display them as options
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DepotID FROM OptimalPaths")
        depot_ids = cursor.fetchall()
        conn.close()
        return render_template('index.html', depot_ids=[depot[0] for depot in depot_ids])
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Route to get the path for a specific DepotID
@app.route('/get_route', methods=['GET'])
def get_route():
    depot_id = request.args.get('depot_id', type=int)
    
    if depot_id is None:
        return jsonify({"error": "Depot ID is required."}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Path FROM OptimalPaths WHERE DepotID = ?", (depot_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({"path": result[0]})
        else:
            return jsonify({"error": "No path found for the selected DepotID."}), 404
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
