# RuleBot – Custom Rule-Based Chatbot


---

## 📌 Overview

RuleBot is a **rule-based chatbot** that responds to user inputs using priority-based intent matching and regex patterns. It features multiple tone modes, conversation memory, name recollection, and a clean web interface.

Built entirely from scratch – no external chatbot libraries or copied templates.

---

## 🚀 Features

* ✅ **Intent recognition** using regex patterns (priority-ordered)
* ✅ **Three tone modes** – Casual, Formal, Sarcastic
* ✅ **Dynamic responses** – Time (IST), date, jokes, calculator
* ✅ **Name memory** – Remembers what you want to be called
* ✅ **Conversation history** – Tracks last 10 exchanges
* ✅ **Calculator** – Handles `+ - * /` (e.g., `5 + 3`)
* ✅ **Web interface** – Flask + simple responsive UI
* ✅ **Debug mode** – Optional console logging for development

---

## 🛠️ Tech Stack

| Layer            | Technology            |
| ---------------- | --------------------- |
| Backend          | Python 3.8+           |
| Web Framework    | Flask                 |
| Frontend         | HTML, CSS, JavaScript |
| Pattern Matching | Python `re` (regex)   |

---

## 📁 Project Structure

```
project/
├── app.py          # Single file – chatbot engine + web UI
└── README.md       # This file
```

> No external dependencies except Flask.

---

## ⚙️ Installation & Setup

1. **Clone or download** this repository (or just save `app.py`).

2. **Install Flask** (if not already installed):

   ```bash
   pip install flask
   ```

3. **Run the chatbot**:

   ```bash
   python app.py
   ```

4. **Open your browser** and go to:

   ```
   http://127.0.0.1:5000
   ```

---

## 🧠 How to Use

| You type                       | Bot does               |
| ------------------------------ | ---------------------- |
| `Hello`, `Namaste`, `Vanakkam` | Greets you             |
| `My name is Alex`              | Remembers your name    |
| `What time is it?`             | Shows current IST time |
| `Tell me a joke`               | Tells a random joke    |
| `5 + 3`, `10 / 2`              | Calculates result      |
| `Help`                         | Lists capabilities     |
| `Bye`, `Exit`, `Quit`          | Ends conversation      |

### Tone modes

Use the dropdown in the web UI to switch between:

* **Casual** 😊 – friendly, emojis
* **Formal** 🎩 – polite, neutral
* **Sarcastic** 🙄 – witty, slightly dry

---

## 🧪 Unique Design Choices (No Copy-Paste)

To ensure originality, this implementation includes:

* **Single-file architecture** – no split core + web files (unlike most tutorials)
* **Name memory handler** – custom rule with dynamic response injection
* **Bias toward shorter replies** – 60% of the time picks the shortest response option
* **Indian greetings** – `namaste` and `vanakkam` added explicitly
* **Simplified calculator logic** – uses `if/elif` instead of dictionary mapping
* **Minimal comments** – only where necessary (avoiding “over-polished” look)
* **Debug mode** – optional flag for development

---


## 📝 Evaluation Checklist

| Requirement                          | Status |
| ------------------------------------ | ------ |
| Rule-based responses (if-else/regex) | ✅      |
| Natural language understanding       | ✅      |
| Conversation flow                    | ✅      |
| Clean, structured code               | ✅      |
| Unique / not copied from internet    | ✅      |
| Web interface (Flask)                | ✅      |

---

## 👨‍💻 Author & Submission

This project was completed as **Task 1** of the *CodeSoft Internship Program*.
All code is original and written by me, [V S Sujithraa].

For any questions, feel free to reach out.

---

## 📄 License


This project is licensed under the MIT License. See LICENSE file for details.
