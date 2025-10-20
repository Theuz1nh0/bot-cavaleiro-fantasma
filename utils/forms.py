import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
from config import carregar_config


class AvisoModal(Modal, title="📋 Criar novo aviso"):
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

    def __init__(self, bot, canal_destino: discord.TextChannel):
        super().__init__()
        self.bot = bot
        self.canal_destino = canal_destino

        # print(f"teste para AvisoModal: {canal_destino}")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        canal = self.canal_destino
        if canal is None:
            await interaction.followup.send("❌ Canal de destino não encontrado.", ephemeral=True)
            return
        
        perms = canal.permissions_for(interaction.guild.me)
        if not perms.send_messages:
            await interaction.followup.send("❌ Não tenho permissão para enviar mensagens nesse canal.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📢 {self.titulo.value}",
            description=self.descricao.value,
            color=discord.Color.orange()
        )

        # Define a imagem do servidor como thumbnail
        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        try:
            await canal.send(embed=embed)
        except Exception as e:
            # logue a exceção no console para debugar
            print("Erro ao enviar embed:", repr(e))
            await interaction.followup.send("❌ Falha ao enviar o aviso. Verifique permissões e se o canal existe.", ephemeral=True)
            return

        await interaction.followup.send("✅ Aviso enviado com sucesso!", ephemeral=True)
        # msg = await interaction.original_response()
        # await asyncio.sleep(10)
        # await msg.delete()


class CanalSelect(Select):
    def __init__(self, bot):
        self.bot = bot
        config = carregar_config()
        canais_ids = config.get("canais_para_aviso", [])
        options = []

        for canal_id in canais_ids:
            canal = bot.get_channel(canal_id)
            if canal and isinstance(canal, discord.TextChannel):
                options.append(discord.SelectOption(
                    label=canal.name, value=str(canal.id)))

        if not options:
            options = [discord.SelectOption(
                label="Nenhum canal disponível", value="none")]

        super().__init__(
            placeholder="Escolha o canal de destino...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("⚠️ Nenhum canal foi configurado ainda.", ephemeral=True)
            return

        canal_id = int(self.values[0])
        canal_destino = self.bot.get_channel(canal_id)
        modal = AvisoModal(self.bot, canal_destino)

        # print(f"teste para CanalSect: {canal_destino}")
        await interaction.response.send_modal(modal)


class FormularioView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CanalSelect(bot))
