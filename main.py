import discord
from discord.ext import commands, tasks
import a2s
import os

TOKEN = os.getenv("TOKEN")

SERVER_IP = ("193.25.252.52", 27016)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def get_server_time(keywords):

    tags = keywords.split(",")

    for tag in tags:
        if ":" in tag:
            return tag

    return None


@bot.event
async def on_ready():
    print(f"[BOT] Online als {bot.user}")

    if not update_status.is_running():
        update_status.start()


@tasks.loop(seconds=30)
async def update_status():

    try:

        print("[QUERY] Checking server time...")

        info = a2s.info(SERVER_IP, timeout=5)

        server_time = get_server_time(info.keywords)

        if server_time is None:
            status_text = "Server time unknown"
            bot_status = discord.Status.idle

        else:

            hour = int(server_time.split(":")[0])

            # dag / nacht check
            if 6 <= hour < 20:
                bot_status = discord.Status.online
            else:
                bot_status = discord.Status.idle

            status_text = f"Server time {server_time}"

        print(f"[TIME] {status_text}")

        await bot.change_presence(
            status=bot_status,
            activity=discord.Game(name=status_text)
        )

    except Exception as e:

        print("[SERVER] Query failed:", e)

        await bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(name="Server offline")
        )


bot.run(TOKEN)
