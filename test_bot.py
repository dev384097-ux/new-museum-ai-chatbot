from chatbot_engine import MuseumChatbot

def test_chatbot():
    bot = MuseumChatbot()
    
    # Test cases: (message, expected_intent or key_fragment)
    tests = [
        ("Book tickets", "exhibit_prefix"),
        ("What are the hours?", "9:00 AM"),
        ("సమయం", "మంగళవారం-ఆదివారం"), # Telugu timing
        ("वेळ", "मंगळवार-रविवार"),      # Marathi timing
        ("সময়", "মঙ্গলবার-রবিবার"),     # Bengali timing
        ("समय", "मंगलवार-रविवार"),      # Hindi timing
        ("Tell me about the history", "Established in 1978"),
        ("Is there a cafe?", "Curator's Cafe"),
        ("Where can I park?", "North Wing")
    ]
    
    for msg, expected in tests:
        state = {'lang': 'en', 'state': 'idle'}
        resp, new_state = bot.process_message(msg, state)
        print(f"Query: {msg}")
        print(f"Response: {resp[:100]}...")
        if expected.lower() in resp.lower():
            print("Status: PASS")
        else:
            print(f"Status: FAIL (Expected fragment: {expected})")
        print("-" * 20)

if __name__ == "__main__":
    test_chatbot()
