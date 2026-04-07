"""
app.py
Flask backend for Tic-Tac-Toe Minimax AI

Exposes:
- /                : serves the web interface (HTML)
- /ai_move (POST)  : accepts board state and difficulty, returns AI move + ThinkingTrace
"""

from flask import Flask, jsonify, render_template, request
from game_core import Difficulty, MinimaxAI, Player, TicTacToeGame

app = Flask(__name__, template_folder=".")


def _difficulty_from_index(index: int) -> Difficulty:
    """Convert frontend slider index (0-3) to Difficulty enum."""
    mapping = {
        0: Difficulty.EASY,
        1: Difficulty.MEDIUM,
        2: Difficulty.HARD,
        3: Difficulty.UNBEATABLE,
    }
    return mapping.get(index, Difficulty.HARD)


def _normalize_board(raw_board):
    """
    Clean up board representation from frontend.
    Frontend may send null, empty strings, or spaces for empty cells.
    Convert to standard ' ' for empty.
    """
    if not isinstance(raw_board, list) or len(raw_board) != 9:
        return None
    normalized = []
    for cell in raw_board:
        if cell in (None, "", " "):
            normalized.append(" ")
        elif cell in ("X", "O"):
            normalized.append(cell)
        else:
            return None
    return normalized


@app.route("/", methods=["GET"])
def home():
    """Serve the main game interface."""
    return render_template("web_interface.html")


@app.route("/ai_move", methods=["POST"])
def ai_move():
    """
    Expects JSON: {"board": [..9 cells..], "difficulty": 0..3}
    Returns JSON with AI move and complete ThinkingTrace.
    """
    data = request.get_json(silent=True) or {}
    board = _normalize_board(data.get("board"))
    difficulty_index = data.get("difficulty", 2)  # default Hard

    try:
        difficulty_index = int(difficulty_index)
    except (TypeError, ValueError):
        difficulty_index = 2

    if board is None:
        return jsonify({"error": "Invalid board format"}), 400

    # Reconstruct game state
    game = TicTacToeGame()
    game.board = board

    # If board is full, no move possible
    if not game.get_empty_cells():
        return jsonify({
            "move": None,
            "score": 0,
            "move_scores": [],
            "nodes_evaluated": 0,
            "branches_pruned": 0,
            "max_depth": 0,
            "evaluation_time": 0.0,
        })

    # Create AI with chosen difficulty and get move
    ai = MinimaxAI(_difficulty_from_index(difficulty_index))
    move, trace = ai.get_move(game, Player.O)   # AI always plays O

    # Convert trace to JSON-serializable dict
    return jsonify({
        "move": move,
        "score": trace.score,
        "move_scores": [
            {"position": ms.position, "score": ms.score, "depth": ms.depth}
            for ms in trace.all_scores
        ],
        "nodes_evaluated": trace.nodes_evaluated,
        "branches_pruned": trace.branches_pruned,
        "max_depth": trace.max_depth_reached,
        "evaluation_time": trace.evaluation_time_ms,
    })


if __name__ == "__main__":
    # Run on port 5001 to avoid conflict with Task 1 (which uses 5000)
    app.run(debug=True, port=5001)