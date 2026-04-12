# Tic-Tac-Toe AI – Minimax with Alpha-Beta Pruning

---

## 📌 Overview

This is a **Tic-Tac-Toe AI game** where a human player competes against an AI agent.
The AI uses the **Minimax algorithm** and **Alpha-Beta pruning** to make optimal decisions and become unbeatable at the highest difficulty level.

The project demonstrates concepts of **game theory, adversarial search, and decision tree optimization**.

---

## 🎯 Features

* ✅ Human vs AI gameplay (X vs O)
* ✅ 4 difficulty levels:

  * Easy – Random moves
  * Medium – 1-step lookahead
  * Hard – Full Minimax algorithm
  * Unbeatable – Minimax + Alpha-Beta pruning
* ✅ AI decision analysis (thinking trace)

  * Nodes evaluated
  * Branches pruned
  * Depth tracking
  * Move score evaluation
* ✅ Web-based interface using Flask
* ✅ Clean and interactive UI
* ✅ Single-file implementation

---

## 🛠️ Tech Stack

| Layer         | Technology            |
| ------------- | --------------------- |
| Backend       | Python 3.8+           |
| Web Framework | Flask                 |
| Frontend      | HTML, CSS, JavaScript |
| AI Algorithm  | Minimax + Alpha-Beta  |

---

## 📁 Project Structure

```
task2/
└── tictactoe_app.py   # Complete game + AI + web app
└── README.md          # Documentation
```

---

## ⚙️ Installation & Run

1. Install Flask:

```bash
pip install flask
```

2. Run the application:

```bash
python tictactoe_app.py
```

3. Open browser:

```
http://127.0.0.1:5001
```

---

## 🧠 How It Works

The AI:

* Explores all possible moves using recursive Minimax search
* Assigns scores:

  * +10 → AI win
  * -10 → AI loss
  * 0 → draw
* Uses **depth-based scoring** to prefer faster wins and delay losses
* Uses **Alpha-Beta pruning** to eliminate unnecessary branches and improve performance

---

## ✨ Unique Design Choices

* Single-file architecture (engine + AI + backend combined)
* Thinking trace system for AI transparency
* Move score analysis for all possible positions
* Separate implementations of Minimax and Alpha-Beta pruning
* Clean modular AI design with difficulty abstraction

---

## 📝 Evaluation Checklist

| Requirement                     | Status |
| ------------------------------- | ------ |
| Tic-Tac-Toe game implementation | ✅      |
| Human vs AI                     | ✅      |
| Minimax algorithm               | ✅      |
| Alpha-Beta pruning              | ✅      |
| Unbeatable AI                   | ✅      |
| Clean structured code           | ✅      |
| Web interface (Flask)           | ✅      |
| Unique implementation           | ✅      |

---

## 👨‍💻 Author & Submission

This project was completed as **Task 2** of the *Code Soft Internship Program*.
All code is original and written by me, [V S Sujithraa].

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.
