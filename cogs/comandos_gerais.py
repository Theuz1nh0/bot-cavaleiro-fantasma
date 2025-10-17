import discord
from discord.ext import commands

class ComandosGerais(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    print("teste")

    @commands.command()
    async def salve(self, ctx):
        await ctx.send("bom dia")

    @commands.command()
    async def aviso_info(self, ctx):
        embed = discord.Embed(
            title="📌 Canal de Avisos",
            description=(
                "Este canal é **destinado à criação de avisos** através de um **formulário interativo**.\n\n"
                "Para enviar um aviso:\n"
                "1️⃣ Digite **.formilario** abaixo.\n"
                "2️⃣ Preencha os campos solicitados (título e descrição).\n"
                "3️⃣ Envie o formulário e o aviso aparecerá automaticamente no canal de avisos ✅\n\n"
                "OBS.: Se preferir, pegue seu texo bruto e peça ai Chat GPT para formata-lo para voÇê\n"
                "na forma de markdown para um aviso, igual a este."
                "⚠️ Use este canal **apenas para criar novos avisos**. Mensagens normais devem ser enviadas em outros canais."
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"Canal de avisos do servidor {ctx.guild.name}")

        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(ComandosGerais(bot))