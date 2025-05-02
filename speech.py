<<<<<<< HEAD
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr

# Set your API key
genai.configure(api_key="AIzaSyDmcV7dMHwZUrJE9bjEcnMntcN4RWGwG7g")

# Define system prompt
SYSTEM_PROMPT = """
You are Charusat Saarthi, an AI assistant designed to help visitors at Charusat University.
Always greet the user warmly before asking how you can assist them.
You have detailed knowledge about the university's history, departments, admissions process, events, and general FAQs, including colleges like CSPIT, DEPSTAR, CMPICA, RPCP, and IIIM at Charusat University.
Your responses should be informative, friendly, and personalized while ensuring a pleasant experience for the user.
Strictly answer in only one paragraph, not more than that.
If a user asks about CSPIT or other colleges, provide full details. For example, CSPIT stands for Chandubhai S. Patel Institute of Technology, and similarly, provide details for DEPSTAR, CMPICA, RPCP, and IIIM.
If you were asked questions other that charusat university or charusat saarthi, then you should answer that "The answer of this question is  out of my knowledge. Please ask questions related to charusat university only."
If asked 'Who are you?' or 'What is your goal?', respond with: 'I am Charusat Saarthi, and my aim is to help people navigate Charusat University.'
Do not pronounce asterisks (*) when responding.
"""

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak_text(text):
    """
    Function to convert text to speech.
    """
    engine.say(text)
    engine.runAndWait()

def listen_to_speech():
    """
    Function to capture user's speech and convert it to text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        try:
            audio = recognizer.listen(source, timeout=5)  # Listen for speech
            user_query = recognizer.recognize_google(audio)  # Convert speech to text
            print(f"You: {user_query}")
            return user_query.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand. Please repeat.")
            speak_text("Sorry, I couldn't understand. Please repeat.")
            return None
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
            speak_text("Speech recognition service is unavailable.")
            return None

def get_gemini_response(user_query, chat):
    """
    Function to generate a response using Google Gemini API with ongoing conversation context.
    """
    try:
        response = chat.send_message(user_query)
        return response.text
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return "Sorry, I'm having trouble answering that question."

def charusat_saarthi_chat():
    """
    Main function to keep the conversation going until the user exits.
    """
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat()

    greeting = "Hello! I am Charusat Saarthi. How can I assist you today?"
    print(f"Charusat Saarthi: {greeting}")
    speak_text(greeting)

    while True:
        user_query = listen_to_speech()
        
        if user_query in ["exit", "bye", "quit"]:
            farewell = "Goodbye! Have a great day."
            print(f"Charusat Saarthi: {farewell}")
            speak_text(farewell)
            break

        if user_query:  # Proceed only if speech was recognized
            response = get_gemini_response(user_query, chat)
            print(f"Charusat Saarthi: {response}")
            speak_text(response)

# Start the interactive voice chat
charusat_saarthi_chat()
=======
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import json
import random
import time
import threading
import os
import logging
from datetime import datetime
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("saarthi_conversation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Saarthi")

load_dotenv()
API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

# Define enhanced system prompt with detailed knowledge
SYSTEM_PROMPT = """
You are Charusat Saarthi, a friendly robot guide at Charusat University. Your responses must be:
1. Friendly and conversational with a warm, helpful tone
2. Concise yet informative (typically 2-3 sentences)
3. Personalized to the visitor's needs
4. Focused exclusively on Charusat University information

Key information about Charusat University:
- Full name: Charotar University of Science and Technology
- Location: Changa, Gujarat, India
- Established: 2009
- Type: Private university recognized by UGC

Main institutes:
- CSPIT: Chandubhai S Patel Institute of Technology (Engineering programs)
- DEPSTAR: Devang Patel Institute of Advance Technology and Research
- RPCP: Ramanbhai Patel College of Pharmacy
- IIIM: Indukaka Ipcowala Institute of Management
- PDPIAS: P.D. Patel Institute of Applied Sciences
- MTIN: Manikaka Topawala Institute of Nursing
- ARIP: Ashok and Rita Patel Institute of Physiotherapy

When a visitor asks about navigation to any building, ONLY say: "I'll guide you to [destination]. Please follow me as I navigate there." - do not provide walking directions.

If asked about anything unrelated to Charusat University, politely redirect by saying: "I'm specialized in Charusat University information. I'd be happy to tell you about our campus, programs, or facilities instead."

For questions about university events, mention: "Charusat hosts various events like Sparsh cultural festival, technical competitions, sports tournaments, and academic conferences."

If someone asks "Who are you?", respond with: "I'm Saarthi, your autonomous robot guide for Charusat University. I can help you navigate campus and answer questions about our programs and facilities."
"""

class SaarthiSpeechModule:
    def __init__(self):
        """Initialize the Saarthi Speech Module with all required components"""
        self.setup_voice_engine()
        self.setup_speech_recognition()
        self.load_phrases()
        self.initialize_gemini()
        self.navigation_active = False
        self.current_destination = None
        self.conversation_context = {
            "interaction_count": 0,
            "last_intent": None,
            "last_topic": None,
            "last_interaction_time": datetime.now(),
            "destinations_discussed": set()
        }
        
        logger.info("Saarthi Speech Module initialized successfully")

    def setup_voice_engine(self):
        """Configure text-to-speech engine with natural voice settings"""
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        
        # Choose a voice that sounds friendly - adjust index based on available voices
        # Test different voices on your system to find the most natural one
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)  # Often female voice (index 1) sounds friendlier
        
        # Adjust speed (words per minute) - lower is slower, higher is faster
        self.engine.setProperty('rate', 175)  # Slightly slower than default for clarity
        
        # Adjust volume (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)

    def setup_speech_recognition(self):
        """Configure speech recognition with noise handling"""
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True  # Adapt to ambient noise
        self.recognizer.energy_threshold = 4000  # Higher threshold for noisy environments
        self.recognizer.pause_threshold = 0.8  # Shorter pause for more responsive interaction
        
        # For improved noise resistance, you might want to use:
        # self.recognizer.dynamic_energy_adjustment_ratio = 1.5

    def load_phrases(self):
        """Load friendly phrases for more engaging interactions"""
        # Create phrases file if it doesn't exist
        phrases_file = "friendly_phrases.json"
        
        if not os.path.exists(phrases_file):
            default_phrases = {
                "greetings": [
                    "Hello! Welcome to Charusat University.",
                    "Hi there! I'm Saarthi, your campus guide.",
                    "Greetings! It's a pleasure to welcome you to Charusat.",
                    "Welcome to Charusat University! I'm Saarthi, at your service.",
                    "Hello! I'm excited to show you around our campus."
                ],
                "listening_indicators": [
                    "I'm listening...",
                    "Go ahead, I'm all ears!",
                    "Please tell me how I can help.",
                    "What would you like to know?",
                    "How can I assist you today?"
                ],
                "acknowledgments": [
                    "I understand.",
                    "Got it!",
                    "I see what you mean.",
                    "That makes sense.",
                    "I hear you."
                ],
                "navigation_start": [
                    "I'll guide you to {destination}. Please follow me.",
                    "Let's head to {destination} together. Please follow me.",
                    "I'll take you to {destination} now. Please follow along.",
                    "Let me show you the way to {destination}. Please follow me.",
                    "I'd be happy to guide you to {destination}. Please come with me."
                ],
                "navigation_comments": [
                    "We're now passing by the central garden area.",
                    "This pathway connects most of the academic buildings.",
                    "The building on your right houses several research laboratories.",
                    "Many students gather in this area between classes.",
                    "This area hosts many of our outdoor cultural events."
                ],
                "farewells": [
                    "Goodbye! Enjoy your time at Charusat University.",
                    "Have a great day! Feel free to find me if you need help again.",
                    "It was a pleasure assisting you. Goodbye!",
                    "Thank you for visiting Charusat University. Goodbye!",
                    "Farewell! I hope you enjoyed our interaction."
                ],
                "misheard": [
                    "I'm sorry, I didn't catch that. Could you please repeat?",
                    "Would you mind repeating that? I didn't hear clearly.",
                    "I missed what you said. Could you say it again?",
                    "I didn't quite get that. Could you repeat it, please?",
                    "Sorry about that. Could you say it again?"
                ],
                "thinking": [
                    "Let me think about that for a moment...",
                    "I'm finding the best answer for you...",
                    "Let me get that information for you...",
                    "Just a moment while I process that...",
                    "I'm working on your question..."
                ]
            }
            
            with open(phrases_file, 'w') as f:
                json.dump(default_phrases, f, indent=4)
        
        with open(phrases_file, 'r') as f:
            self.phrases = json.load(f)

    def initialize_gemini(self):
        """Initialize the Gemini model with appropriate settings"""
        try:
            # Use gemini-pro for best performance
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config={
                    "temperature": 0.7,  # Higher values make output more creative
                    "top_p": 0.95,       # Control diversity
                    "top_k": 40,         # Control diversity
                    "max_output_tokens": 200,  # Limit response length
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )
            
            # Start chat with system prompt
            self.chat = self.model.start_chat(history=[
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "model", "parts": ["I understand my role as Charusat Saarthi. I'll follow these guidelines in all my interactions."]}
            ])
            
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.speak("I'm experiencing a technical issue. Please wait a moment while I restart my systems.")
            raise

    def get_random_phrase(self, category):
        """Get a random phrase from the specified category"""
        if category in self.phrases and self.phrases[category]:
            return random.choice(self.phrases[category])
        return ""

    def speak(self, text, wait=True):
        """Convert text to speech with improved expression"""
        logger.info(f"Saarthi speaking: {text}")
        print(f"Saarthi: {text}")
        
        # Add slight pauses for natural speech rhythm
        processed_text = text.replace('. ', '. <break time="300ms"/> ')
        processed_text = processed_text.replace(', ', ', <break time="200ms"/> ')
        processed_text = processed_text.replace('? ', '? <break time="300ms"/> ')
        processed_text = processed_text.replace('! ', '! <break time="300ms"/> ')
        
        # Remove any SSML tags that pyttsx3 can't handle
        for tag in ['<break time="300ms"/>', '<break time="200ms"/>']:
            processed_text = processed_text.replace(tag, '')
        
        # Speak the text
        self.engine.say(processed_text)
        if wait:
            self.engine.runAndWait()

    def listen(self, timeout=7, phrase_time_limit=10):
        """Listen for user speech with improved error handling"""
        phrase = self.get_random_phrase("listening_indicators")
        print(f"Saarthi: {phrase}")
        
        with sr.Microphone() as source:
            # Dynamically adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                # Indicate processing
                thinking_phrase = self.get_random_phrase("thinking")
                print(f"Saarthi: {thinking_phrase}")
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    logger.info(f"User said: {text}")
                    print(f"You: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    misheard_phrase = self.get_random_phrase("misheard")
                    self.speak(misheard_phrase)
                    logger.warning("Speech recognition failed: Unknown value")
                    return None
                except sr.RequestError as e:
                    self.speak("I'm having trouble connecting to the speech recognition service. Please try again.")
                    logger.error(f"Speech recognition request error: {e}")
                    return None
                
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything. If you need assistance, please let me know.")
                logger.warning("Speech recognition timed out")
                return None
            except Exception as e:
                self.speak("I encountered an unexpected issue while listening. Let's try again.")
                logger.error(f"Unexpected error in speech recognition: {e}")
                return None

    def detect_navigation_intent(self, text):
        """Check if the user is asking for navigation to a specific building"""
        text = text.upper()
        destinations = ["CSPIT", "DEPSTAR", "RPCP", "IIIM", "PDPIAS", "MTIN", "ARIP"]
        
        # Look for navigation phrases
        nav_phrases = ["take me to", "guide me to", "go to", "where is", "how do i get to", 
                      "how do i find", "show me to", "lead me to", "navigate to"]
        
        has_nav_intent = any(phrase in text.lower() for phrase in nav_phrases)
        
        # Check for destinations
        detected_destination = None
        for dest in destinations:
            if dest in text:
                detected_destination = dest
                break
        
        # If we found both navigation intent and a destination
        if has_nav_intent and detected_destination:
            return detected_destination
        # If only destination is mentioned (implicit navigation)
        elif detected_destination:
            return detected_destination
        
        return None

    def start_navigation(self, destination):
        """Begin navigation to the specified destination"""
        self.navigation_active = True
        self.current_destination = destination
        
        # Use appropriate navigation phrase
        nav_phrase = self.get_random_phrase("navigation_start").format(destination=destination)
        self.speak(nav_phrase)
        
        # Simulate navigation in a separate thread
        threading.Thread(target=self.simulate_navigation, args=(destination,), daemon=True).start()
    
    def simulate_navigation(self, destination):
        """Simulate the navigation process with commentary"""
        try:
            # Get random selection of navigation comments
            comments = random.sample(self.phrases["navigation_comments"], 
                                   min(3, len(self.phrases["navigation_comments"])))
            
            # Simulate walking and provide commentary
            for i, comment in enumerate(comments):
                if not self.navigation_active:
                    break
                    
                # Simulate walking time
                time.sleep(4)
                
                # Only give commentary if still navigating
                if self.navigation_active:
                    self.speak(comment)
            
            # Simulate arrival time
            if self.navigation_active:
                time.sleep(5)
                self.speak(f"We have arrived at {destination}. Is there anything specific you'd like to know about this building?")
                
            self.navigation_active = False
            
        except Exception as e:
            logger.error(f"Error in navigation simulation: {e}")
            self.navigation_active = False

    def check_for_farewell(self, text):
        """Check if the user is saying goodbye"""
        farewell_phrases = ["bye", "goodbye", "see you", "farewell", "thanks for your help", 
                          "that's all", "exit", "quit", "end conversation"]
        
        return any(phrase in text.lower() for phrase in farewell_phrases)

    def update_conversation_context(self, user_input, response):
        """Update the conversation context based on the interaction"""
        self.conversation_context["interaction_count"] += 1
        self.conversation_context["last_interaction_time"] = datetime.now()
        
        # Check for navigation intent and update context
        destination = self.detect_navigation_intent(user_input)
        if destination:
            self.conversation_context["last_intent"] = "navigation"
            self.conversation_context["destinations_discussed"].add(destination)
        
        # Simple topic detection
        topics = {
            "program": ["program", "course", "degree", "study"],
            "facility": ["facility", "library", "hostel", "lab", "canteen"],
            "event": ["event", "festival", "activity", "cultural", "technical"],
            "admission": ["admission", "apply", "entrance", "test", "fee"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                self.conversation_context["last_topic"] = topic
                break

    def process_query_with_gemini(self, query):
        """Process query using Gemini API with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get response from Gemini
                response = self.chat.send_message(query)
                return response.text
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    return "I'm having trouble connecting to my knowledge database right now. Could you please ask me something else about Charusat University?"
    
    def start_interaction(self):
        """Begin the interaction with a warm greeting"""
        greeting = self.get_random_phrase("greetings")
        self.speak(greeting)
        
        while True:
            # Listen for user input
            user_input = self.listen()
            
            # Skip processing if nothing was heard
            if not user_input:
                continue
            
            # Check for navigation intent
            destination = self.detect_navigation_intent(user_input)
            if destination:
                self.start_navigation(destination)
                continue
            
            # Check for farewell intent
            if self.check_for_farewell(user_input):
                farewell = self.get_random_phrase("farewells")
                self.speak(farewell)
                break
            
            # Process with Gemini
            response = self.process_query_with_gemini(user_input)
            
            # Update conversation context
            self.update_conversation_context(user_input, response)
            
            # Speak the response
            self.speak(response)
            
            # After a lengthy conversation, offer additional help
            if self.conversation_context["interaction_count"] % 5 == 0:
                self.speak("Is there anything else you'd like to know about Charusat University?")

# Main execution
if __name__ == "__main__":
    try:
        print("Starting Charusat Saarthi Speech Module...")
        saarthi = SaarthiSpeechModule()
        saarthi.start_interaction()
    except KeyboardInterrupt:
        print("\nSaarthi Speech Module terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Critical error in main execution: {e}", exc_info=True)
>>>>>>> 4a0f030 (Updated speech module)
