# Task 1: Rule-Based Chatbot with Priority-Driven Pattern Matching

> **Problem Statement**
> Build a simple chatbot that responds to user inputs based on predefined rules. Use if-else statements or pattern matching techniques to identify user queries and provide appropriate responses. This will give you a basic understanding of natural language processing and conversation flow.

---

## Overview

This project implements a **rule-based chatbot** that does **not** rely on long, messy if-else chains. Instead, it uses a **priority-based rule engine** combined with **regex pattern matching** — a professional, scalable approach that still fully satisfies the requirement (pattern matching is explicitly allowed and often preferred over raw if-else).

The chatbot detects **intents** (greeting, time, joke, calculation, exit, etc.) and replies with responses that change based on **three personalities** (Casual, Formal, Sarcastic). It also maintains a short-term **conversation context** (history and last intent) to simulate basic conversation flow.

---

## How This Aligns with the Problem Statement

| Requirement | Our Implementation | Where to find it |
|---|---|---|
| Predefined rules | Rules stored as `Rule` dataclasses with `patterns`, `responses`, and `priority` | `chatbot_core.py` — `_initialize_rules()` |
| Pattern matching | Compiled regex patterns (`re.compile`) matched against user input | `IntentMatcher.match()` |
| Identify user queries | Matches input against all patterns, returns best rule by priority | `get_response()` calls `matcher.match()` |
| Appropriate responses | Each rule holds responses per personality; a random one is chosen | `_get_response_for_intent()` |
| NLP and conversation flow | Intent detection, conversation history, exit handling | `ConversationContext` class, `get_response()` |

> **Why a priority-based rule engine is still pattern matching:** the engine relies entirely on **regex patterns** to match user input. Priority only decides which matched rule fires first — exactly like a well-structured if-elif chain, but cleaner and easier to extend. This is **not** machine learning; it is a classic rule-based NLP technique.

---

## Features

- **Intent detection** — GREETING, TIME, DATE, JOKE, CALCULATE, HELP, EXIT, UNKNOWN
- **Regex patterns** — each intent supports multiple patterns (e.g. `"what.*time"`, `"current time"`)
- **Priority system** — lower number = higher priority (exit > greeting > help > default)
- **Three personalities** — Casual, Formal, Sarcastic — responses change instantly
- **Calculator handler** — evaluates expressions like `5 + 3` or `12 / 3`, formatted per personality
- **Conversation context** — stores last 10 exchanges and remembers last intent
- **Two interfaces** — Web UI (Flask) and Command Line Interface (CLI)

---

## Architecture

```
User input
    │
    ▼
Rules sorted by priority (lower number = higher priority)
    │
    ▼
Regex pattern matching (precompiled for performance)
    │
    ▼
Matching rule found?
    ├── Yes → Get responses for current personality
    │          If rule has a handler (e.g. calculator) → dynamic response
    │          Else → random static response
    └── No  → Fallback to UNKNOWN intent
    │
    ▼
Update conversation history
    │
    ▼
Return response + detected intent to UI
```

---

## Project Structure

```
Task 1/
├── chatbot_core.py      # Core engine: Rule, IntentMatcher, ConversationContext, RuleBasedChatbot
├── web_interface.py     # Flask web server — imports core, serves chat UI
└── README.md
```

The HTML is embedded inside `web_interface.py` — no separate templates folder needed.

---

## 💬 Code Comments & Workflow Clarity

All source files are **heavily commented** to explain the logic step by step:

- **`chatbot_core.py`** – Each class and method includes a docstring; important lines (regex compilation, priority sorting, context update) have inline comments.
- **`web_interface.py`** – The Flask routes and JavaScript functions are explained, showing how the frontend communicates with the backend.

These comments make it easy for any reader (instructor, peer, future you) to understand:
- How the priority‑based rule engine works
- Why regex pattern matching is used instead of simple if‑else
- How conversation context is maintained
- How the web UI sends messages and displays intents

> *The comments serve as a self‑documenting guide to the code’s workflow.*

## Getting Started

**Prerequisites:** Python 3.8+ and Flask

```bash
pip install flask
```

**Run the web interface (recommended):**

```bash
cd "Task 1"
python web_interface.py
```

Open **http://127.0.0.1:5000** in your browser.

**Run the CLI instead:**

```bash
cd "Task 1"
python chatbot_core.py
```

CLI commands: `help`, `personality casual/formal/sarcastic`, `stats`, `quit`

---

## Example Conversations (Casual mode)

| Input | Response | Detected intent |
|---|---|---|
| `Hello` | "Hey there! 👋" | GREETING |
| `What time is it?` | "It's 02:30 PM ⏰" | TIME |
| `Tell me a joke` | "Why don't scientists trust atoms? Because they make up everything! 😂" | JOKE |
| `5 + 3` | "5 + 3 = 8 🧮" | CALCULATE |
| `12 / 3` | "12 / 3 = 4 🧮" | CALCULATE |
| `Help` | "I can chat, tell jokes, give time/date, do math! Try me! 😊" | HELP |
| `bye` | "Bye! 👋" | EXIT |

Each bot message in the web UI displays an **intent badge** (e.g. `Intent: GREETING`) — showing the pattern matching in action.

---

## Pattern Matching in Practice

The regex patterns handle natural input variation:

| Intent | Pattern | Matches "Hello there!"? | Matches "hey" alone? |
|---|---|---|---|
| GREETING | `\b(hello\|hi\|hey)\b` | ✅ Yes | ✅ Yes |
| TIME | `what.*time` | ✅ Yes | ✅ Yes |
| JOKE | `\b(joke\|funny\|laugh)\b` | ✅ Yes | ✅ Yes |
| CALCULATE | `(\d+)\s*([+\-*/])\s*(\d+)` | ✅ Yes | ✅ Yes |

---

## Extending the Chatbot

To add a new intent, append one `Rule` to `_initialize_rules()` — no other changes needed:

```python
Rule(
    intent="WEATHER",
    patterns=[r"\b(weather|rain|sunny)\b"],
    responses={
        Personality.CASUAL: ["I can't check weather, but hope it's nice!"],
        Personality.FORMAL: ["I lack weather API access. Please consult a meteorologist."],
        Personality.SARCASTIC: ["Oh sure, let me just pull up my satellite feed... not."]
    },
    priority=2
)
```

---

## Checklist

- [x] Predefined rules (Rule dataclasses)
- [x] Pattern matching (regex via `re.compile`)
- [x] User query identification mapped to intents
- [x] Appropriate responses (static + dynamic calculator)
- [x] NLP demonstration (intent detection, conversation context)
- [x] Clean modular code — no spaghetti if-else
- [x] Runnable with a single command