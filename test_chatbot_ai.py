from chatbot_engine import MuseumChatbot
import json
import sys

# Ensure UTF-8 output for Windows terminals
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_chatbot():
    bot = MuseumChatbot()
    
    test_cases = [
        {"msg": "Hello", "description": "English Greeting"},
        {"msg": "नमस्ते", "description": "Hindi Greeting"},
        {"msg": "பார்க்கிங் எங்கே?", "description": "Tamil Parking Query"},
        {"msg": "আমি কি টিকিট কিনতে পারি?", "description": "Bengali Booking Intent"},
        {"msg": "1", "description": "Exhibition Selection (Number)"},
        {"msg": "2", "description": "Ticket Count (Number)"}
    ]
    
    state = {'state': 'idle'}
    print("--- Starting Multilingual AI Chatbot Logic Test ---")
    
    for case in test_cases:
        print(f"\nTesting: {case['description']} ('{case['msg']}')")
        try:
            response, state = bot.process_message(case['msg'], state)
            print(f"BOT REPLY: {response}")
            print(f"NEW STATE: {state.get('state', 'idle')} (Lang: {state.get('lang', 'en')})")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_chatbot()
