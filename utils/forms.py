import discord
from discord.ext import commands
from config import CANAL_FORMULARIO_ID, CANAL_AVISOS_ID

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

    async def on_submit(self, interaction: discord.Integration):
        canal_avisos = interaction.client.get_channel(CANAL_AVISOS_ID)
        if not canal_avisos:
            await interaction.response.send_mensage("⚠️ Canal de avisos não encontrado!", ephemeral=True)
            return
        

        embed = discord.Embed(
            title=f"📢 {self.titulo.value}",
            description=self.descricao.value,
            color=discord.Color.orange()
        )
        
        await canal_avisos.send(embed=embed)
        await interaction.response.send_message("✅ Aviso enviado com sucesso!", ephemeral=True)


class FormularioButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir formulário", style=discord.ButtonStyle.primary, emoji="📝")
    async def abrir_form(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel_id != CANAL_FORMULARIO_ID:
            await interaction.response.send_message(
                "⚠️ Esse formulário só pode ser usado no canal correto!",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(AvisoModal())