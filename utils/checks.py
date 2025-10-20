from discord.ext import commands

def canal_permitido(canais):
    async def predicate(ctx):
        if ctx.channel.id not in canais:
            await ctx.message.delete(delay=5)
            await ctx.send(f"⚠️ {ctx.author.mention}, esse comando não pode ser usado aqui.", delete_after=5)
            return False
        return True
    return commands.check(predicate)