"""
Personal Voice Assistant — Level 2 (Fixed)
=============================================
Now with Wikipedia search, calculator, and jokes!

Try saying:
  - "Tell me about the Eiffel Tower"
  - "What is 245 times 38?"
  - "Tell me a joke"
  - "What time is it?"
  - "Remember that I need to buy groceries"
  - "What are my notes?"
"""

import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, AgentServer, RunContext, function_tool
from livekit.plugins import openai, silero

load_dotenv(".env.local")

saved_notes = []


class PersonalAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Jarvis, a smart and friendly personal voice assistant.

Your abilities:
- Tell the current time and date
- Check weather for any city
- Remember notes for the user
- Do math calculations
- Search Wikipedia for information about anything
- Tell jokes

Rules:
- Keep responses SHORT since this is voice, around 1 to 3 sentences
- Do not use formatting, emojis, or special characters
- Be conversational and natural
- When the user asks about a topic you do not know, use the search_wikipedia tool
- When the user asks to calculate something, use the calculate tool
- When the user wants a joke, use the tell_joke tool
- When the user asks about time or date, use the get_current_time tool
- When the user asks about weather, use the get_weather tool""",
        )

    # --- Time ---
    @function_tool()
    async def get_current_time(self, context: RunContext):
        """Get the current date and time. Use when the user asks what time or date it is."""
        now = datetime.now()
        return f"Current date: {now.strftime('%A, %B %d, %Y')}. Current time: {now.strftime('%I:%M %p')}"

    # --- Weather ---
    @function_tool()
    async def get_weather(self, context: RunContext, city: str):
        """Get the current weather for a given city.

        Args:
            city: The name of the city to get weather for.
        """
        demo_weather = {
            "london": "Cloudy, 14 degrees, light rain expected",
            "new york": "Sunny, 22 degrees, clear skies",
            "tokyo": "Partly cloudy, 18 degrees, humid",
            "mumbai": "Hot, 33 degrees, chance of rain",
            "chennai": "Warm, 31 degrees, partly cloudy",
            "paris": "Clear, 16 degrees, pleasant breeze",
            "dubai": "Hot, 38 degrees, sunny",
            "bangalore": "Pleasant, 26 degrees, partly cloudy",
            "delhi": "Warm, 30 degrees, hazy",
            "hyderabad": "Warm, 29 degrees, clear skies",
        }

        city_lower = city.lower()
        for key, weather in demo_weather.items():
            if key in city_lower:
                return f"Weather in {city}: {weather}"

        return f"Weather in {city}: Around 20 degrees, mostly clear. This is demo data."

    # --- Notes ---
    @function_tool()
    async def remember_note(self, context: RunContext, note: str):
        """Save a note that the user wants to remember.

        Args:
            note: The note or information to save.
        """
        saved_notes.append({
            "note": note,
            "time": datetime.now().strftime("%I:%M %p")
        })
        return f"Saved your note: {note}"

    @function_tool()
    async def recall_notes(self, context: RunContext):
        """Recall all saved notes. Use when the user asks what they asked you to remember."""
        if not saved_notes:
            return "No saved notes yet."

        notes_text = ""
        for i, item in enumerate(saved_notes, 1):
            notes_text += f"Note {i}: {item['note']}, saved at {item['time']}. "
        return notes_text

    # --- Calculator ---
    @function_tool()
    async def calculate(self, context: RunContext, expression: str):
        """Calculate a math expression. Use when the user asks to do any math.

        Args:
            expression: The math expression to evaluate, like 245 times 38 or 100 divided by 7.
        """
        try:
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "I can only do basic math with numbers and plus, minus, multiply, divide."

            result = eval(expression)
            return f"The answer is: {result}"
        except Exception:
            return "Sorry, I could not calculate that. Please try a simpler expression."

    # --- Wikipedia ---
    @function_tool()
    async def search_wikipedia(self, context: RunContext, topic: str):
        """Search Wikipedia for information about a topic. Use when the user asks about a person, place, thing, or concept.

        Args:
            topic: The topic to search for on Wikipedia.
        """
        try:
            import urllib.request
            import urllib.parse

            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
            req = urllib.request.Request(url, headers={"User-Agent": "VoiceAgent/1.0"})

            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                extract = data.get("extract", "")

                if extract:
                    short = extract[:500]
                    if len(extract) > 500:
                        short += "..."
                    return f"About {topic}: {short}"
                else:
                    return f"I could not find information about {topic} on Wikipedia."

        except Exception as e:
            return f"Sorry, I could not search for that right now."

    # --- Jokes ---
    @function_tool()
    async def tell_joke(self, context: RunContext):
        """Tell a random joke. Use when the user asks for a joke or wants to laugh."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What did the ocean say to the beach? Nothing, it just waved.",
            "Why did the bicycle fall over? Because it was two tired!",
            "What do you call a sleeping dinosaur? A dino snore!",
            "What do you call a dog that does magic tricks? A Labracadabrador!",
            "Why could not the bicycle stand up by itself? It was two tired!",
        ]
        return random.choice(jokes)


# Server setup
server = AgentServer()


@server.rtc_session(agent_name="personal-assistant-v2")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(
        stt=openai.STT(model="gpt-4o-transcribe", language="en"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(
            model="gpt-4o-mini-tts",
            voice="ash",
            instructions="Speak in a friendly, enthusiastic, and conversational tone.",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=PersonalAssistant(),
    )

    await session.generate_reply(
        instructions="Greet the user by saying: Hey there! I am Jarvis, your personal assistant. I can check the weather, do math, look things up on Wikipedia, remember things for you, and even tell jokes. What would you like to do?"
    )


if __name__ == "__main__":
    agents.cli.run_app(server)