import discord
import asyncio
import os
from mcstatus import JavaServer

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1488527125798588610
SERVER_IP = "n5dupe.minefort.com"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_to_edit = None


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

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Channel not found")
        return

    # Send first message
    online, max_players = await get_player_count()
    if online is None:
        message_to_edit = await channel.send("❌ Server offline or unreachable")
    else:
        message_to_edit = await channel.send(
            f"🟢 Server Online: {online}/{max_players} players"
        )

    # Loop every 10 seconds
    while not client.is_closed():
        await asyncio.sleep(10)

        online, max_players = await get_player_count()

        try:
            if online is None:
                await message_to_edit.edit(
                    content="❌ Server offline or unreachable"
                )
            else:
                await message_to_edit.edit(
                    content=f"🟢 Server Online: {online}/{max_players} players"
                )
        except Exception as e:
            print(f"Error editing message: {e}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(update_loop())


client.run(TOKEN)
