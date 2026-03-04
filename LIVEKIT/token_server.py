"""
Token Server — Generates tokens AND dispatches the agent automatically
=======================================================================
No more manual dispatch needed! When a user connects, this server:
  1. Creates the room token
  2. Dispatches the agent into the room via API

Usage: python token_server.py
Then open: http://localhost:8080
"""

import os
import json
import asyncio
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from livekit import api
from livekit.protocol.agent_dispatch import CreateAgentDispatchRequest
from dotenv import load_dotenv

load_dotenv(".env.local")

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_HTTP_URL = LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://")

ROOM_NAME = "my-room"
AGENT_NAME = "personal-assistant"


def dispatch_agent():
    """Dispatch the agent into the room via LiveKit API"""
    async def _dispatch():
        try:
            lk = api.LiveKitAPI(
                LIVEKIT_HTTP_URL,
                api_key=LIVEKIT_API_KEY,
                api_secret=LIVEKIT_API_SECRET,
            )
            result = await lk.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(
                    room=ROOM_NAME,
                    agent_name=AGENT_NAME,
                )
            )
            await lk.aclose()
            print(f"Agent dispatched to room '{ROOM_NAME}'!")
            return result
        except Exception as e:
            print(f"Agent dispatch error: {e}")
            return None

    # Run async dispatch in a new event loop (since we're in a sync HTTP handler)
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_dispatch())
    finally:
        loop.close()


class TokenHandler(SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/token":
            self.generate_token()
        elif self.path == "/":
            self.serve_frontend()
        else:
            super().do_GET()

    def generate_token(self):
        """Generate a token AND dispatch the agent"""
        try:
            # 1. Create the token
            token = (
                api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
                .with_identity("web-user")
                .with_name("Web User")
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=ROOM_NAME,
                    )
                )
                .to_jwt()
            )

            # 2. Dispatch the agent into the room
            dispatch_agent()

            # 3. Send token to browser
            response = json.dumps({
                "token": token,
                "url": LIVEKIT_URL,
            })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
            print(f"Token generated + agent dispatched!")

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            print(f"Error: {e}")

    def serve_frontend(self):
        try:
            with open("chat.html", "r") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"chat.html not found!")


if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("0.0.0.0", port), TokenHandler)
    print(f"")
    print(f"  ===================================")
    print(f"  Token Server running!")
    print(f"  Open: http://localhost:{port}")
    print(f"  ===================================")
    print(f"")
    print(f"  LiveKit URL: {LIVEKIT_URL}")
    print(f"  Room: {ROOM_NAME}")
    print(f"  Agent: {AGENT_NAME}")
    print(f"  Auto-dispatch: ON")
    print(f"")
    server.serve_forever()
