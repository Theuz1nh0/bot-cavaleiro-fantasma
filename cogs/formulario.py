import discord
from discord.ext import commands
from utils.forms import AvisoModal, CanalSelect, FormularioView

CANAL_AUTORIZADO = "┊formulários"

class Formulario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def formulario(self, ctx):
        if ctx.channel.name != CANAL_AUTORIZADO:
            await ctx.send(f"❌ Este comando só pode ser usado no canal #{CANAL_AUTORIZADO}.", delete_after=10)
            return

        await ctx.message.delete(delay=60)
        #---  Envia o botão para abrir o formulário ---#
        view = FormularioView(ctx.guild)
        await ctx.send("Escolha o canal onde o aviso será enviado:", delete_after=60, view=view)

async def setup(bot):
    await bot.add_cog(Formulario(bot))