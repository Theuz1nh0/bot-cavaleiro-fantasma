import discord
from discord.ext import commands


class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#---------- COMANDO PARA ENTRADA DE MEMBROS -----------#
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(
            member.guild.text_channels, name="🟢➦𝕖𝕟𝕥𝕣𝕒𝕕𝕒")

        if not channel:
            print("Canal não encontrado!")
            return

        user_avatar = member.display_avatar.url
        server_name = member.guild.name
        server_icon = member.guild.icon.url
        member_numbers = member.guild.member_count

        embed = discord.Embed(
        title=f"Bem-vindo(a) à {server_name}",
        description=(
            f"Salve {member.mention}"
            f"\nCom você agora temos {member_numbers} membros!"),
        color=discord.Color.green()
        )
        embed.set_thumbnail(url=user_avatar)
        embed.set_author(name=server_name, icon_url=server_icon)

        await channel.send(embed=embed)

#---------- COMANDO PARA SAÍDA DE MEMBROS -----------#
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="🔴➥𝕤𝕒í𝕕𝕒")

        if not channel:
            print("Canal não encontrado!")
            return

        user_avatar = member.display_avatar.url
        server_name = member.guild.name
        server_icon = member.guild.icon.url

        embed = discord.Embed(
            description=(
                f"Infelizmente {member.mention} saiu do servidor..."),
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=user_avatar)
        embed.set_author(name=server_name, icon_url=server_icon)

        await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Eventos(bot))
