import speech_recognition as sr
from gtts import gTTS
from IPython.display import Audio, display, clear_output
import ipywidgets as widgets
from datetime import date, timedelta, datetime
import random
import webbrowser
import os
import tempfile
from pydub import AudioSegment

try:
    from ollama import chat
    OLLAMA_AVAILABLE = True
    print("✅ Using gemma2:2b")
except ImportError:
    OLLAMA_AVAILABLE = False
    print("❌ Ollama not found.")

class Bezaleel:
    def __init__(self):
        self.log_file = "conversation_log.txt"
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.start_log()
        if OLLAMA_AVAILABLE:
            print("🧠 AI Mode: gemma2:2b is active")
        else:
            print("⚠️ AI mode disabled")

    def start_log(self):
        today = date.today().strftime("%Y-%m-%d %H:%M")
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Conversation Started: {today} ===\n")
        except:
            pass

    def remember(self, command: str):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"User: {command}\n")
        except:
            pass

    def speak(self, text: str):
        print(f"🗣️ Bezaleel: {text}")
        try:
            tts = gTTS(text=text[:400], lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                temp_filename = tmp.name
                tts.save(temp_filename)
            
            audio = AudioSegment.from_mp3(temp_filename)
            louder_audio = audio + 18
            louder_audio = louder_audio.normalize()
            
            louder_filename = temp_filename.replace(".mp3", "_loud.mp3")
            louder_audio.export(louder_filename, format="mp3")
            
            display(Audio(louder_filename, autoplay=True))
        except:
            print(f"→ Bezaleel: {text}")

    def smart_ai_response(self, user_input: str):
        if not OLLAMA_AVAILABLE:
            self.speak("AI mode is not available.")
            return
        
        self.speak("Thinking...")
        try:
            response = chat(
                model='gemma2:2b',
                messages=[{'role': 'user', 'content': user_input}],
                options={
                    'temperature': 0.7,
                    'num_ctx': 1024,
                    'num_predict': 1800      # High limit for longer answers
                }
            )
            answer = response['message']['content']
            if len(answer) > 3500:
                answer = answer[:3500] + "\n\n... (Very long response)"
            self.speak(answer)
        except Exception as e:
            print(f"AI Error: {e}")
            self.speak("Sorry, it took too long.")

    def analyze(self, command: str):
        if not command:
            return
        cmd = command.lower().strip()
        self.remember(command)

        if any(word in cmd for word in ["smart", "ai", "think", "explain", "what is", "tell me about", "how does", "detail"]):
            self.smart_ai_response(command)
            return

        if cmd.startswith("open") or "play song" in cmd or "play music" in cmd:
            self.open_things(cmd)
        elif "introduce yourself" in cmd or "who are you" in cmd:
            self.speak("Hello! I am Bezaleel, your digital assistant.")
        elif "how are you" in cmd:
            self.speak("I am doing great, thank you!")
        elif "joke" in cmd:
            self.tell_joke()
        elif "quote" in cmd or "motivate" in cmd:
            self.give_quote()
        elif "news" in cmd:
            self.get_news()
        elif "weather" in cmd:
            self.get_weather()
        elif any(word in cmd for word in ["time", "date", "today", "yesterday"]):
            self.understand_time(cmd)
        else:
            self.speak("Searching Google for you.")
            webbrowser.open(f"https://www.google.com/search?q={command.replace(' ', '+')}")

    def tell_joke(self):
        jokes = ["Why don't programmers prefer dark mode? Because light attracts bugs!",
                 "Why did the scarecrow win an award? He was outstanding in his field!"]
        self.speak(random.choice(jokes))

    def give_quote(self):
        quotes = ["The only way to do great work is to love what you do.",
                  "Believe you can and you're halfway there."]
        self.speak(random.choice(quotes))

    def get_news(self):
        self.speak("Opening latest news.")
        webbrowser.open("https://news.google.com")

    def open_things(self, command: str):
        cmd = command.lower()
        if "jiosaavn" in cmd:
            self.speak("Opening JioSaavn.")
            webbrowser.open("https://www.jiosaavn.com")
        elif "spotify" in cmd:
            self.speak("Opening Spotify.")
            webbrowser.open("https://open.spotify.com")
        elif "play song" in cmd or "play music" in cmd:
            song = cmd.replace("play song", "").replace("play music", "").strip()
            if song:
                self.speak(f"Searching {song} on YouTube Music.")
                webbrowser.open(f"https://music.youtube.com/search?q={song.replace(' ', '+')}")
            else:
                self.speak("Opening YouTube Music.")
                webbrowser.open("https://music.youtube.com")
        else:
            self.speak("Opening website.")
            webbrowser.open(f"https://www.google.com/search?q={cmd}")

    def get_weather(self):
        self.speak("Weather service is currently unavailable.")

    def understand_time(self, command: str):
        today = date.today()
        now = datetime.now()
        if "time" in command:
            self.speak(now.strftime("The current time is %I:%M %p"))
        else:
            self.speak(today.strftime("Today is %B %d, %Y"))


# ====================== UI ======================
b = Bezaleel()

output_area = widgets.Output()
chat_input = widgets.Text(
    placeholder="Try: smart give me a detailed explanation of how the internet works",
    description="You:",
    layout=widgets.Layout(width='70%')
)
send_button = widgets.Button(description="Send", button_style="primary")

def on_send(widget):
    with output_area:
        clear_output(wait=True)
        user_text = chat_input.value.strip()
        if user_text:
            print(f"👤 You: {user_text}")
            b.analyze(user_text)
            chat_input.value = ""

send_button.on_click(on_send)

text_ui = widgets.VBox([widgets.HTML("<h3>🟢 Bezaleel Digital Assistant</h3>"), output_area, widgets.HBox([chat_input, send_button])])

voice_button = widgets.Button(description="🎤 Speak to Bezaleel", button_style="success", layout=widgets.Layout(height='50px'))
voice_output = widgets.Output()

def listen_voice(widget):
    with voice_output:
        clear_output()
        print("🎤 Listening...")
        try:
            with b.microphone as source:
                b.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio = b.recognizer.listen(source, timeout=8, phrase_time_limit=8)
            command = b.recognizer.recognize_google(audio)
            print(f"👤 You said: {command}")
            b.analyze(command)
        except:
            print("Sorry, I didn't understand.")
            b.speak("Sorry, I didn't catch that.")

voice_button.on_click(listen_voice)

voice_ui = widgets.VBox([widgets.HTML("<b>Voice Mode:</b> Click and speak"), widgets.HBox([voice_button, voice_output])])

display(text_ui)
display(voice_ui)

print("\n✅ Bezaleel is ready with gemma2:2b!")
print("Use 'smart' before your question for detailed answers.")
