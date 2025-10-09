# The-Cognitive-Sequence-Recall-Game
The game presents players with a sequence of colored tiles that light up on a 4×4 grid. The player must recall and repeat the sequence exactly. Difficulty scales rapidly by increasing sequence length, flash speed, and, at higher levels, introducing complex, recognizable sub-patterns that challenge the brain to chunk information efficiently.





Yes, I can now generate the **final, full-fledged README** file. This version incorporates all the updates and instructions required for both the advanced cognitive features ($\text{GameLogic.py}$ changes) and the essential steps for running the separated frontend/backend architecture, including the necessary Python commands.

-----

# 🧠 Cogni-Quest: The Advanced Cognitive Sequence Recall Game

[](https://www.python.org/)
[](https://flask.palletsprojects.com/)
[](https://www.pygame.org/)
[](https://opensource.org/licenses/MIT)

## 🚀 Overview

**Cogni-Quest** is an advanced Python game designed to rigorously train core components of **fluid intelligence** ($Gf$), focusing on **working memory**, **pattern recognition**, and **cognitive flexibility**.

The game challenges the player to recall a sequence of flashing tiles on a $4 \times 4$ grid. Difficulty scales rapidly, introducing complex cognitive modes that move beyond simple recall:

1.  **Transformation Recall:** Requires the player to mentally manipulate the sequence (e.g., reverse it or sort by tile number) *before* inputting it.
2.  **Pattern Prediction:** Requires the player to identify a repeating pattern and predict the next tile that was deliberately omitted from the flash.

The game uses a **separated client-server architecture** where the Pygame client runs the game, and a Flask server handles persistent score tracking and performance analytics.

-----

## ✨ Key Features

  * **Advanced Cognitive Modes:** **TRANSFORM** and **PREDICT** modes challenge mental manipulation and inductive reasoning.
  * **Adaptive Difficulty:** Adjusts sequence length and flash speed dynamically based on player score.
  * **Split Architecture:** Pygame client for responsive $2$D graphics; Flask API backend for data persistence.
  * **Score Analytics:** Records detailed scores to an SQLite database for long-term performance tracking.

-----

## 🛠️ Technology Stack & Dependencies

This project is built entirely in Python. You will need **Python 3.9+**.

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend (Client)** | **Pygame** | Game rendering, user input, and making API calls. |
| **Backend (Server)** | **Flask** | RESTful API for score management and data handling. |
| **Core Logic** | **Pure Python** | Manages game state, sequence generation, and cognitive rules. |
| **Database** | **SQLite** | Local database for persistent storage of player scores ($\text{cogni\_quest\_scores.db}$). |

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/YourUsername/cogni-quest.git
    cd cogni-quest
    ```

2.  **Set up Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate   # Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: This uses the `requirements.txt` file generated previously.)*

-----

## ▶️ How to Run the Game

**IMPORTANT:** The Flask backend must be running before the Pygame client can launch, as the client attempts to submit scores to the server upon game over.

### Step 1: Start the Backend Server (Terminal 1)

Open your first terminal, activate the virtual environment, and run the Flask application. This will also initialize the SQLite database file ($\text{cogni\_quest\_scores.db}$).

```bash
# In Terminal 1
python app.py 
```

The server will run on `http://127.0.0.1:5000/`. Keep this terminal window open.

### Step 2: Launch the Pygame Frontend (Terminal 2)

Open a **new terminal window**, activate the virtual environment, and launch the game client.

```bash
# In Terminal 2
python main_game.py
```

The game window will appear. The game automatically transitions through **RECALL**, **TRANSFORM**, and **PREDICT** modes as your score increases.

-----

## 🗺️ Project Structure

Your project directory should contain the following files:

```
cogni-quest/
├── app.py              # Flask Backend API
├── GameLogic.py        # Core game logic, patterns, and transformation rules
├── main_game.py        # Pygame client, rendering, and input handling
├── requirements.txt    # List of project dependencies (pygame, Flask, requests)
├── README.md           # This file
└── cogni_quest_scores.db # SQLite database (created on first run of app.py)
```

-----

## 💻 API Endpoints (Backend)

The Pygame client interacts with the Flask server using the following endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/submit_score` | Used by the client to record the final score to the database. |
| **GET** | `/api/highscores/<player_id>` | Retrieves the top scores and a performance trend/improvement metric for the specified player. |

-----

## 🤝 Contributing

We welcome suggestions and contributions, especially for creating more challenging transformation rules or sophisticated pattern generation algorithms for the high-level modes.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/new-pattern-logic`).
3.  Commit your changes (`git commit -m 'Feat: Added new prediction logic.'`).
4.  Open a Pull Request.

## 📄 License

This project is licensed under the **MIT License**.
