

import re
import random
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template_string, request, jsonify

# ---------------------- TIMEZONE (IST) ----------------------
IST = timezone(timedelta(hours=5, minutes=30))

def now_ist():
    return datetime.now(IST)

# ---------------------- TONE MODES --------------------------
class ToneMode:
    FORMAL = "formal"
    CASUAL = "casual"
    SARCASTIC = "sarcastic"

# ---------------------- CHAT MEMORY -------------------------
class ChatMemory:
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history
        self.user_name = None          # 👈 unique: remembers name
        self.last_intent = None

    def add(self, user_msg, bot_msg, intent):
        self.history.append({
            "user": user_msg,
            "bot": bot_msg,
            "intent": intent,
            "time": now_ist().strftime("%H:%M:%S")
        })
        self.last_intent = intent
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_last_user(self):
        return self.history[-1]["user"] if self.history else None

# ---------------------- PATTERN DISPATCHER ------------------
class PatternDispatcher:
    def __init__(self):
        self.compiled = {}

    def compile_rules(self, rules):
        for rule in rules:
            self.compiled[rule["intent"]] = [
                re.compile(p, re.IGNORECASE) for p in rule["patterns"]
            ]

    def match(self, text, rules):
        text = text.lower().strip()
        # sort by priority (lower = higher)
        sorted_rules = sorted(rules, key=lambda r: r["priority"])
        for rule in sorted_rules:
            for pattern in self.compiled.get(rule["intent"], []):
                m = pattern.search(text)
                if m:
                    return rule, m
        return None, None

# ---------------------- RESPONSE STYLIST --------------------
class ReplyStylist:
    @staticmethod
    def pick(responses):
        # MY STYLE: prefer shorter responses 60% of the time
        if random.random() < 0.6 and len(responses) > 1:
            return min(responses, key=len)
        return random.choice(responses)

    @staticmethod
    def fill_placeholders(text, context=None):
        t = now_ist()
        text = text.replace("{time}", t.strftime("%I:%M %p"))
        text = text.replace("{date}", t.strftime("%B %d, %Y"))
        if context and context.user_name:
            text = text.replace("{name}", context.user_name)
        return text

# ---------------------- INTENT ROUTER (MAIN ENGINE) ---------
class IntentRouter:
    def __init__(self, tone=ToneMode.CASUAL):
        self.tone = tone
        self.memory = ChatMemory()
        self.dispatcher = PatternDispatcher()
        self.rules = self._build_rules()
        self.dispatcher.compile_rules(self.rules)

    def _build_rules(self):
        # Custom rules – each has intent, patterns, responses (per tone), priority, optional handler
        return [
            {  # EXIT – highest priority
                "intent": "EXIT",
                "patterns": [r"\b(bye|goodbye|exit|quit)\b", r"see you"],
                "responses": {
                    ToneMode.FORMAL: ["Farewell. Goodbye.", "Until next time."],
                    ToneMode.CASUAL: ["Bye! 👋", "See you later!", "Take care!"],
                    ToneMode.SARCASTIC: ["Finally. Bye.", "Don't let the door hit you."]
                },
                "priority": 1,
                "handler": None
            },
            {  # GREETING
                "intent": "GREETING",
                "patterns": [r"\b(hello|hi|hey|namaste|vanakkam)\b", r"^hey$", r"^hi$"],
                "responses": {
                    ToneMode.FORMAL: ["Hello. How may I help?", "Greetings."],
                    ToneMode.CASUAL: ["Hey there! 👋", "Hi! How's it going?", "Namaste! 😊", "Vanakkam! 🙏"],
                    ToneMode.SARCASTIC: ["Oh, hello there.", "Well, look who's here."]
                },
                "priority": 2,
                "handler": None
            },
            {  # NAME MEMORY (UNIQUE FEATURE)
                "intent": "REMEMBER_NAME",
                "patterns": [r"my name is (\w+)", r"call me (\w+)", r"i am (\w+)"],
                "responses": {},  # handled dynamically
                "priority": 1,
                "handler": self._handle_name
            },
            {  # TIME (IST)
                "intent": "TIME",
                "patterns": [r"what.*time", r"current time", r"time now"],
                "responses": {
                    ToneMode.FORMAL: ["The time is {time} IST"],
                    ToneMode.CASUAL: ["It's {time} IST ⏰"],
                    ToneMode.SARCASTIC: ["*sigh* It's {time} IST"]
                },
                "priority": 2,
                "handler": None
            },
            {  # DATE
                "intent": "DATE",
                "patterns": [r"what.*date", r"today('s)? date", r"what day"],
                "responses": {
                    ToneMode.FORMAL: ["Today is {date} (IST)"],
                    ToneMode.CASUAL: ["It's {date} 📅 (IST)"],
                    ToneMode.SARCASTIC: ["*checks calendar* {date} IST"]
                },
                "priority": 2,
                "handler": None
            },
            {  # JOKE
                "intent": "JOKE",
                "patterns": [r"\b(joke|funny|laugh)\b", r"tell me a joke"],
                "responses": {
                    ToneMode.FORMAL: ["Why do programmers prefer dark mode? Light attracts bugs.", "What do you call a fake noodle? An impasta."],
                    ToneMode.CASUAL: ["Why don't scientists trust atoms? Because they make up everything! 😂", "What's a computer's favorite snack? Micro-chips! 🍟"],
                    ToneMode.SARCASTIC: ["Why did the scarecrow win an award? Outstanding in his field. Get it?", "A man walks into a library... Never mind."]
                },
                "priority": 3,
                "handler": None
            },
            {  # CALCULATOR (simpler logic – my style)
                "intent": "CALCULATE",
                "patterns": [r"(\d+)\s*([+\-*/])\s*(\d+)"],
                "responses": {},
                "priority": 1,
                "handler": self._calculate
            },
            {  # HELP
                "intent": "HELP",
                "patterns": [r"\b(help|capabilities|what can you do)\b"],
                "responses": {
                    ToneMode.FORMAL: ["I can: greet, tell time/date, tell jokes, calculate, remember your name, and chat."],
                    ToneMode.CASUAL: ["I can chat, tell jokes, give time/date, do math, and remember your name! Try me! 😊"],
                    ToneMode.SARCASTIC: ["I do greetings, jokes, math, name memory, and pretend to care. Ask away."]
                },
                "priority": 2,
                "handler": None
            },
            {  # FALLBACK – catches anything else
                "intent": "UNKNOWN",
                "patterns": [r".*"],
                "responses": {
                    ToneMode.FORMAL: ["I don't understand. Please rephrase.", "Could you clarify?"],
                    ToneMode.CASUAL: ["Hmm, not sure I got that 🤔", "Can you say that differently?"],
                    ToneMode.SARCASTIC: ["Uh... what?", "That made no sense to me."]
                },
                "priority": 999,
                "handler": None
            }
        ]

    def _handle_name(self, match):
        name = match.group(1)
        self.memory.user_name = name
        replies = {
            ToneMode.FORMAL: f"Nice to meet you, {name}.",
            ToneMode.CASUAL: f"Got it, {name}! 😊",
            ToneMode.SARCASTIC: f"Oh wow, you have a name. {name} it is."
        }
        return replies[self.tone]

    def _calculate(self, match):
        try:
            a = float(match.group(1))
            op = match.group(2)
            b = float(match.group(3))
            if op == '+':
                res = a + b
            elif op == '-':
                res = a - b
            elif op == '*':
                res = a * b
            elif op == '/':
                if b == 0:
                    return "Cannot divide by zero."
                res = a / b
            else:
                return "Invalid operator."
            # Format based on tone
            if self.tone == ToneMode.FORMAL:
                return f"{a} {op} {b} = {res}"
            elif self.tone == ToneMode.CASUAL:
                return f"{a} {op} {b} = {res} 🧮"
            else:
                return f"Even I can do math. {a} {op} {b} = {res}"
        except:
            return "Use format like: 5 + 3"

    def get_reply(self, user_input, debug=False):
        # Debug mode (unique)
        if debug:
            print(f"[DEBUG] Input: {user_input}")

        # Quick exit
        if re.search(r"\b(bye|goodbye|exit|quit)\b", user_input.lower()):
            reply = self._pick_response_for_intent("EXIT")
            self.memory.add(user_input, reply, "EXIT")
            return {"text": reply, "intent": "EXIT", "exit": True}

        # Match intent
        rule, match = self.dispatcher.match(user_input, self.rules)
        if not rule:
            rule = next(r for r in self.rules if r["intent"] == "UNKNOWN")

        # Generate response
        if rule["handler"] and match:
            reply_text = rule["handler"](match)
        else:
            reply_text = self._pick_response_for_intent(rule["intent"])
            # Fill placeholders like {time}, {name}
            reply_text = ReplyStylist.fill_placeholders(reply_text, self.memory)

        self.memory.add(user_input, reply_text, rule["intent"])
        return {"text": reply_text, "intent": rule["intent"], "exit": False}

    def _pick_response_for_intent(self, intent):
        for r in self.rules:
            if r["intent"] == intent:
                responses = r["responses"].get(self.tone, [])
                if responses:
                    return ReplyStylist.pick(responses)
        return "I'm not sure how to respond."

    def set_tone(self, new_tone):
        self.tone = new_tone

    def get_stats(self):
        return {
            "rules": len(self.rules),
            "history": len(self.memory.history),
            "tone": self.tone,
            "user_name": self.memory.user_name
        }

# ---------------------- FLASK WEB INTERFACE -----------------
app = Flask(__name__)
bot = IntentRouter(tone=ToneMode.CASUAL)

# Simple, slightly handmade UI – no overdesign
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RuleBot – Custom Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto; background: #eef2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .chat-container { max-width: 700px; width: 100%; background: white; border-radius: 28px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #1e2a3e; color: white; padding: 1.2rem; text-align: center; }
        .header h1 { font-weight: 600; font-size: 1.6rem; }
        .tone-select { margin-top: 8px; padding: 6px 12px; border-radius: 40px; border: none; background: #2d3e50; color: white; cursor: pointer; }
        .chat-area { height: 420px; overflow-y: auto; padding: 1rem; background: #f9fbfd; display: flex; flex-direction: column; gap: 12px; }
        .msg { display: flex; max-width: 85%; }
        .user { align-self: flex-end; justify-content: flex-end; }
        .bot { align-self: flex-start; }
        .bubble { padding: 8px 16px; border-radius: 24px; font-size: 0.9rem; line-height: 1.4; }
        .user .bubble { background: #1e2a3e; color: white; border-bottom-right-radius: 6px; }
        .bot .bubble { background: white; border: 1px solid #ddd; border-bottom-left-radius: 6px; color: #1e2a3e; }
        .intent { font-size: 0.65rem; opacity: 0.7; margin-top: 4px; }
        .quick-area { padding: 10px 1rem; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 8px; flex-wrap: wrap; }
        .quick-btn { background: #eef2f5; border: none; padding: 5px 14px; border-radius: 40px; font-size: 0.8rem; cursor: pointer; }
        .input-area { padding: 12px 1rem 1rem; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 10px 16px; border: 1px solid #ccc; border-radius: 60px; outline: none; }
        .input-area button { background: #1e2a3e; color: white; border: none; padding: 0 20px; border-radius: 60px; cursor: pointer; }
        @media (max-width: 550px) { .msg { max-width: 95%; } }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <h1>🤖 RuleBot</h1>
        <p>rule‑based · memory · tone modes</p>
        <select class="tone-select" id="toneSelect">
            <option value="casual">😊 Casual</option>
            <option value="formal">🎩 Formal</option>
            <option value="sarcastic">🙄 Sarcastic</option>
        </select>
    </div>
    <div class="chat-area" id="chatArea">
        <div class="msg bot">
            <div class="bubble">Hello! I remember names, tell jokes, do math, and more.<br><span class="intent">Intent: WELCOME</span></div>
        </div>
    </div>
    <div class="quick-area" id="quickArea">
        <button class="quick-btn">Hello</button>
        <button class="quick-btn">My name is Alex</button>
        <button class="quick-btn">Tell me a joke</button>
        <button class="quick-btn">What time is it?</button>
        <button class="quick-btn">5 + 3</button>
        <button class="quick-btn">Help</button>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
        <button id="sendBtn">Send</button>
    </div>
</div>
<script>
    const chatArea = document.getElementById('chatArea');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const toneSelect = document.getElementById('toneSelect');

    function addMessage(text, isUser, intent=null) {
        const div = document.createElement('div');
        div.className = `msg ${isUser ? 'user' : 'bot'}`;
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.innerHTML = text;
        if (!isUser && intent) {
            const badge = document.createElement('div');
            badge.className = 'intent';
            badge.innerText = `Intent: ${intent}`;
            bubble.appendChild(badge);
        }
        div.appendChild(bubble);
        chatArea.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }

    async function sendMessage() {
        const msg = userInput.value.trim();
        if (!msg) return;
        addMessage(msg, true);
        userInput.value = '';
        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            addMessage(data.response, false, data.intent);
        } catch(e) {
            addMessage('Server error', false, 'ERROR');
        }
    }

    async function changeTone() {
        const tone = toneSelect.value;
        await fetch('/tone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tone: tone })
        });
        addMessage(`🧠 Tone changed to ${tone} mode`, false, 'SYSTEM');
    }

    sendBtn.onclick = sendMessage;
    userInput.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
    toneSelect.onchange = changeTone;
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.onclick = () => { userInput.value = btn.innerText; sendMessage(); };
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '')
    reply = bot.get_reply(user_msg, debug=False)   # set debug=True to see console logs
    return jsonify({'response': reply['text'], 'intent': reply['intent']})

@app.route('/tone', methods=['POST'])
def set_tone():
    data = request.json
    new_tone = data.get('tone', 'casual')
    if new_tone in [ToneMode.FORMAL, ToneMode.CASUAL, ToneMode.SARCASTIC]:
        bot.set_tone(new_tone)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)