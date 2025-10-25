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
        self.config = self.load_config()
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

    def load_config(self):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

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
        
        xp_ganho = 5
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