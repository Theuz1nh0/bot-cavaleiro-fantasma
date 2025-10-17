import discord
from discord.ext import commands
from utils.forms import AvisoModal, FormularioButton

class Formulario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def formulario(self, ctx):
        #---  Envia o botão para abrir o formulário ---#
        view = FormularioButton()
        await ctx.send("Clique no botão abaixo para enviar um aviso:", view=view)

async def setup(bot):
    await bot.add_cog(Formulario(bot))