"""
Personal Voice Assistant — Level 1 (Real Weather!)
=====================================================
Now with REAL weather data using Open-Meteo API (free, no API key needed!)

Try saying:
  - "What time is it?"
  - "What's the weather in Chennai?"
  - "What's the weather in London?"
  - "Remember that my meeting is at 3 PM"
  - "What did I ask you to remember?"
"""

import os
import json
import urllib.request
import urllib.parse
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
            instructions="""You are a helpful personal voice assistant named Jarvis.
You are friendly, smart, and always ready to help.
You can tell the time, check REAL weather, and remember things for the user.
Keep your responses short and conversational since this is a voice interaction.
Do not use complex formatting, emojis, or special characters.
When the user asks you to remember something, use the remember_note tool.
When the user asks what you remember, use the recall_notes tool.
When the user asks about the time or date, use the get_current_time tool.
When the user asks about weather, use the get_weather tool.
When reporting weather, always say the temperature in both Celsius and Fahrenheit.""",
        )

    @function_tool()
    async def get_current_time(self, context: RunContext):
        """Get the current date and time. Use this when the user asks what time or date it is."""
        now = datetime.now()
        return f"Current date: {now.strftime('%A, %B %d, %Y')}. Current time: {now.strftime('%I:%M %p')}"

    @function_tool()
    async def get_weather(self, context: RunContext, city: str):
        """Get the REAL current weather for any city in the world.

        Args:
            city: The name of the city to get weather for.
        """
        try:
            # Step 1: Convert city name to coordinates using Open-Meteo Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1&language=en"
            geo_req = urllib.request.Request(geo_url, headers={"User-Agent": "VoiceAgent/1.0"})

            with urllib.request.urlopen(geo_req, timeout=5) as response:
                geo_data = json.loads(response.read().decode())

            if "results" not in geo_data or len(geo_data["results"]) == 0:
                return f"Sorry, I could not find a city called {city}."

            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = location["name"]
            country = location.get("country", "")

            # Step 2: Get actual weather from Open-Meteo Weather API
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
                f"weather_code,wind_speed_10m"
                f"&temperature_unit=celsius"
            )
            weather_req = urllib.request.Request(weather_url, headers={"User-Agent": "VoiceAgent/1.0"})

            with urllib.request.urlopen(weather_req, timeout=5) as response:
                weather_data = json.loads(response.read().decode())

            current = weather_data["current"]
            temp_c = current["temperature_2m"]
            temp_f = round(temp_c * 9 / 5 + 32, 1)
            feels_like_c = current["apparent_temperature"]
            feels_like_f = round(feels_like_c * 9 / 5 + 32, 1)
            humidity = current["relative_humidity_2m"]
            wind_speed = current["wind_speed_10m"]
            weather_code = current["weather_code"]

            # Convert weather code to description
            weather_descriptions = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Foggy",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snowfall",
                73: "Moderate snowfall",
                75: "Heavy snowfall",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail",
            }
            condition = weather_descriptions.get(weather_code, "Unknown conditions")

            return (
                f"Current weather in {city_name}, {country}: "
                f"{condition}. "
                f"Temperature: {temp_c} degrees Celsius ({temp_f} degrees Fahrenheit). "
                f"Feels like: {feels_like_c} degrees Celsius ({feels_like_f} degrees Fahrenheit). "
                f"Humidity: {humidity} percent. "
                f"Wind speed: {wind_speed} kilometers per hour."
            )

        except Exception as e:
            return f"Sorry, I could not get weather data right now. Error: {str(e)}"

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
        return f"Got it! I have saved your note: {note}"

    @function_tool()
    async def recall_notes(self, context: RunContext):
        """Recall all saved notes. Use when the user asks what they asked you to remember."""
        if not saved_notes:
            return "You have not asked me to remember anything yet."

        notes_text = ""
        for i, item in enumerate(saved_notes, 1):
            notes_text += f"Note {i}: {item['note']}, saved at {item['time']}. "

        return f"Here are your saved notes: {notes_text}"


# Server setup
server = AgentServer()


@server.rtc_session(agent_name="personal-assistant")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(
        stt=openai.STT(
            model="gpt-4o-transcribe",
            language="en",
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
        ),
        tts=openai.TTS(
            model="gpt-4o-mini-tts",
            voice="ash",
            instructions="Speak in a friendly and conversational tone, like a helpful assistant.",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=PersonalAssistant(),
    )

    await session.generate_reply(
        instructions="Greet the user by saying: Hi! I am Jarvis, your personal assistant. I can tell you the time, check real weather for any city in the world, and remember things for you. How can I help?"
    )


if __name__ == "__main__":
    agents.cli.run_app(server)