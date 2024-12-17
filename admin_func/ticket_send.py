import disnake
from disnake.ext import commands
from disnake.ui import Button, View
import json

# Загрузка конфигурации из JSON файла
with open('conf/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


class SupportTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ticket_msg", description="Отправить сообщение для открытия тикета.")
    async def ticket_msg(
        self,
        inter: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel
    ):
        """Отправляет сообщение с кнопкой для открытия тикета."""
        # Проверка на права
        user_roles = {role.id for role in inter.user.roles}
        admin_roles = set(config["ADMIN"])

        if not user_roles & admin_roles:
            await inter.response.send_message(
                "У вас недостаточно прав для использования этой команды.",
                ephemeral=True
            )
            return

        # Создание Embed для сообщения
        embed = disnake.Embed(
            title="Возникли вопросы?",
            description="Вы можете открыть обращение, напрямую ожидая помощи от администрации",
            color=disnake.Color.green()
        )
        embed.set_image(url="https://i.pinimg.com/originals/fd/db/60/fddb602396802a3de27e2dc30fd75896.gif")
        embed.set_footer(text="Не грустите, мы вам поможем :D")

        # Создание кнопки
        view = View(timeout=None)  # View без тайм-аута, чтобы кнопка оставалась активной после перезагрузки
        button = Button(label="Открыть обращение", style=disnake.ButtonStyle.blurple, custom_id="open_support_ticket")
        view.add_item(button)

        # Отправка сообщения
        await channel.send(embed=embed, view=view)
        await inter.response.send_message("Сообщение с тикетом отправлено!", ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        """Обработка нажатия кнопки для открытия тикета."""
        if interaction.data["custom_id"] != "open_support_ticket":
            return

        # Проверяем, существует ли уже тикет для этого пользователя
        category_id = 878553432053665852
        category = interaction.guild.get_channel(category_id)
        if not category:
            await interaction.response.send_message(
                "Категория для тикетов не найдена. Обратитесь к администратору.",
                ephemeral=True
            )
            return

        existing_channel = disnake.utils.get(
            category.channels, name=f"ticket-{interaction.user.name.lower()}"
        )
        if existing_channel:
            await interaction.response.send_message(
                f"У вас уже есть открытый тикет: {existing_channel.mention}",
                ephemeral=True
            )
            return

        # Создание нового канала
        overwrites = {
            interaction.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
            interaction.user: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.guild.get_role(1294045970975428628): disnake.PermissionOverwrite(view_channel=True),
            interaction.guild.get_role(784160890761117767): disnake.PermissionOverwrite(view_channel=True),
            interaction.guild.get_role(1025668964447158322): disnake.PermissionOverwrite(view_channel=True),
        }

        ticket_channel = await category.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            overwrites=overwrites
        )

        # Отправка Embed в новый канал
        embed = disnake.Embed(
            title=f"{interaction.user.display_name} открывает обращение",
            description="Не переживайте, совсем скоро вам помогут 🌅",
            color=disnake.Color.blue()
        )
        embed.set_image(url="https://i.pinimg.com/originals/dc/f3/7a/dcf37a91bd27c05db5cfa4906176513d.gif")

        await ticket_channel.send("@everyone", embed=embed)

        # Ответ пользователю
        await interaction.response.send_message(
            f"Тикет создан: {ticket_channel.mention}", ephemeral=True
        )


def setup(bot):
    bot.add_cog(SupportTicket(bot))
