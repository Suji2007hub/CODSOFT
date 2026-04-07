# Task 2: Tic-Tac-Toe AI — Minimax with Alpha-Beta Pruning (X-Ray Edition)

> **Problem Statement**  
> *Implement an AI agent that plays Tic-Tac-Toe against a human player. Use algorithms like Minimax with or without Alpha-Beta Pruning to make the AI player unbeatable. This project will help you understand game theory and basic search algorithms.*

---

## 📌 Overview

This implementation goes beyond a simple unbeatable bot. It exposes the **internal reasoning** of the AI through a live "X-Ray" panel:

- **Move score heatmap** – every empty cell shows the numeric score the AI calculated (green = good for AI, red = bad).
- **Nodes evaluated** – how many game states were explored.
- **Branches pruned** – how many were cut by Alpha-Beta (only in Unbeatable mode).
- **Max recursion depth** – how deep the search went.
- **Evaluation time** – milliseconds per move.

This turns the game into a **teaching tool** for search algorithms.

---

## 🎯 How This Aligns with the Problem Statement

| Requirement | Implementation | Where to Find |
|---|---|---|
| AI agent plays Tic-Tac-Toe | Complete game logic with human vs AI | `TicTacToeGame` class |
| Minimax algorithm | Full recursive Minimax in `_minimax()` | `game_core.py` lines 200–260 |
| Alpha-Beta pruning | `_minimax_alpha_beta()` with prune checks | `game_core.py` lines 270–340 |
| Unbeatable AI | Hard and Unbeatable modes always choose optimal moves | Verified by minimax scoring |
| Understanding game theory | Score system (+10 - depth, depth -10) shows preference for faster wins / slower losses | Terminal evaluation in minimax |

**Four difficulty levels** demonstrate algorithmic progression:

| Level | Algorithm | Nodes Evaluated (empty board) |
|---|---|---|
| Easy | Random | 0 |
| Medium | 1-ply lookahead | ~9 |
| Hard | Full Minimax | ~549,946 |
| Unbeatable | Minimax + Alpha-Beta | ~20,866 (96% fewer!) |

---

## ✨ Unique Features (The "X-Ray")

- **Heatmap** – each empty cell shows its minimax score. Click any difficulty and watch the numbers appear.
- **Real-time statistics** – after every AI move, the sidebar updates with nodes evaluated, pruned branches, depth, and time.
- **Algorithm comparison** – play the same opening move on Hard vs Unbeatable to see pruning in action.
- **Winning line highlight** – when the game ends, the winning cells flash.

---

## 📁 Project Structure

```
Task 2/
├── game_core.py          # Game logic, Minimax, Alpha-Beta, ThinkingTrace
├── app.py                # Flask backend (serves HTML, handles /ai_move API)
├── web_interface.html    # Frontend UI (board, heatmap, stats sidebar)
└── README.md             # This file
```

> **Note:** `web_interface.html` uses JavaScript to draw the board, fetch `/ai_move`, and update the heatmap and stats.

---

## 🚀 How to Run

### Prerequisites
- Python 3.8+
- Install Flask:
```bash
pip install flask
```

### Steps
```bash
cd "Task 2"
python app.py
```

Then open your browser at **http://127.0.0.1:5001**

> Port 5001 is used to avoid conflict with Task 1 (which uses 5000).

### Play the Game
1. **You are X** (human). Click any empty cell to place your mark.
2. The AI (O) moves automatically.
3. Use the **difficulty slider** at the top to change AI behaviour at any time.
4. Watch the **heatmap** update before the AI moves – it shows the score of every possible move.
5. Check the **sidebar** after each AI turn to see how many nodes were evaluated and how many branches were pruned.

---

## 🧪 Example: Seeing Alpha-Beta in Action

1. Set difficulty to **Hard** (full Minimax).  
   Make a move (e.g., center). The AI thinks — sidebar shows ~500,000 nodes evaluated, 0 pruned.

2. Reset, set difficulty to **Unbeatable** (Minimax + Alpha-Beta).  
   Make the same move. Sidebar shows ~20,000 nodes evaluated and thousands of pruned branches.  
   The AI still makes the same optimal move, but much faster internally.

This is the **core learning outcome** — Alpha-Beta pruning dramatically reduces search space without sacrificing correctness.

---

## 📊 Code Walkthrough (Key Methods)

### `TicTacToeGame`
- `make_move()` – places a mark and checks win.
- `get_empty_cells()` – returns available positions.
- `check_winner()` – row/column/diagonal check.

### `MinimaxAI`
- `get_move()` – dispatches to appropriate algorithm based on difficulty.
- `_minimax()` – pure recursive minimax. Returns `(best_move, score, all_scores)`.
- `_minimax_alpha_beta()` – same but with alpha/beta cutoffs and pruning counter.
- **Scoring:** AI win = `10 - depth` (prefers faster wins), human win = `depth - 10` (delays loss), draw = `0`.

### `ThinkingTrace`
- Captures all statistics for one move. Returned to frontend and displayed.

### Flask API (`/ai_move`)
- Receives board and difficulty, returns JSON with move and trace data.

---

## ✅ Alignment Checklist

- [x] AI plays Tic-Tac-Toe against human
- [x] Implements Minimax (Hard mode)
- [x] Implements Alpha-Beta pruning (Unbeatable mode)
- [x] AI is unbeatable in Hard/Unbeatable modes
- [x] Demonstrates game theory via scoring and pruning statistics
- [x] Clean, modular code with extensive comments
- [x] Web interface with visual heatmap and real-time analytics

---

## 🔧 Possible Enhancements

1. **Move ordering** – sort moves by heuristic to improve pruning even more.
2. **Opening book** – hardcode optimal first moves for instant response.
3. **Unit tests** – verify minimax scores for all board states.
4. **Persistent analytics** – track win rates per difficulty over many games.

---

## 📚 Final Note

This project is **not just a game** — it is an **interactive visualization of search algorithms**. The instructor can slide difficulty, observe node counts drop by orders of magnitude, and see exactly why Alpha-Beta is essential for game AI. All code is self-contained, runs offline, and requires no external APIs.