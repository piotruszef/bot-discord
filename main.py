import logging
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True  # Wymagane do odczytywania treści wiadomości

bot = commands.Bot(command_prefix='!', intents=intents)

# Token twojego bota
TOKEN = 'YOUR_TOKEN_BOT'
CHANNEL_ID = 1178827936237883521  # ID kanału, w którym chcesz tworzyć wątki

scheduler = AsyncIOScheduler()

@bot.event
async def on_ready():
    logging.info(f'Bot {bot.user} jest gotowy.')

    # Uruchomienie create_thread natychmiast po starcie bota
    await create_thread()

    # Ustaw harmonogram na poniedziałek o 10:00
    scheduler.add_job(create_thread, CronTrigger(day_of_week='mon', hour=10, minute=0))
    scheduler.start()

async def create_thread():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        thread_name = f'Tygodniowy Wątek - {datetime.datetime.now().strftime("%Y-%m-%d")}'
        thread = await channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
        await thread.send('To jest początkowa wiadomość w nowym wątku.')
        logging.info(f'Utworzono wątek: {thread_name}')
    else:
        logging.error(f'Nie mogę znaleźć kanału o ID {CHANNEL_ID}')

@bot.event
async def on_error(event, *args, **kwargs):
    logging.exception(f'Wystąpił błąd w wydarzeniu: {event}')

bot.run(TOKEN)
