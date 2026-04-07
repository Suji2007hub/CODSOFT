"""
chatbot_core.py
Rule-Based Chatbot Core Engine

This module implements a priority-driven rule engine with regex pattern matching.
It detects user intents, supports multiple personalities, and maintains conversation context.
"""

import re
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class Personality(Enum):
    """Bot personality types – affects response style."""
    FORMAL = "formal"
    CASUAL = "casual"
    SARCASTIC = "sarcastic"


@dataclass
class Rule:
    """
    Represents a single conversation rule.
    
    Attributes:
        intent: Unique identifier for the intent (e.g., "GREETING")
        patterns: List of regex patterns that trigger this rule
        responses: Dictionary mapping personality to list of possible responses
        priority: Lower number = higher priority (1 is highest)
        handler: Optional callable for dynamic responses (e.g., calculator)
    """
    intent: str
    patterns: List[str]
    responses: Dict[Personality, List[str]]
    priority: int
    handler: Optional[Callable] = None


class ResponseGenerator:
    """Handles response selection and formatting (e.g., injecting time/date)."""
    
    @staticmethod
    def get_random_response(responses: List[str]) -> str:
        """Pick a random response from the list."""
        return random.choice(responses)
    
    @staticmethod
    def format_with_context(response: str, context: Dict) -> str:
        """Replace placeholders like {time} with actual values."""
        if "{time}" in response:
            response = response.replace("{time}", datetime.now().strftime("%H:%M:%S"))
        if "{date}" in response:
            response = response.replace("{date}", datetime.now().strftime("%B %d, %Y"))
        return response


class IntentMatcher:
    """
    Handles pattern matching and intent detection using precompiled regex.
    This is the core of the NLP pattern matching.
    """
    
    def __init__(self):
        # Store compiled regex patterns per intent for fast matching
        self.compiled_patterns: Dict[str, List[re.Pattern]] = {}
    
    def compile_patterns(self, rules: List[Rule]) -> None:
        """
        Pre-compile all regex patterns from the rules for performance.
        This is called once when the chatbot is initialized.
        """
        for rule in rules:
            self.compiled_patterns[rule.intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in rule.patterns
            ]
    
    def match(self, user_input: str, rules: List[Rule]) -> Tuple[Optional[Rule], Optional[re.Match]]:
        """
        Match user input against all rules (sorted by priority).
        Returns the first matching rule and the regex match object.
        """
        user_input = user_input.lower().strip()
        
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            patterns = self.compiled_patterns.get(rule.intent, [])
            for pattern in patterns:
                match = pattern.search(user_input)
                if match:
                    return rule, match  # Stop at first match (priority order)
        
        return None, None  # No rule matched


class ConversationContext:
    """
    Manages conversation state and history.
    This gives the chatbot a sense of "flow" – it knows what was said before.
    """
    
    def __init__(self, max_history: int = 10):
        self.history: List[Dict] = []          # List of exchanges
        self.max_history = max_history         # Keep only last N exchanges
        self.user_name: Optional[str] = None   # Could store user's name
        self.last_intent: Optional[str] = None # Last detected intent
    
    def add_exchange(self, user_input: str, response: str, intent: str) -> None:
        """Store one turn of conversation."""
        self.history.append({
            "user": user_input,
            "bot": response,
            "intent": intent,
            "timestamp": datetime.now()
        })
        self.last_intent = intent
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_last_user_message(self) -> Optional[str]:
        """Return the last user message (useful for context-aware responses)."""
        return self.history[-1]["user"] if self.history else None


class RuleBasedChatbot:
    """
    Main chatbot class – orchestrates rules, matching, context, and response generation.
    This is the facade for the entire rule-based system.
    """
    
    def __init__(self, personality: Personality = Personality.CASUAL):
        self.personality = personality
        self.rules: List[Rule] = []
        self.context = ConversationContext()
        self.matcher = IntentMatcher()
        self._initialize_rules()          # Define all conversation rules
        self.matcher.compile_patterns(self.rules)  # Precompile regex patterns
    
    def _initialize_rules(self) -> None:
        """
        Define all conversation rules.
        Each rule contains regex patterns, responses per personality, priority, and optional handler.
        """
        self.rules = [
            # Priority 1: Exit commands – highest priority so they always work
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
            
            # Greetings – priority 2
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
            
            # Jokes – priority 3 (lower than greetings/time/help)
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
            
            # Help command
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
            
            # Calculator – uses a handler function for dynamic responses
            Rule(
                intent="CALCULATE",
                patterns=[r"(\d+)\s*([+\-*/])\s*(\d+)"],
                responses={p: [] for p in Personality},  # Empty, because handler is used
                priority=1,
                handler=self._calculate
            ),
            
            # Default fallback – catches anything that didn't match previous rules
            Rule(
                intent="UNKNOWN",
                patterns=[r".*"],  # Matches everything
                responses={
                    Personality.FORMAL: ["I don't understand. Please rephrase.", "Could you clarify?"],
                    Personality.CASUAL: ["Hmm, not sure I got that 🤔", "Can you say that differently?"],
                    Personality.SARCASTIC: ["Uh... what?", "That made no sense to me."]
                },
                priority=999  # Lowest priority – only if nothing else matches
            ),
        ]
    
    def _calculate(self, match: re.Match) -> str:
        """
        Handler for calculator intent.
        Evaluates arithmetic expression and returns formatted result based on personality.
        """
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
                
                # Personality-specific formatting
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
        """
        Main method to get bot response.
        Steps:
        1. Check for exit command first (priority override)
        2. Match user input against rules using IntentMatcher
        3. If rule has a handler (calculator), use it; else pick random response
        4. Update conversation context
        5. Return response text, intent, and exit flag
        """
        # Quick exit check (also covered by EXIT rule, but we handle early for clarity)
        if re.search(r"\b(bye|goodbye|exit|quit)\b", user_input.lower()):
            return {"text": self._get_response_for_intent("EXIT"), "intent": "EXIT", "should_exit": True}
        
        # Match intent using regex patterns
        rule, match = self.matcher.match(user_input, self.rules)
        
        if not rule:
            # Fallback to UNKNOWN rule (should never happen because UNKNOWN matches .*)
            rule = next(r for r in self.rules if r.intent == "UNKNOWN")
        
        # Generate response text
        if rule.handler and match:
            response_text = rule.handler(match)   # Dynamic response (calculator)
        else:
            response_text = self._get_response_for_intent(rule.intent)  # Static response
        
        # Store in conversation history
        self.context.add_exchange(user_input, response_text, rule.intent)
        
        return {
            "text": response_text,
            "intent": rule.intent,
            "should_exit": False
        }
    
    def _get_response_for_intent(self, intent: str) -> str:
        """Pick a random response for the given intent and current personality."""
        rule = next((r for r in self.rules if r.intent == intent), None)
        if rule and rule.responses.get(self.personality):
            return random.choice(rule.responses[self.personality])
        return "I'm not sure how to respond to that."
    
    def set_personality(self, personality: Personality) -> None:
        """Change bot personality on the fly."""
        self.personality = personality
    
    def get_stats(self) -> Dict:
        """Return statistics about the rule engine and conversation."""
        return {
            "total_rules": len(self.rules),
            "total_patterns": sum(len(r.patterns) for r in self.rules),
            "history_length": len(self.context.history),
            "current_personality": self.personality.value
        }


def run_cli():
    """
    Command-line interface for the chatbot.
    Allows direct interaction without web server.
    """
    bot = RuleBasedChatbot(Personality.CASUAL)
    
    print("\n" + "="*50)
    print("RULE-BASED CHATBOT (CLI MODE)")
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