import discord
from discord.ext import commands, tasks
import json
import os
import asyncio
from datetime import datetime
from utils.checks import canal_permitido

DATA_PATH = "data/levels.json"
CANAL_COMANDOS = 1428430208121442367

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self.load_data()
        self.config = self.load_config()
        self.active_users = {}

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

    def load_config(self):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    # -------------------------------
    # SISTEMA DE XP
    # -------------------------------
    def add_xp(self, member, xp_amount):
        uid = str(member)
        if uid not in self.data:
            self.data[uid] = {"xp": 0, "level": 1, "voice_total": 0}

        self.data[uid]["xp"] += xp_amount
        current_xp = self.data[uid]["xp"]
        current_level = self.data[uid]["level"]
        XP1 = 100
        r = 1.0625

        next_level_xp = XP1 * (r ** (current_level - 1))

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
        
        # print(message)
        # print(message.channel.name)
        
        xp_ganho = 2
        subiu = self.add_xp(message.author.id, xp_ganho)
        self.save_data()
        user_id = str(message.author.id)

        if subiu:
            await message.channel.send(
                f"🎉 {message.author.mention} subiu para o **nível {self.data[user_id]['level']}!**"
            )

            # Tenta aplicar cargo se houver
            await self.give_role_based_on_level(message.author, self.data[user_id]["level"])

    # -------------------------------
    # XP POR TEMPO EM CALL
    # -------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        # Entrou em call
        if after.channel and not before.channel:
            if member.id not in self.active_users:
                task = asyncio.create_task(self.track_voice_xp(member))
                self.active_users[member.id] = task
                print(f"[LEVELS] Loop iniciado para {member.display_name}")

        # Saiu da call
        elif before.channel and not after.channel:
            if member.id in self.active_users:
                self.active_users[member.id].cancel()
                del self.active_users[member.id]
                print(f"[LEVELS] {member.display_name} saiu da call (loop cancelado)")
    
    async def track_voice_xp(self, member: discord.Member):
        uid = str(member.id)

        if uid not in self.data:
            self.data[uid] = {"xp": 0, "level": 1, "voice_total": 0}

        try:
            while True:
                await asyncio.sleep(60)

                if not member.voice or not member.voice.channel:
                    print(f"[LEVELS] {member.display_name} saiu da call (detectado pelo loop)")
                    break

                subiu = self.add_xp(member.id, 2)
                self.data[uid]["voice_total"] += 1

                print(subiu)

                if subiu:
                    try:
                        await member.voice.channel.send(f"🎉 {member.mention} subiu para o **nível {self.data[uid]['level']}!**")
                        await self.give_role_based_on_level(member, self.data[uid]["level"])
                    except discord.Forbidden:
                        print(f"[LEVELS] Não consegui enviar a mensagem")

                self.save_data()
        except asyncio.CancelledError:
            pass


    # -------------------------------
    # COMANDO RANK
    # -------------------------------
    @canal_permitido([CANAL_COMANDOS])
    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        uid = str(member.id)
        user_data = self.data.get(uid, {"xp": 0, "level": 1, "voice_total": 0})
        user_xp = user_data["xp"]
        xp_needed = 100 * (1.0625 ** (user_data["level"] - 1))
        voice_total = user_data["voice_total"]
        voice_horas = None
        voice_minutes = None

        if voice_total >= 60:
            voice_horas = voice_total // 60
            if voice_total % 60 > 0:
                voice_minutes = voice_total - (voice_horas * 60)

        tempo_call = f"{voice_total}min"

        if voice_horas:
            tempo_call = f"{voice_horas}h"
            if voice_minutes:
                tempo_call = f"{voice_horas}h {voice_minutes}min"

        # Calcula a porcentagem de XP
        percent = user_xp / xp_needed
        bar_length = 10  # número de blocos da barra
        filled_length = int(bar_length * percent)
        empty_length = bar_length - filled_length

        progress_bar = "▬" * filled_length + "──" * empty_length
        progress_display = f"[{progress_bar}] {int(percent * 100)}%"

        embed = discord.Embed(
            title=f"📊 Nível de {member.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="🧩 Nível", value=user_data["level"])
        embed.add_field(name="✨ XP", value=user_xp)
        embed.add_field(name="🎧 Tempo total em call", value=f"{tempo_call}")
        embed.add_field(name="Progresso", value=progress_display, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")

        await ctx.send(embed=embed)

    async def give_role_based_on_level(self, member: discord.Member, level: int):
        """
        Dá o cargo apropriado ao membro baseado no nível e remove cargos
        de níveis anteriores (os definidos em config.json).
        """
        guild = member.guild
        roles_map = self.config.get("level_roles", {})

        if not roles_map:
            return

        # Converte e ordena os níveis (do maior para o menor)
        level_items = sorted(
            ((int(k), int(v)) for k, v in roles_map.items()),
            key=lambda x: x[0],
            reverse=True
        )

        # Acha o cargo alvo (o maior nível que o usuário já atingiu)
        target_role = None
        target_level = None
        for lvl, role_id in level_items:
            if level >= lvl:
                target_role = guild.get_role(role_id)
                target_level = lvl
                break

        # Se não existe cargo correspondente, apenas remova cargos antigos (se quiser)
        role_ids_config = {int(rid) for _, rid in level_items}

        # Lista de cargos do membro que fazem parte do sistema de level roles
        member_level_roles = [r for r in member.roles if r.id in role_ids_config]

        # Se o target_role for None, apenas remova qualquer cargo de level (opcional)
        # Caso queira não remover se não houver target, comente a remoção.
        try:
            # Primeiro: remover cargos de nível que não são o target
            for r in member_level_roles:
                if target_role and r.id == target_role.id:
                    continue  # preserva o target
                # tenta remover
                try:
                    await member.remove_roles(r, reason="Atualização de cargos por level")
                except discord.Forbidden:
                    # bot não tem permissão para remover este cargo (role hierarchy)
                    print(f"[WARN] Não foi possível remover role {r.id} ({r.name}) do membro {member.id} — permissões.")
                except Exception as e:
                    print(f"[ERROR] Erro ao remover role {r.id} do membro {member.id}: {e}")

            # Depois: adiciona o cargo alvo (se existir e o membro não tiver)
            if target_role:
                if target_role not in member.roles:
                    try:
                        await member.add_roles(target_role, reason=f"Alcançou o nível {target_level}")
                        # opcional: enviar DM
                        try:
                            await member.send(f"🏅 Você alcançou o nível {level} no discord de {guild} e recebeu o cargo de **{target_role.name}**!")
                        except Exception:
                            pass  # ignora falha em DM
                    except discord.Forbidden:
                        print(f"[WARN] Não foi possível adicionar role {target_role.id} ({target_role.name}) ao membro {member.id} — permissões.")
                    except Exception as e:
                        print(f"[ERROR] Erro ao adicionar role {target_role.id} ao membro {member.id}: {e}")
        except Exception as e:
            print(f"[ERROR] give_role_based_on_level geral: {e}")


async def setup(bot):
    await bot.add_cog(LevelSystem(bot))