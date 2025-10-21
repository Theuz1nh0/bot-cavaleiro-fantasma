import discord
from discord.ext import commands, tasks
import json
import os
import random
from datetime import datetime
from utils.checks import canal_permitido

DATA_PATH = "data/levels.json"
CANAL_COMANDOS = 1428430208121442367

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self.load_data()
        self.voice_times = {}
        self.save_loop.start()

    # -------------------------------
    # MANIPULAÇÃO DE ARQUIVO
    # -------------------------------
    def load_data(self):
        if not os.path.exists(DATA_PATH):
            with open(DATA_PATH, "w") as f:
                json.dump({}, f)
        with open(DATA_PATH, "r") as f:
            return json.load(f)
        
    def save_data(self):
        with open(DATA_PATH, "w") as f:
            json.dump(self.data, f, indent=4)

    
    @tasks.loop(minutes=5)
    async def save_loop(self):
        self.save_data()

    # -------------------------------
    # SISTEMA DE XP
    # -------------------------------
    def add_xp(self, user_id, xp_amount):
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {"xp": 0, "level": 1, "voice_total": 0}

        self.data[uid]["xp"] += xp_amount
        current_xp = self.data[uid]["xp"]
        current_level = self.data[uid]["level"]

        next_level_xp = current_level * 100

        if current_xp >= next_level_xp:
            self.data[uid]["level"] += 1
            self.data[uid]["xp"] = 0
            return True
        return False
    
    # -------------------------------
    # XP POR MENSAGEM
    # -------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        print(message)
        print(message.channel.name)
        
        xp_ganho = random.randint(5, 15)
        subiu = self.add_xp(message.author.id, xp_ganho)
        self.save_data()

        if subiu:
            await message.channel.send(
                f"🎉 {message.author.mention} subiu para o **nível {self.data[str(message.author.id)]['level']}!**"
            )

    # -------------------------------
    # XP POR TEMPO EM CALL
    # -------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        uid = str(member.id)

        # Entrou em call
        if before.channel is None and after.channel is not None:
            self.voice_times[uid] = datetime.now()
            print("comecou a contar")

        # Saiu da call
        elif before.channel is not None and after.channel is None:
            print("terminou de contar")

            if uid in self.voice_times:
                joined_at = self.voice_times.pop(uid)
                duration = (datetime.now() - joined_at).total_seconds()
                minutes = int(duration // 60)

                print(minutes)
                if minutes > 0:
                    #soma tempo total em call
                    if uid not in self.data:
                        self.data[uid] = {"xp": 0, "nivel": 1, "voice_total": 0}

                    self.data[uid]["voice_total"] += minutes

                    xp_ganho = minutes * 2 # 2 XP por minuto em call
                    subiu  = self.add_xp(member.id, xp_ganho)
                    self.save_data()

                    if subiu:
                        await after.channel.send(
                            f"🎙️ {member.mention} subiu para o nível "
                            f"{self.data[uid]['level']} após passar {minutes} minutos em call!"
                        )

    # -------------------------------
    # COMANDO RANK
    # -------------------------------
    @canal_permitido([CANAL_COMANDOS])
    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        uid = str(member.id)
        user_data = self.data.get(uid, {"xp": 0, "level": 1, "voice_total": 0})

        embed = discord.Embed(
            title=f"📊 Nível de {member.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="🧩 Nível", value=user_data["level"])
        embed.add_field(name="✨ XP", value=user_data["xp"])
        embed.add_field(name="🎧 Tempo total em call", value=f"{user_data['voice_total']} min")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))