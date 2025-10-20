import discord
from discord.ext import commands
from utils.forms import FormularioView
from utils.checks import canal_permitido
from config import carregar_config, salvar_config

CANAL_FORMULARIO = 1428595023615889440
CANAL_COMANDOS = 1428430208121442367

class Formulario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @canal_permitido([CANAL_FORMULARIO])
    @commands.command(name="aviso")
    async def formulario(self, ctx):
        await ctx.message.delete(delay=60)
        #---  Envia o botão para abrir o formulário ---#
        view = FormularioView(self.bot)
        await ctx.send("Escolha o canal onde o aviso será enviado:", delete_after=60, view=view)

    @canal_permitido([CANAL_COMANDOS])
    @commands.command(name="setcanalaviso")
    @commands.has_permissions(administrator=True)
    async def set_canal_aviso(self, ctx, canal: discord.TextChannel):
        config = carregar_config()
        canais = config.get("canais_para_aviso", [])

        if canal.id in canais:
            await ctx.send("⚠️ Esse canal já está na lista de permitidos.")
            return

        canais.append(canal.id)
        config["canais_para_aviso"] = canais
        salvar_config(config)
        await ctx.send(f"✅ Canal {canal.mention} foi adicionado à lista de permitidos!")

    @canal_permitido([CANAL_COMANDOS])
    @commands.command(name="removecanalaviso")
    @commands.has_permissions(administrator=True)
    async def remove_canal_aviso(self, ctx, canal: discord.TextChannel):
        config = carregar_config()
        canais = config.get("canais_para_aviso", [])

        if canal.id not in canais:
            await ctx.send("⚠️ Esse canal não está na lista.")
            return
        
        canais.remove(canal.id)
        config["canais_para_aviso"] = canais
        salvar_config(config)
        await ctx.send(f"❌ Canal {canal.mention} foi removido da lista de permitidos!")

    @commands.command(name="listarcanaisaviso")
    async def list_canais_aviso(self, ctx):
        config = carregar_config()
        canais = config.get("canais_para_aviso", [])

        if not canais:
            await ctx.send("📭 Nenhum canal foi configurado ainda.")
            return
        
        lista = "\n".join(f"<#{cid}>" for cid in canais)
        await ctx.send(f"📋 **Canais permitidos:**\n{lista}")

async def setup(bot):
    await bot.add_cog(Formulario(bot))