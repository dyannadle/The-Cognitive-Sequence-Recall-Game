from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/global_highscores', methods=['GET'])
def global_highscores():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Fetch top 10 scores from all players
    cursor.execute("SELECT player_id, score, date FROM scores ORDER BY score DESC, date DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    
    results = [{"player_id": s[0], "score": s[1], "date": s[2]} for s in scores]
    return jsonify({"results": results})

@app.route('/download')
def download():
    # Placeholder for the future executable
    return "Download coming soon! Run 'python build_exe.py' to generate your local version."

if __name__ == '__main__':
    init_db()
    # Ensure templates and static folders exist if not created by tools
    if not os.path.exists('templates'): os.makedirs('templates')
    if not os.path.exists('static'): os.makedirs('static')
    
    print("Cogni-Quest Backend is ready.")
    print("Serving on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
