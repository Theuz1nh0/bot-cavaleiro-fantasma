import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
from config import carregar_config

class AvisoModal(Modal, title="📋 Criar novo aviso"):
    def __init__(self, bot, canal_destino):
        super().__init__()
        self.bot = bot
        self.canal_destino = canal_destino

    titulo = discord.ui.TextInput(
        label="Título do aviso",
        placeholder="Digite o título...",
        required=True,
        max_length=100
    )

    descricao = discord.ui.TextInput(
        label="Descrição do aviso",
        style=discord.TextStyle.paragraph,
        placeholder="Escreva os detalhes aqui...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Integration):
        embed = discord.Embed(
            title=f"📢 {self.titulo.value}",
            description=self.descricao.value,
            color=discord.Color.orange()
        )

        # Define a imagem do servidor como thumbnail
        if self.canal_target.guild.icon:    # verifica se o servidor tem ícone
            embed.set_thumbnail(url=self.canal_target.guild.icon.url)
        
        await self.canal_target.send(embed=embed)
        await interaction.response.send_message("✅ Aviso enviado com sucesso!", ephemeral=False)
        msg = await interaction.original_response()
        await asyncio.sleep(10)
        await msg.delete()

class CanalSelect(Select):
    def __init__(self, bot):
        self.bot = bot
        config = carregar_config()
        canais_ids = config.get("canais_para_aviso", [])
        options = []

        for canal_id in canais_ids:
            canal = bot.get_channel(canal_id)
            if canal and isinstance(canal, discord.TextChannel):
                options.append(discord.SelectOption(label=canal.name, value=str(canal.id)))

        if not options:
            options = [discord.SelectOption(label="Nenhum canal disponível", value="none")]

        super().__init__(
            placeholder="Escolha o canal de destino...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Integration):
        if self.values[0] == "none":
            await interaction.response.send_message("⚠️ Nenhum canal foi configurado ainda.", ephemeral=True)
            return
        
        canal_id = int(self.values[0])
        canal_destino = self.bot.get_channel(canal_id)
        modal = AvisoModal(self.bot, canal_destino)
        await interaction.response.send_modal(modal)
        
class FormularioView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CanalSelect(bot))