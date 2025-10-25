import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
from config import carregar_config
import aiohttp
import io


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
        await interaction.response.send_message(
            "Agora envie uma imagem para anexar ao aviso (ou digite `pular` para enviar sem imagem).",
            ephemeral=True
        )

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)

            if msg.content.lower() == "pular":
                image_url = None
            elif msg.attachments:
                # Baixa a imagem para anexar junto com o embed
                async with aiohttp.ClientSession() as session:
                    async with session.get(msg.attachments[0].url) as resp:
                        imagem_bytes = io.BytesIO(await resp.read())
                        imagem_bytes.seek(0)
            else:
                await interaction.followup.send("Nenhuma imagem válida foi enviada. Enviando aviso sem imagem.", ephemeral=True)
                image_url = None
            
            embed = discord.Embed(
                title=f"📢 {self.titulo.value}",
                description=self.descricao.value,
                color=discord.Color.orange()
            )

            # Define a imagem do servidor como thumbnail
            if interaction.guild and interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)

            canal = self.canal_destino
            if canal:
                if imagem_bytes:
                    file = discord.File(imagem_bytes, filename="aviso.png")
                    await canal.send(file=file, embed=embed)
                else:
                    await canal.send(embed=embed)
                    
                await interaction.followup.send("✅ Aviso enviado com sucesso!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Canal 'avisos' não encontrado.", ephemeral=True)
            
            await msg.delete()


            # msg = await interaction.original_response()
            # await asyncio.sleep(10)
            # await msg.delete()
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Tempo esgotado. Nenhuma imagem foi enviada.", ephemeral=True)


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
