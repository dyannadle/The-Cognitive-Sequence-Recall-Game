from flask import Flask, request, jsonify, render_template, send_from_directory # Import Flask components for web serving and API handling
import sqlite3 # Import sqlite3 for local database management
import datetime # Import datetime to timestamp score submissions
import os # Import os for directory and file path operations

app = Flask(__name__, template_folder='templates', static_folder='static') # Initialize the Flask application with template and static paths
DB_NAME = 'cogni_quest_scores.db' # Define the filename for the SQLite database

def init_db(): # Function to initialize the database and ensure the scores table exists
    conn = sqlite3.connect(DB_NAME) # Establish a connection to the SQLite database file
    cursor = conn.cursor() # Create a cursor object to execute SQL commands
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores ( # SQL command to create the table if it's missing
            id INTEGER PRIMARY KEY, # Unique auto-incrementing ID for each score entry
            player_id TEXT NOT NULL, # String identifier for the player (e.g., 'Elite_Agent')
            score INTEGER NOT NULL, # Numerical score achieved by the player
            date TEXT NOT NULL # ISO-formatted timestamp of the game session
        )
    """)
    conn.commit() # Save the changes to the database
    conn.close() # Close the database connection to free up resources

@app.route('/api/submit_score', methods=['POST']) # Define the API endpoint for submitting new scores
def submit_score(): # Handler function for the score submission POST request
    data = request.json # Parse the incoming JSON data from the request body
    player_id = data.get('player_id') # Extract the player identifier from the JSON
    score = data.get('score') # Extract the numerical score from the JSON
    
    if player_id and isinstance(score, int): # Validate that both player_id exists and score is an integer
        conn = sqlite3.connect(DB_NAME) # Connect to the database
        cursor = conn.cursor() # Create a cursor
        date_str = datetime.datetime.now().isoformat() # Generate a timestamp string for the current moment
        
        cursor.execute("INSERT INTO scores (player_id, score, date) VALUES (?, ?, ?)", # SQL to insert data
                       (player_id, score, date_str)) # Provide the tuple of values for the query
        conn.commit() # Commit the insertion transaction
        conn.close() # Close the connection
        return jsonify({"message": "Score recorded successfully"}), 201 # Return success response with 201 Created status
    return jsonify({"error": "Invalid data"}), 400 # Return error response if validation fails

@app.route('/api/highscores/<player_id>', methods=['GET']) # Endpoint to fetch top scores for a specific player
def get_highscores(player_id): # Handler function that takes the player_id from the URL path
    conn = sqlite3.connect(DB_NAME) # Connect to the database
    cursor = conn.cursor() # Create a cursor
    cursor.execute("SELECT score, date FROM scores WHERE player_id = ? ORDER BY score DESC, date DESC LIMIT 10", # Query
                   (player_id,)) # Use the player_id as a parameter to prevent SQL injection
    scores = cursor.fetchall() # Retrieve all matching rows (up to 10)
    conn.close() # Close the connection
    
    # Simple score analysis to show improvement (the IQ 'boost' metric)
    if scores: # If any scores were found for this player
        average = sum(s[0] for s in scores) / len(scores) # Calculate the arithmetic mean of the top 10 scores
        latest_score = scores[0][0] # Get the very highest score (from the sorted list)
        improvement = latest_score - average # Calculate how much the best score exceeds the average
    else: # If no scores are recorded yet
        improvement = 0 # Default improvement to zero
    
    # Return JSON containing the scores list and the calculated improvement metric
    return jsonify({
        "highscores": [{"score": s[0], "date": s[1]} for s in scores], # Format scores as list of dictionaries
        "improvement_metric": f"{improvement:.2f} difference from average" # Format improvement as a string
    })

@app.route('/') # Define the main landing page route
def index(): # Handler for the root URL
    return render_template('index.html') # Serve the 'index.html' file from the templates folder

@app.route('/api/global_highscores', methods=['GET']) # Endpoint for the global leaderboard across all players
def global_highscores(): # Handler for fetching top scores globally
    conn = sqlite3.connect(DB_NAME) # Connect to the database
    cursor = conn.cursor() # Create a cursor
    # Fetch top 10 scores from all players
    cursor.execute("SELECT player_id, score, date FROM scores ORDER BY score DESC, date DESC LIMIT 10") # Global query
    scores = cursor.fetchall() # Get the top 10 global entries
    conn.close() # Close the connection
    
    # Map the results to a clean list of dictionaries for the frontend
    results = [{"player_id": s[0], "score": s[1], "date": s[2]} for s in scores]
    return jsonify({"results": results}) # Return the global leaderboard as JSON

@app.route('/download') # Route for the game download page (place holder)
def download(): # Handler for the download URL
    # Placeholder for the future executable
    return "Download coming soon! Run 'python build_exe.py' to generate your local version." # Informative message

if __name__ == '__main__': # Traditional Python entry point check
    init_db() # Ensure the database schema is initialized before starting the server
    # Ensure templates and static folders exist if not created by tools
    if not os.path.exists('templates'): os.makedirs('templates') # Create templates directory if it doesn't exist
    if not os.path.exists('static'): os.makedirs('static') # Create static directory if it doesn't exist
    
    print("Cogni-Quest Backend is ready.") # Log to console that initialization is complete
    print("Serving on http://127.0.0.1:5000") # Log the local access URL
    app.run(debug=True, port=5000) # Start the Flask development server on port 5000 with debug mode enabled
