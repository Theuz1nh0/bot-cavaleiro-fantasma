import discord
from discord.ext import commands
from utils.forms import FormularioView
from utils.checks import canal_permitido

CANAL_AUTORIZADO = "┊formulários"
CANAL_FORMULARIO = 1428595023615889440

class Formulario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @canal_permitido([CANAL_FORMULARIO])
    @commands.command()
    async def aviso(self, ctx):
        await ctx.message.delete(delay=60)
        #---  Envia o botão para abrir o formulário ---#
        view = FormularioView(ctx.guild)
        await ctx.send("Escolha o canal onde o aviso será enviado:", delete_after=60, view=view)

async def setup(bot):
    await bot.add_cog(Formulario(bot))