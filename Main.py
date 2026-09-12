  import os
import re
import json
import threading
import subprocess
import webbrowser
import requests

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

# =========================================================
# JARVIS CONFIGURATION
# =========================================================

DEEPSEEK_API_KEY = os.environ.get("sk-or-v1-7be09bae890983593859f849a69a2f647abcb01a21b5eba9d40f981dd8f666ed105:12 PM", "")

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

MODEL = "deepseek-chat"

PC_SERVER = "http://192.168.1.100:5000"

# Change this to the IP address of your PC.
# Example:
# PC_SERVER = "http://192.168.1.5:5000"


# =========================================================
# JARVIS AI
# =========================================================

SYSTEM_PROMPT = """
You are JARVIS, a multilingual personal AI assistant.

You are concise, intelligent and practical.

Supported languages:
English
Hindi
Spanish
Chinese
Japanese
Russian

Important:
- Reply in the language requested by the user.
- If the user speaks Hindi, reply in Hindi.
- If the user speaks English, reply in English.
- Never claim that you performed an action unless the program actually performed it.
- When an action should be performed by the device, identify the action clearly.
- Do not invent real-time information.
"""

conversation = []


def ask_deepseek(user_text):

    if not DEEPSEEK_API_KEY:
        return "DeepSeek API key is not connected."

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(conversation[-10:])

    messages.append({
        "role": "user",
        "content": user_text
    })

    try:

        response = requests.post(
            DEEPSEEK_URL,
            headers={
                "Authorization": "Bearer " + DEEPSEEK_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.5,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        conversation.append({
            "role": "user",
            "content": user_text
        })

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:

        return "DeepSeek error: " + str(e)


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(query):

    try:

        url = "https://www.google.com/search"

        params = {
            "q": query
        }

        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        return r.url

    except Exception:

        return "https://www.google.com/search?q=" + requests.utils.quote(query)


# =========================================================
# ANDROID ACTIONS
# =========================================================

def android_action(command):

    c = command.lower()

    # -----------------------------------------------------
    # YouTube
    # -----------------------------------------------------

    if "open youtube" in c or "youtube kholo" in c:

        webbrowser.open(
            "https://www.youtube.com"
        )

        return "Opening YouTube."

    # -----------------------------------------------------
    # Google
    # -----------------------------------------------------

    if "open google" in c or "google kholo" in c:

        webbrowser.open(
            "https://www.google.com"
        )

        return "Opening Google."

    # -----------------------------------------------------
    # Gmail
    # -----------------------------------------------------

    if "open gmail" in c or "gmail kholo" in c:

        webbrowser.open(
            "https://mail.google.com"
        )

        return "Opening Gmail."

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search_words = [
        "search for",
        "search",
        "google",
        "find"
    ]

    for word in search_words:

        if c.startswith(word):

            query = command[len(word):].strip()

            if query:

                url = web_search(query)

                webbrowser.open(url)

                return "Searching for " + query

    return None


# =========================================================
# PC CONTROL
# =========================================================

def pc_request(endpoint, data=None):

    try:

        url = PC_SERVER + endpoint

        response = requests.post(
            url,
            json=data or {},
            timeout=10
        )

        return response.json()

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


def pc_action(command):

    c = command.lower()

    # -----------------------------------------------------
    # Chrome
    # -----------------------------------------------------

    if "open chrome on pc" in c:

        result = pc_request(
            "/open_app",
            {
                "app": "chrome"
            }
        )

        if result.get("success"):
            return "Opening Chrome on your PC."

    # -----------------------------------------------------
    # YouTube on PC
    # -----------------------------------------------------

    if "open youtube on pc" in c:

        result = pc_request(
            "/open_url",
            {
                "url": "https://youtube.com"
            }
        )

        if result.get("success"):
            return "Opening YouTube on your PC."

    # -----------------------------------------------------
    # PC volume
    # -----------------------------------------------------

    if "volume up" in c:

        result = pc_request(
            "/volume",
            {
                "action": "up"
            }
        )

        if result.get("success"):
            return "Increasing PC volume."

    if "volume down" in c:

        result = pc_request(
            "/volume",
            {
                "action": "down"
            }
        )

        if result.get("success"):
            return "Decreasing PC volume."

    # -----------------------------------------------------
    # PC lock
    # -----------------------------------------------------

    if "lock my pc" in c:

        result = pc_request("/lock")

        if result.get("success"):
            return "Locking your PC."

    return None


# =========================================================
# COMMAND PROCESSOR
# =========================================================

def process_command(command):

    command = command.strip()

    if not command:
        return "Please give me a command."

    # Android action
    result = android_action(command)

    if result:
        return result

    # PC action
    result = pc_action(command)

    if result:
        return result

    # Otherwise ask AI
    return ask_deepseek(command)


# =========================================================
# TEXT TO SPEECH
# =========================================================

def speak(text):

    try:

        import pyttsx3

        engine = pyttsx3.init()

        engine.say(text)

        engine.runAndWait()

    except Exception:

        pass


# =========================================================
# GUI
# =========================================================

class JarvisUI(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=10,
            padding=15,
            **kwargs
        )

        self.status = Label(
            text="JARVIS ONLINE",
            font_size=25,
            size_hint_y=0.15
        )

        self.add_widget(self.status)

        self.output = Label(
            text="Hello. I am JARVIS.",
            font_size=18,
            halign="left",
            valign="top"
        )

        self.add_widget(self.output)

        self.input_box = TextInput(
            hint_text="Type a command...",
            multiline=False,
            size_hint_y=0.15
        )

        self.add_widget(self.input_box)

        self.send_button = Button(
            text="SEND",
            size_hint_y=0.15
        )

        self.send_button.bind(
            on_press=self.send_command
        )

        self.add_widget(self.send_button)

        self.voice_button = Button(
            text="🎙 SPEAK",
            size_hint_y=0.15
        )

        self.voice_button.bind(
            on_press=self.voice_command
        )

        self.add_widget(self.voice_button)

    def send_command(self, instance):

        command = self.input_box.text.strip()

        if not command:
            return

        self.output.text = "You: " + command

        self.input_box.text = ""

        threading.Thread(
            target=self.run_command,
            args=(command,),
            daemon=True
        ).start()

    def run_command(self, command):

        answer = process_command(command)

        Clock.schedule_once(
            lambda dt: self.show_answer(answer)
        )

        threading.Thread(
            target=speak,
            args=(answer,),
            daemon=True
        ).start()

    def show_answer(self, answer):

        self.output.text = answer

    def voice_command(self, instance):

        self.status.text = "LISTENING..."

        threading.Thread(
            target=self.listen,
            daemon=True
        ).start()

    def listen(self):

        try:

            import speech_recognition as sr

            recognizer = sr.Recognizer()

            with sr.Microphone() as source:

                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            text = recognizer.recognize_google(
                audio
            )

            Clock.schedule_once(
                lambda dt: self.process_voice(text)
            )

        except Exception as e:

            Clock.schedule_once(
                lambda dt: self.voice_error(str(e))
            )

    def process_voice(self, text):

        self.status.text = "PROCESSING..."

        self.input_box.text = text

        threading.Thread(
            target=self.run_command,
            args=(text,),
            daemon=True
        ).start()

    def voice_error(self, error):

        self.status.text = "VOICE ERROR"

        self.output.text = error


# =========================================================
# APP
# =========================================================

class JarvisApp(App):

    def build(self):

        Window.size = (400, 700)

        return JarvisUI()


if __name__ == "__main__":

    JarvisApp().run()
