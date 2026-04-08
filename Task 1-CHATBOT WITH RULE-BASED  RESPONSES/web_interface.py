"""
web_interface.py
Flask Web Interface for Rule-Based Chatbot

Provides a browser-based chat UI with personality selector and quick replies.
All logic remains unchanged – only the frontend design is refined.
"""

from flask import Flask, render_template_string, request, jsonify
from chatbot_core import RuleBasedChatbot, Personality

app = Flask(__name__)
bot = RuleBasedChatbot(Personality.CASUAL)

# Clean, modern HTML template – no "AI generated" look
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>RuleBot | Intent‑Driven Chatbot</title>
    <style>
        /* ---------- RESET & BASE ---------- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif;
            background: #eef2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1.5rem;
        }

        /* main chat card */
        .chat-card {
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 32px;
            box-shadow: 0 20px 35px -12px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.2s ease;
        }

        /* header */
        .chat-header {
            background: #1e2a3e;
            color: white;
            padding: 1.5rem 2rem;
            text-align: center;
        }
        .chat-header h1 {
            font-weight: 600;
            font-size: 1.8rem;
            letter-spacing: -0.3px;
        }
        .chat-header p {
            font-size: 0.85rem;
            opacity: 0.8;
            margin-top: 0.3rem;
        }
        .personality-select {
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            border-radius: 40px;
            border: none;
            background: #2d3e50;
            color: white;
            font-weight: 500;
            cursor: pointer;
            font-size: 0.85rem;
        }

        /* message area */
        .message-area {
            height: 450px;
            overflow-y: auto;
            padding: 1.5rem;
            background: #f9fbfd;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .message {
            display: flex;
            max-width: 85%;
        }
        .user-message {
            align-self: flex-end;
            justify-content: flex-end;
        }
        .bot-message {
            align-self: flex-start;
        }
        .bubble {
            padding: 0.75rem 1.2rem;
            border-radius: 24px;
            font-size: 0.9rem;
            line-height: 1.4;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .user-message .bubble {
            background: #1e2a3e;
            color: white;
            border-bottom-right-radius: 6px;
        }
        .bot-message .bubble {
            background: white;
            color: #1e2a3e;
            border-bottom-left-radius: 6px;
            border: 1px solid #e2edf2;
        }
        .intent-badge {
            font-size: 0.65rem;
            opacity: 0.7;
            margin-top: 0.3rem;
            font-family: 'SF Mono', monospace;
        }
        .user-message .intent-badge {
            color: #bdd4e8;
        }

        /* quick replies */
        .quick-replies {
            padding: 0.8rem 1.5rem;
            background: white;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
        }
        .quick-btn {
            background: #f1f5f9;
            border: none;
            padding: 0.4rem 1rem;
            border-radius: 40px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.15s;
            color: #1e2a3e;
        }
        .quick-btn:hover {
            background: #e2e8f0;
            transform: translateY(-1px);
        }

        /* input area */
        .input-area {
            padding: 1rem 1.5rem 1.5rem;
            background: white;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 0.8rem;
        }
        .input-area input {
            flex: 1;
            padding: 0.8rem 1.2rem;
            border: 1px solid #cbd5e1;
            border-radius: 48px;
            font-size: 0.9rem;
            outline: none;
            transition: 0.15s;
        }
        .input-area input:focus {
            border-color: #2c6e9e;
            box-shadow: 0 0 0 2px rgba(44,110,158,0.1);
        }
        .input-area button {
            background: #1e2a3e;
            color: white;
            border: none;
            padding: 0 1.5rem;
            border-radius: 48px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }
        .input-area button:hover {
            background: #0f1a2a;
        }

        /* scrollbar */
        .message-area::-webkit-scrollbar {
            width: 6px;
        }
        .message-area::-webkit-scrollbar-track {
            background: #e2e8f0;
            border-radius: 10px;
        }
        .message-area::-webkit-scrollbar-thumb {
            background: #94a3b8;
            border-radius: 10px;
        }

        @media (max-width: 600px) {
            .chat-card {
                border-radius: 24px;
            }
            .message {
                max-width: 95%;
            }
        }
    </style>
</head>
<body>
<div class="chat-card">
    <div class="chat-header">
        <h1>🤖 RuleBot</h1>
        <p>rule‑based · intent detection · personality modes</p>
        <select class="personality-select" id="personalitySelect">
            <option value="casual">😊 Casual</option>
            <option value="formal">🎩 Formal</option>
            <option value="sarcastic">🙄 Sarcastic</option>
        </select>
    </div>

    <div class="message-area" id="messageArea">
        <div class="message bot-message">
            <div class="bubble">
                Hello! I'm a rule‑based chatbot. Ask me anything.<br>
                <span class="intent-badge">Intent: WELCOME</span>
            </div>
        </div>
    </div>

    <div class="quick-replies" id="quickReplies">
        <button class="quick-btn">Hello</button>
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
    const messageArea = document.getElementById('messageArea');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const personalitySelect = document.getElementById('personalitySelect');

    function addMessage(text, isUser, intent = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.innerHTML = text;
        if (!isUser && intent) {
            const badge = document.createElement('div');
            badge.className = 'intent-badge';
            badge.textContent = `Intent: ${intent}`;
            bubble.appendChild(badge);
        }
        msgDiv.appendChild(bubble);
        messageArea.appendChild(msgDiv);
        msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        addMessage(message, true);
        userInput.value = '';

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await res.json();
            addMessage(data.response, false, data.intent);
        } catch (err) {
            addMessage('⚠️ Server error. Is the backend running?', false, 'ERROR');
        }
    }

    async function changePersonality() {
        const personality = personalitySelect.value;
        try {
            await fetch('/personality', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ personality: personality })
            });
            addMessage(`🧠 Personality changed to ${personality} mode`, false, 'SYSTEM');
        } catch (err) {
            console.warn('failed to update personality');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    personalitySelect.addEventListener('change', changePersonality);

    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.textContent;
            sendMessage();
        });
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    response = bot.get_response(user_input)
    return jsonify({
        'response': response['text'],
        'intent': response['intent']
    })

@app.route('/personality', methods=['POST'])
def set_personality():
    data = request.json
    personality_name = data.get('personality', 'casual')
    try:
        personality = Personality(personality_name)
        bot.set_personality(personality)
        return jsonify({'status': 'success', 'personality': personality_name})
    except:
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)