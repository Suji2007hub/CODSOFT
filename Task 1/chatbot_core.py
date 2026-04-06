"""
Rule-Based Chatbot Core Engine
Clean, modular, and well-structured
"""

import re
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class Personality(Enum):
    """Bot personality types"""
    FORMAL = "formal"
    CASUAL = "casual"
    SARCASTIC = "sarcastic"


@dataclass
class Rule:
    """Represents a single conversation rule"""
    intent: str
    patterns: List[str]
    responses: Dict[Personality, List[str]]
    priority: int
    handler: Optional[Callable] = None


class ResponseGenerator:
    """Handles response selection and formatting"""
    
    @staticmethod
    def get_random_response(responses: List[str]) -> str:
        return random.choice(responses)
    
    @staticmethod
    def format_with_context(response: str, context: Dict) -> str:
        """Inject context into response"""
        if "{time}" in response:
            response = response.replace("{time}", datetime.now().strftime("%H:%M:%S"))
        if "{date}" in response:
            response = response.replace("{date}", datetime.now().strftime("%B %d, %Y"))
        return response


class IntentMatcher:
    """Handles pattern matching and intent detection"""
    
    def __init__(self):
        self.compiled_patterns: Dict[str, List[re.Pattern]] = {}
    
    def compile_patterns(self, rules: List[Rule]) -> None:
        """Pre-compile all regex patterns for performance"""
        for rule in rules:
            self.compiled_patterns[rule.intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in rule.patterns
            ]
    
    def match(self, user_input: str, rules: List[Rule]) -> Tuple[Optional[Rule], Optional[re.Match]]:
        """Match user input against all rules"""
        user_input = user_input.lower().strip()
        
        # Sort by priority (lower number = higher priority)
        sorted_rules = sorted(rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            patterns = self.compiled_patterns.get(rule.intent, [])
            for pattern in patterns:
                match = pattern.search(user_input)
                if match:
                    return rule, match
        
        return None, None


class ConversationContext:
    """Manages conversation state and history"""
    
    def __init__(self, max_history: int = 10):
        self.history: List[Dict] = []
        self.max_history = max_history
        self.user_name: Optional[str] = None
        self.last_intent: Optional[str] = None
    
    def add_exchange(self, user_input: str, response: str, intent: str) -> None:
        self.history.append({
            "user": user_input,
            "bot": response,
            "intent": intent,
            "timestamp": datetime.now()
        })
        self.last_intent = intent
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_last_user_message(self) -> Optional[str]:
        return self.history[-1]["user"] if self.history else None


class RuleBasedChatbot:
    """Main chatbot class - clean and modular"""
    
    def __init__(self, personality: Personality = Personality.CASUAL):
        self.personality = personality
        self.rules: List[Rule] = []
        self.context = ConversationContext()
        self.matcher = IntentMatcher()
        self._initialize_rules()
        self.matcher.compile_patterns(self.rules)
    
    def _initialize_rules(self) -> None:
        """Define all conversation rules"""
        self.rules = [
            # Priority 1: Critical/Exit rules
            Rule(
                intent="EXIT",
                patterns=[r"\b(bye|goodbye|exit|quit)\b", r"see you"],
                responses={
                    Personality.FORMAL: ["Farewell. Goodbye.", "Until next time."],
                    Personality.CASUAL: ["Bye! 👋", "See you later!", "Take care!"],
                    Personality.SARCASTIC: ["Finally. Bye.", "Don't let the door hit you."]
                },
                priority=1
            ),
            
            # Greetings
            Rule(
                intent="GREETING",
                patterns=[r"\b(hello|hi|hey|greetings)\b", r"^hey$", r"^hi$"],
                responses={
                    Personality.FORMAL: ["Hello. How may I help?", "Greetings. Good to see you."],
                    Personality.CASUAL: ["Hey there! 👋", "Hi! How's it going?", "Hello! 😊"],
                    Personality.SARCASTIC: ["Oh, hello there.", "Well, look who's here."]
                },
                priority=2
            ),
            
            # Time query
            Rule(
                intent="TIME",
                patterns=[r"what.*time", r"current time", r"time now"],
                responses={
                    Personality.FORMAL: [f"The time is {datetime.now().strftime('%H:%M:%S')}"],
                    Personality.CASUAL: [f"It's {datetime.now().strftime('%I:%M %p')} ⏰"],
                    Personality.SARCASTIC: [f"*sigh* It's {datetime.now().strftime('%H:%M:%S')}"]
                },
                priority=2
            ),
            
            # Date query
            Rule(
                intent="DATE",
                patterns=[r"what.*date", r"today('s)? date", r"what day"],
                responses={
                    Personality.FORMAL: [f"Today is {datetime.now().strftime('%B %d, %Y')}"],
                    Personality.CASUAL: [f"It's {datetime.now().strftime('%A, %B %d')} 📅"],
                    Personality.SARCASTIC: [f"*checks calendar* {datetime.now().strftime('%B %d, %Y')}"]
                },
                priority=2
            ),
            
            # Jokes
            Rule(
                intent="JOKE",
                patterns=[r"\b(joke|funny|laugh)\b", r"tell me a joke"],
                responses={
                    Personality.FORMAL: [
                        "Why do programmers prefer dark mode? Because light attracts bugs.",
                        "What do you call a fake noodle? An impasta."
                    ],
                    Personality.CASUAL: [
                        "Why don't scientists trust atoms? Because they make up everything! 😂",
                        "What's a computer's favorite snack? Micro-chips! 🍟"
                    ],
                    Personality.SARCASTIC: [
                        "Why did the scarecrow win an award? Outstanding in his field. Get it?",
                        "A man walks into a library... Never mind, you wouldn't get it."
                    ]
                },
                priority=3
            ),
            
            # Help
            Rule(
                intent="HELP",
                patterns=[r"\b(help|capabilities|what can you do)\b"],
                responses={
                    Personality.FORMAL: [
                        "I can: greet, tell time/date, tell jokes, calculate, and chat."
                    ],
                    Personality.CASUAL: [
                        "I can chat, tell jokes, give time/date, do math! Try me! 😊"
                    ],
                    Personality.SARCASTIC: [
                        "I do greetings, jokes, math, and pretend to care. Ask away."
                    ]
                },
                priority=2
            ),
            
            # Calculations (with handler)
            Rule(
                intent="CALCULATE",
                patterns=[r"(\d+)\s*([+\-*/])\s*(\d+)"],
                responses={p: [] for p in Personality},  # Empty, uses handler
                priority=1,
                handler=self._calculate
            ),
            
            # Default fallback
            Rule(
                intent="UNKNOWN",
                patterns=[r".*"],
                responses={
                    Personality.FORMAL: ["I don't understand. Please rephrase.", "Could you clarify?"],
                    Personality.CASUAL: ["Hmm, not sure I got that 🤔", "Can you say that differently?"],
                    Personality.SARCASTIC: ["Uh... what?", "That made no sense to me."]
                },
                priority=999
            ),
        ]
    
    def _calculate(self, match: re.Match) -> str:
        """Handle mathematical calculations"""
        try:
            num1 = float(match.group(1))
            op = match.group(2)
            num2 = float(match.group(3))
            
            operations = {
                '+': num1 + num2,
                '-': num1 - num2,
                '*': num1 * num2,
                '/': num1 / num2 if num2 != 0 else float('inf')
            }
            
            if op in operations:
                result = operations[op]
                if result == float('inf'):
                    return "Cannot divide by zero."
                
                responses = {
                    Personality.FORMAL: f"{num1} {op} {num2} = {result}",
                    Personality.CASUAL: f"{num1} {op} {num2} = {result} 🧮",
                    Personality.SARCASTIC: f"Even I can do math. {num1} {op} {num2} = {result}"
                }
                return responses[self.personality]
        except:
            pass
        return "Invalid calculation. Use format: 5 + 3"
    
    def get_response(self, user_input: str) -> Dict:
        """Main method to get bot response"""
        # Check for exit first
        if re.search(r"\b(bye|goodbye|exit|quit)\b", user_input.lower()):
            return {"text": self._get_response_for_intent("EXIT"), "intent": "EXIT", "should_exit": True}
        
        # Match intent
        rule, match = self.matcher.match(user_input, self.rules)
        
        if not rule:
            rule = next(r for r in self.rules if r.intent == "UNKNOWN")
        
        # Generate response
        if rule.handler and match:
            response_text = rule.handler(match)
        else:
            response_text = self._get_response_for_intent(rule.intent)
        
        # Update context
        self.context.add_exchange(user_input, response_text, rule.intent)
        
        return {
            "text": response_text,
            "intent": rule.intent,
            "should_exit": False
        }
    
    def _get_response_for_intent(self, intent: str) -> str:
        """Get random response for given intent"""
        rule = next((r for r in self.rules if r.intent == intent), None)
        if rule and rule.responses.get(self.personality):
            return random.choice(rule.responses[self.personality])
        return "I'm not sure how to respond to that."
    
    def set_personality(self, personality: Personality) -> None:
        """Change bot personality"""
        self.personality = personality
    
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        return {
            "total_rules": len(self.rules),
            "total_patterns": sum(len(r.patterns) for r in self.rules),
            "history_length": len(self.context.history),
            "current_personality": self.personality.value
        }


# CLI Interface
def run_cli():
    bot = RuleBasedChatbot(Personality.CASUAL)
    
    print("\n" + "="*50)
    print("RULE-BASED CHATBOT")
    print("="*50)
    print(f"Personality: {bot.personality.value}")
    print("Commands: 'help', 'personality [formal/casual/sarcastic]', 'stats', 'quit'")
    print("-"*50 + "\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print(f"Bot: {bot._get_response_for_intent('EXIT')}")
            break
        
        elif user_input.lower().startswith('personality'):
            parts = user_input.split()
            if len(parts) > 1:
                try:
                    new_personality = Personality(parts[1].lower())
                    bot.set_personality(new_personality)
                    print(f"Bot: Personality changed to {new_personality.value}")
                except ValueError:
                    print("Bot: Invalid personality. Use: formal, casual, sarcastic")
            else:
                print(f"Bot: Current personality: {bot.personality.value}")
        
        elif user_input.lower() == 'stats':
            stats = bot.get_stats()
            print(f"Bot: {stats}")
        
        else:
            response = bot.get_response(user_input)
            print(f"Bot [{response['intent']}]: {response['text']}")
            
            if response.get('should_exit'):
                break


if __name__ == "__main__":
    run_cli()