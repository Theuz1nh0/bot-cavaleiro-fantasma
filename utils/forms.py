import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio

class AvisoModal(discord.ui.Modal, title="📋 Criar novo aviso"):
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

    def __init__(self, canal_target):
        super().__init__()
        self.canal_target = canal_target

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
    def __init__(self, guild):
        canais_permitidos = ["┊・𝕀𝕟𝕥𝕣𝕠𝕕𝕦𝕔̧𝕒̃𝕠", "┊・𝔸𝕧𝕚𝕤𝕠𝕤"]
        options = []

        for nome in canais_permitidos:
            canal_obj = discord.utils.get(guild.text_channels, name=nome)
            if canal_obj:
                options.append(discord.SelectOption(label=nome, value=str(canal_obj.id)))

        super().__init__(placeholder="Escolha o canal de destino", options=options)

    async def callback(self, interaction: discord.Integration):
        canal_id = int(self.values[0])
        canal_target = interaction.guild.get_channel(canal_id)
        await interaction.response.send_modal(AvisoModal(canal_target))

class FormularioView(View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.add_item(CanalSelect(guild))