import discord
from discord.ext import commands
from config import TOKEN
import asyncio

intents = discord.Intents.all()
bot = commands.Bot("!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

async def load_cogs():
    await bot.load_extension("cogs.comandos_gerais")
    await bot.load_extension("cogs.eventos")
    await bot.load_extension("cogs.formulario")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
