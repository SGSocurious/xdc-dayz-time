import discord
from discord.ext import commands, tasks
import a2s
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TOKEN = os.getenv("TOKEN")

SERVER_IP = ("193.25.252.52", 27016)

RESTART_HOURS = [1, 5, 9, 13, 17, 21]

AMSTERDAM = ZoneInfo("Europe/Amsterdam")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def in_restart_window():

    now = datetime.now(AMSTERDAM)

    restart_times = []

    for hour in RESTART_HOURS:
        today_restart = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        restart_times.append(today_restart)
        restart_times.append(today_restart + timedelta(days=1))

    next_restart = min(rt for rt in restart_times if rt > now)
    last_restart = max(rt for rt in restart_times if rt <= now)

    window_start = last_restart - timedelta(minutes=2)
    window_end = last_restart + timedelta(minutes=2)

    return window_start <= now <= window_end


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

    if in_restart_window():
        print("[RESTART] Skipping update during restart window")
        return

    try:

        print("[QUERY] Checking server time...")

        info = a2s.info(SERVER_IP, timeout=5)

        server_time = get_server_time(info.keywords)

        if server_time is None:
            status_text = "Server time unknown"
            bot_status = discord.Status.idle

        else:

            hour = int(server_time.split(":")[0])

            if 6 <= hour < 15:
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
