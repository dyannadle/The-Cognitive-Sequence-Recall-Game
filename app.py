from flask import Flask, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)
DB_NAME = 'cogni_quest_scores.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY,
            player_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route('/api/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    player_id = data.get('player_id')
    score = data.get('score')
    
    if player_id and isinstance(score, int):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        date_str = datetime.datetime.now().isoformat()
        
        cursor.execute("INSERT INTO scores (player_id, score, date) VALUES (?, ?, ?)", 
                       (player_id, score, date_str))
        conn.commit()
        conn.close()
        return jsonify({"message": "Score recorded successfully"}), 201
    return jsonify({"error": "Invalid data"}), 400

@app.route('/api/highscores/<player_id>', methods=['GET'])
def get_highscores(player_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score, date FROM scores WHERE player_id = ? ORDER BY score DESC, date DESC LIMIT 10", 
                   (player_id,))
    scores = cursor.fetchall()
    conn.close()
    
    # Simple score analysis to show improvement (the IQ 'boost' metric)
    if scores:
        average = sum(s[0] for s in scores) / len(scores)
        latest_score = scores[0][0]
        improvement = latest_score - average
    else:
        improvement = 0

    return jsonify({
        "highscores": [{"score": s[0], "date": s[1]} for s in scores],
        "improvement_metric": f"{improvement:.2f} difference from average"
    })

if __name__ == '__main__':
    init_db()
    # For a real application, you'd run this server on a network and the Pygame client
    # would make HTTP requests to it.
    # app.run(debug=True, port=5000)
    print("Flask Backend is set up. Run Pygame client separately.")
