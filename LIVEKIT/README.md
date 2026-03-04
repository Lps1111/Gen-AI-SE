# Jarvis — AI Voice Assistant

A real-time AI voice assistant built with **LiveKit Agents Framework**, powered by **OpenAI** for speech-to-text, language understanding, and text-to-speech. Talk to Jarvis through your browser or terminal — it can check live weather, do math, search Wikipedia, tell jokes, and remember things for you.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![LiveKit](https://img.shields.io/badge/LiveKit-Agents_1.4-purple)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

## How It Works

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Browser    │────▶│  LiveKit Server  │◀────│  Agent (AI)  │
│  (Your Mic)  │◀────│   (WebRTC Hub)   │────▶│  (Python)    │
└─────────────┘     └─────────────────┘     └──────┬───────┘
                                                    │
                                         ┌──────────┴──────────┐
                                         │     OpenAI API       │
                                         │  STT → LLM → TTS    │
                                         └─────────────────────┘
```

1. **You speak** → Browser captures audio via WebRTC
2. **STT** → OpenAI `gpt-4o-transcribe` converts speech to text
3. **LLM** → OpenAI `gpt-4o-mini` processes your request (with function tools)
4. **TTS** → OpenAI `gpt-4o-mini-tts` converts response to speech
5. **You hear** → Audio streamed back through WebRTC

## Features

**Level 1 — Core Assistant** (`agent_level1.py`)
- Real-time weather for any city worldwide (Open-Meteo API, no key needed)
- Current date and time
- Save and recall notes/reminders
- Temperature reported in both Celsius and Fahrenheit

**Level 2 — Enhanced Assistant** (`agent_level2.py`)
- Everything in Level 1, plus:
- Wikipedia search for any topic
- Math calculator (complex expressions supported)
- Random jokes

**Two Ways to Interact**
- **Browser UI** — Beautiful web interface with animated orb, live transcriptions
- **Console Mode** — Talk directly through your terminal mic/speakers

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | LiveKit Agents 1.4 (Python) |
| LiveKit Server | Self-hosted via Docker |
| Speech-to-Text | OpenAI `gpt-4o-transcribe` |
| LLM | OpenAI `gpt-4o-mini` |
| Text-to-Speech | OpenAI `gpt-4o-mini-tts` (voice: ash) |
| Voice Activity Detection | Silero VAD |
| Weather API | Open-Meteo (free, no API key) |
| Knowledge Search | Wikipedia REST API |
| Frontend | Vanilla HTML/JS + LiveKit Client SDK |
| Token Server | Python HTTP server with LiveKit API |

## Project Structure

```
├── agent_level1.py       # Voice agent with weather, time, notes
├── agent_level2.py       # Enhanced agent + Wikipedia, calculator, jokes
├── token_server.py       # Token generation + auto agent dispatch
├── chat.html             # Browser UI with animated orb
├── .env.local            # Environment variables (API keys)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container setup for the agent
├── docker-compose.yml    # Run LiveKit server + agent together
└── README.md
```

## Prerequisites

- **Python 3.11+**
- **Docker Desktop** (for LiveKit server)
- **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))
- **Microphone** (for voice interaction)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/jarvis-voice-assistant.git
cd jarvis-voice-assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env.local` file:

```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Replace `sk-your-openai-api-key-here` with your actual OpenAI API key.

### 5. Start LiveKit Server (Docker)

```bash
docker run -d \
  --name livekit-server \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 50000-50060:50000-50060/udp \
  livekit/livekit-server \
  --dev --bind 0.0.0.0 --node-ip 127.0.0.1
```

> **Windows CMD** — replace `\` with `^` or put everything on one line.

Verify it's running: open http://localhost:7880 — it should show "ok".

### 6. Run the Agent

**Option A: Console Mode** (quickest, talk via terminal)

```bash
python agent_level1.py console
```

Speak into your mic and Jarvis responds through your speakers. No browser needed.

**Option B: Browser Mode** (full UI experience)

You need **two terminals** running simultaneously:

**Terminal 1 — Agent:**
```bash
python agent_level1.py start
```

**Terminal 2 — Token Server:**
```bash
python token_server.py
```

Then open http://localhost:8080 in your browser, click **Connect**, and start talking!

## Usage Examples

Once connected, try saying:

| Say This | What Happens |
|----------|-------------|
| "What time is it?" | Returns current date and time |
| "What's the weather in Tokyo?" | Fetches live weather from Open-Meteo |
| "Remember that my flight is at 6 PM" | Saves a note |
| "What did I ask you to remember?" | Recalls all saved notes |
| "What is 847 divided by 23?" | Calculates the answer (Level 2) |
| "Tell me about black holes" | Searches Wikipedia (Level 2) |
| "Tell me a joke" | Tells a random joke (Level 2) |

## Browser UI

The web interface features:

- **Animated orb** that changes color based on state:
  - 🔵 Blue = Connected, ready
  - 🟢 Green = Listening to you
  - 🟣 Purple = Jarvis is speaking
- **Live transcription** of both your speech and Jarvis's responses
- **Connect/Disconnect** button for easy session management

## Architecture Deep Dive

### LiveKit Agents Framework

The agent runs as a **LiveKit participant** — just like a human user in a video call, but powered by AI. The framework handles:

- **Voice Activity Detection (VAD):** Silero model detects when you start/stop speaking
- **Turn-taking:** Knows when to listen vs. respond, handles interruptions
- **Streaming pipeline:** Audio flows through STT → LLM → TTS in real-time
- **Function tools:** LLM can call Python functions (weather, calculator, etc.)

### Self-Hosted Setup

This project uses a **self-hosted LiveKit server** running in Docker, which means:

- No LiveKit Cloud account needed
- Everything runs on your machine
- Free for development and testing
- Agent dispatch is handled via API (not token-based dispatch)

### Token Server

The `token_server.py` serves two purposes:

1. **Generates JWT tokens** for the browser to authenticate with LiveKit
2. **Auto-dispatches the agent** into the room via LiveKit's Agent Dispatch API

This is necessary because self-hosted LiveKit dev servers don't support token-based agent dispatch (a feature available in LiveKit Cloud).

## Configuration

### Change the Voice

In the agent file, modify the `voice` parameter in the TTS config:

```python
tts=openai.TTS(
    model="gpt-4o-mini-tts",
    voice="ash",  # Change this
)
```

Available voices: `alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`, `verse`

### Change the LLM

```python
llm=openai.LLM(
    model="gpt-4o-mini",  # or "gpt-4o" for more capable (but costs more)
)
```

### Customize Personality

Edit the `instructions` string in the `PersonalAssistant` class to change how Jarvis behaves.

### Add Custom Tools

Add new capabilities by defining methods inside the `PersonalAssistant` class:

```python
@function_tool()
async def my_new_tool(self, context: RunContext, param: str):
    """Description of what this tool does — the LLM reads this to decide when to call it.

    Args:
        param: Description of the parameter.
    """
    # Your logic here
    return "Result as a string"
```

## Adding New Tools

Tools must follow these rules (LiveKit Agents 1.4+):

1. Must be **methods inside the Agent class** (not standalone functions)
2. Must include `self` and `context: RunContext` parameters
3. Must have a **clear docstring** — the LLM uses it to decide when to call the tool
4. Return value is automatically converted to a string

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ServerDisconnectedError` | Restart LiveKit with `--bind 0.0.0.0` |
| `could not establish pc connection` | Add `--node-ip 127.0.0.1` to Docker command |
| Agent not joining room | Use `token_server.py` (auto-dispatches agent) |
| `ImportError: RoomAgentDispatch` | Run `pip install livekit-api` |
| Browser shows "waiting for agent" | Restart agent with `python agent_level1.py start` |
| Weather not working | Open-Meteo API is free, no key needed — check internet connection |
| No audio in browser | Allow microphone permission when prompted |
| `InsecureKeyLengthWarning` | Harmless warning from dev keys, safe to ignore |

## Ports Reference

| Port | Service | Protocol |
|------|---------|----------|
| 7880 | LiveKit Server (HTTP/WebSocket) | TCP |
| 7881 | LiveKit Server (WebRTC TCP) | TCP |
| 50000-50060 | LiveKit Server (WebRTC media) | UDP |
| 8080 | Token Server + Web UI | TCP |

## Roadmap

- [ ] Neo4j knowledge graph integration (RAG)
- [ ] Telephony support (phone calls)
- [ ] Multi-language support
- [ ] Persistent memory (database-backed notes)
- [ ] Custom wake word detection
- [ ] Mobile app frontend
- [ ] Production deployment guide

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [LiveKit](https://livekit.io/) — Open-source real-time communication platform
- [OpenAI](https://openai.com/) — STT, LLM, and TTS models
- [Open-Meteo](https://open-meteo.com/) — Free weather API
- [Silero](https://github.com/snakers4/silero-vad) — Voice Activity Detection
