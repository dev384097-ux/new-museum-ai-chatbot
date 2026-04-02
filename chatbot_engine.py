import re
import uuid
import random
from database import get_db_connection
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator

# Ensure consistent language detection
DetectorFactory.seed = 0

class TranslatorLayer:
    """Handles automatic language detection and seamless translation."""
    @staticmethod
    def detect_lang(text):
        t = text.lower().strip()
        # 1. Check for common English greetings/shorthand first to avoid 'fi' (Finnish) or other false positives
        if re.fullmatch(r'[a-zA-Z\s\d\!\?\.]{1,5}', t):
            if any(w in t for w in ['hi', 'hello', 'hey', 'help', 'ok', 'yes', 'no']):
                return 'en'

        try:
            # 2. Precise Script Detection for all 22+ Scheduled Indian Languages
            # Devanagari (Hindi, Marathi, Sanskrit, Konkani, Bodo, Dogri, Maithili, Nepali)
            if re.search(r'[\u0900-\u097F]', text): return 'hi'
            # Bengali (Bengali, Assamese, Manipuri)
            if re.search(r'[\u0980-\u09FF]', text): return 'bn'
            # Gurmukhi (Punjabi)
            if re.search(r'[\u0A00-\u0A7F]', text): return 'pa'
            # Gujarati
            if re.search(r'[\u0A80-\u0AFF]', text): return 'gu'
            # Oriya (Odia)
            if re.search(r'[\u0B00-\u0B7F]', text): return 'or'
            # Tamil
            if re.search(r'[\u0B80-\u0BFF]', text): return 'ta'
            # Telugu
            if re.search(r'[\u0C00-\u0C7F]', text): return 'te'
            # Kannada
            if re.search(r'[\u0C80-\u0CFF]', text): return 'kn'
            # Malayalam
            if re.search(r'[\u0D00-\u0D7F]', text): return 'ml'
            
            # 3. Fallback to probabilistic detection
            return detect(text)
        except:
            return 'en'

    @staticmethod
    def translate(text, target_lang='en', source_lang='auto'):
        if target_lang == source_lang:
            return text
        try:
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return translated
        except Exception as e:
            print(f"Translation Error: {e}")
            return text

class MuseumChatbot:
    def __init__(self):
        self.translator = TranslatorLayer()
        
        # Centralized Knowledge Base (English)
        self.BASE_CONFIG = {
            'greet': "Good day. I am the Virtual Curator. How may I assist you? I can help with 'tickets', 'timings', 'parking', 'cafe', or 'history'.",
            'exhib_prefix': "Here are our current exhibitions:<br>",
            'select_prompt': "Which exhibition number has caught your eye? (Reply with the number)",
            'count_prompt': "For how many guests shall I prepare these tickets?",
            'pay_prompt': "The total for <b>'{title}'</b> is ₹{total}. Proceed to payment?",
            'success': "Payment Successful! 🎉<br>Booking ID: {hash}",
            'error': "I apologize, I didn't quite grasp that. Try asking about 'parking', 'photography', or 'tickets'.",
            'cancel': "Reservation withdrawn.",
            'btn_text': "Proceed to Ledger",
            'kb': {
                'parking': "We offer secure valet parking in the North Wing. It is complimentary for ticket holders.",
                'photo': "Photography is encouraged in the main galleries, but flash is prohibited to preserve pigments.",
                'cafe': "The 'Curator's Cafe' on the 2nd floor offers artisanal refreshments and organic snacks until 5 PM.",
                'lost': "Found items are safely kept at the Security Desk near the main entrance.",
                'timing': "Museum Hours: 9:00 AM - 6:00 PM (Tuesday-Sunday). Closed on Mondays.",
                'history': "Established in 1978, this museum preserves India's rich scientific and cultural heritage through interactive galleries.",
                'location': "We are located near the National Mall. You can reach us via the 'Museum Station' on the Blue Line.",
                'accessibility': "The museum is fully wheelchair accessible with elevators connecting all floors. Wheelchairs are available for free at the entrance.",
                'membership': "Our 'Patron Program' offers unlimited entry and exclusive preview access for ₹2,000 annually.",
                'security': "Security is a top priority. Bags are scanned at the entry, and CCTV is monitored 24/7.",
                'souvenir': "Our gift shop is located at the exit, offering replicas, scientific kits, and traditional crafts.",
                'contact': "You can reach the administration at info@museumbot.gov.in or call +91-11-2345-6789."
            }
        }

        self.INTENTS = {
            'parking': [r'park', r'vehicle', r'car'],
            'photo': [r'photo', r'camera', r'flash', r'pic'],
            'cafe': [r'cafe', r'food', r'eat', r'hungry', r'restaurant', r'water', r'drink'],
            'lost': [r'lost', r'found', r'security', r'missing'],
            'timing': [r'timing', r'hours', r'open', r'close', r'when'],
            'history': [r'history', r'about', r'establish', r'old', r'who built'],
            'location': [r'location', r'where', r'reach', r'map', r'way', r'address'],
            'accessibility': [r'wheelchair', r'disab', r'lift', r'elevator', r'ramp'],
            'membership': [r'member', r'patron', r'subscrip', r'join'],
            'security': [r'security', r'guard', r'safe', r'bag'],
            'souvenir': [r'shop', r'gift', r'souvenir', r'replica'],
            'contact': [r'contact', r'email', r'phone', r'call', r'manager']
        }

    def process_message(self, message, state_data):
        raw_msg = message.strip()
        if not raw_msg: return "", state_data

        # 1. Detect Language and update state
        detected_lang = self.translator.detect_lang(raw_msg)
        
        # Keep existing language if input is just numbers (e.g. exhibition selection)
        if raw_msg.isdigit() and 'lang' in state_data:
            lang = state_data['lang']
        else:
            lang = detected_lang
            state_data['lang'] = lang
        
        # 2. Translate Input to English for internal processing
        msg_en = self.translator.translate(raw_msg, target_lang='en', source_lang=lang).lower()
        
        # 3. Core Logic (English)
        response_en, state_data = self._get_logic_response(msg_en, state_data)
        
        # 4. Translate Response back to User Language
        final_response = self.translator.translate(response_en, target_lang=lang, source_lang='en')
        
        return final_response, state_data

    def _get_logic_response(self, msg, state_data):
        state = state_data.get('state', 'idle')

        # A. GLOBAL FLOWS (Priority over KB)
        if re.search(r'\b(hi|hello|hey|greetings|namaste)\b', msg):
            return self.BASE_CONFIG['greet'], state_data

        if re.search(r'\b(book|ticket|buy|booking|reservation)\b', msg):
            state_data['state'] = 'awaiting_exhibition_selection'
            return self.BASE_CONFIG['select_prompt'] + "<br>" + self.format_exhibition_list(), state_data

        # B. Check Knowledge Base Intents
        for intent, patterns in self.INTENTS.items():
            if any(re.search(p, msg) for p in patterns):
                return self.BASE_CONFIG['kb'].get(intent, self.BASE_CONFIG['error']), state_data

        # C. State-Based Logic (Booking Flow)
        if state == 'awaiting_exhibition_selection':
            match = re.search(r'\d+', msg)
            if match:
                ex_id = int(match.group())
                conn = get_db_connection()
                exhibition = conn.execute('SELECT * FROM exhibitions WHERE id = ?', (ex_id,)).fetchone()
                conn.close()
                if exhibition:
                    state_data['exhibition'] = dict(exhibition)
                    state_data['state'] = 'awaiting_ticket_count'
                    return self.BASE_CONFIG['count_prompt'], state_data
            return self.BASE_CONFIG['select_prompt'], state_data

        elif state == 'awaiting_ticket_count':
            match = re.search(r'\d+', msg)
            if match:
                count = int(match.group())
                state_data['count'] = count
                state_data['state'] = 'awaiting_payment_confirm'
                total = count * state_data['exhibition']['price']
                state_data['total'] = total
                btn_html = f"<button class='cta-btn' style='padding:5px 15px; font-size:0.8rem; margin-top:10px;' onclick='openPaymentModal({total})'>{self.BASE_CONFIG['btn_text']} (₹{total})</button>"
                return self.BASE_CONFIG['pay_prompt'].format(title=state_data['exhibition']['title'], total=total) + "<br>" + btn_html, state_data
            return self.BASE_CONFIG['count_prompt'], state_data

        # D. Fallback
        return self.BASE_CONFIG['error'], state_data

    def format_exhibition_list(self):
        conn = get_db_connection()
        exhibs = conn.execute('SELECT * FROM exhibitions').fetchall()
        conn.close()
        resp = self.BASE_CONFIG['exhib_prefix']
        for e in exhibs:
            resp += f"<b>{e['id']}. {e['title']}</b> - ₹{e['price']}<br>"
        return resp

    def process_payment_success(self, state_data, user_id):
        lang = state_data.get('lang', 'en')
        ticket_hash = str(uuid.uuid4())[:8].upper()
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO bookings (user_id, visitor_name, exhibition_id, num_tickets, total_price, ticket_hash) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, 'Authenticated User', state_data['exhibition']['id'], state_data['count'], state_data['total'], ticket_hash)
        )
        conn.commit()
        conn.close()
        
        state_data['state'] = 'idle'
        success_msg_en = self.BASE_CONFIG['success'].format(hash=ticket_hash)
        final_msg = self.translator.translate(success_msg_en, target_lang=lang, source_lang='en')
        
        return {'success': True, 'chat_message': final_msg}, state_data
