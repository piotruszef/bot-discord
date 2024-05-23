import logging
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import sqlite3
import datetime

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True  # Wymagane do odczytywania treści wiadomości

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = 'token_bota'
CHANNEL_ID = 1178827936237883521  # ID kanału, w którym chcesz tworzyć wątki

# Połączenie z bazą danych SQLite
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Stworzenie tabeli w bazie danych, jeśli nie istnieje
cursor.execute('''CREATE TABLE IF NOT EXISTS schedule
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, hour INTEGER, minute INTEGER)''')
conn.commit()

scheduler = AsyncIOScheduler()

@bot.event
async def on_ready():
    logging.info(f'Bot {bot.user} jest gotowy.')
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

@bot.command(name='data', description='Ustaw dzień tygodnia i godzinę utworzenia wątku. Format: !data poniedziałek 10:43')
async def data(ctx, day: str, time: str):
    """Ustaw dzień tygodnia i godzinę utworzenia wątku. Format: !data poniedziałek 10:43"""
    try:
        # Mapa dni tygodnia na ich numeryczne reprezentacje w CronTrigger
        days_of_week = {
            'pon': 'mon',
            'wt': 'tue',
            'śr': 'wed',
            'czw': 'thu',
            'pt': 'fri',
            'sob': 'sat',
            'nd': 'sun'
        }

        day_of_week = days_of_week.get(day.lower())
        if day_of_week is None:
            await ctx.send('Błędny dzień tygodnia. Użyj jednego z: poniedziałek, wtorek, środa, czwartek, piątek, sobota, niedziela.')
            return

        hour, minute = map(int, time.split(':'))

        # Dodanie zadania do harmonogramu
        scheduler.add_job(create_thread, CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute))

        # Zapisanie harmonogramu do bazy danych
        cursor.execute('INSERT INTO schedule (day, hour, minute) VALUES (?, ?, ?)', (day_of_week, hour, minute))
        conn.commit()

        await ctx.send(f'Ustawiono harmonogram na {day} o {time}. Wątek będzie tworzony co tydzień.')
        logging.info(f'Ustawiono harmonogram na {day} o {time}. Wątek będzie tworzony co tydzień.')
    except ValueError as e:
        await ctx.send('Błędny format czasu. Użyj formatu: HH:MM')
        logging.error(f'Błędny format czasu: {e}')

@bot.event
async def on_error(event, *args, **kwargs):
    logging.exception(f'Wystąpił błąd w wydarzeniu: {event}')

bot.run(TOKEN)
