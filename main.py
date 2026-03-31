import discord
import asyncio
import os
from mcstatus import JavaServer
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1488527125798588610
SERVER_IP = "n5dupe.minefort.com"

if not TOKEN:
    raise ValueError("TOKEN is missing!")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_to_edit = None


# ✅ KEEP RAILWAY ALIVE
def run_web():
    server = HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web).start()


async def get_player_count():
    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        return status.players.online, status.players.max
    except Exception as e:
        print(f"Error fetching server status: {e}")
        return None, None


async def update_loop():
    global message_to_edit
    await client.wait_until_ready()

    print("Bot ready, starting loop...")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Channel not found")
        return

    online, max_players = await get_player_count()

    if online is None:
        message_to_edit = await channel.send("❌ Server offline")
    else:
        message_to_edit = await channel.send(
            f"🟢 {online}/{max_players} players online"
        )

    while True:
        await asyncio.sleep(10)

        online, max_players = await get_player_count()

        try:
            if online is None:
                await message_to_edit.edit(content="❌ Server offline")
            else:
                await message_to_edit.edit(
                    content=f"🟢 {online}/{max_players} players online"
                )
        except Exception as e:
            print(f"Edit error: {e}")


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    asyncio.create_task(update_loop())


client.run(TOKEN)
