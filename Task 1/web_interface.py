"""
Minimal Flask Web Interface for Chatbot
"""

from flask import Flask, render_template_string, request, jsonify
from chatbot_core import RuleBasedChatbot, Personality

app = Flask(__name__)
bot = RuleBasedChatbot(Personality.CASUAL)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RuleBot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 500px;
            height: 700px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: #2d3748;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .personality-select {
            margin-top: 10px;
            padding: 5px 10px;
            border-radius: 5px;
            border: none;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f7fafc;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .user-message {
            justify-content: flex-end;
        }
        .bot-message {
            justify-content: flex-start;
        }
        .message-content {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 18px;
            font-size: 14px;
        }
        .user-message .message-content {
            background: #667eea;
            color: white;
        }
        .bot-message .message-content {
            background: white;
            color: #2d3748;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .intent-badge {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 5px;
        }
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 25px;
            outline: none;
        }
        .chat-input button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }
        .quick-replies {
            display: flex;
            gap: 8px;
            padding: 10px 20px;
            overflow-x: auto;
        }
        .quick-reply {
            padding: 5px 12px;
            background: #edf2f7;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 12px;
            white-space: nowrap;
        }
        .quick-reply:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 RuleBot</h2>
            <select class="personality-select" id="personality">
                <option value="casual">😊 Casual</option>
                <option value="formal">🎩 Formal</option>
                <option value="sarcastic">🙄 Sarcastic</option>
            </select>
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                <div class="message-content">
                    Hello! I'm a rule-based chatbot. Ask me anything!
                    <div class="intent-badge">Intent: WELCOME</div>
                </div>
            </div>
        </div>
        
        <div class="quick-replies" id="quickReplies">
            <button class="quick-reply">Hello</button>
            <button class="quick-reply">Tell me a joke</button>
            <button class="quick-reply">What time is it?</button>
            <button class="quick-reply">5 + 3</button>
            <button class="quick-reply">Help</button>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
            <button id="sendBtn">Send</button>
        </div>
    </div>
    
    <script>
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const personalitySelect = document.getElementById('personality');
        
        function addMessage(text, isUser, intent = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = text;
            
            if (intent && !isUser) {
                const intentSpan = document.createElement('div');
                intentSpan.className = 'intent-badge';
                intentSpan.textContent = `Intent: ${intent}`;
                contentDiv.appendChild(intentSpan);
            }
            
            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
            messageDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            userInput.value = '';
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            addMessage(data.response, false, data.intent);
        }
        
        async function changePersonality() {
            const personality = personalitySelect.value;
            const response = await fetch('/personality', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ personality: personality })
            });
            addMessage(`Personality changed to ${personality} mode`, false, 'SYSTEM');
        }
        
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        personalitySelect.addEventListener('change', changePersonality);
        
        document.querySelectorAll('.quick-reply').forEach(btn => {
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