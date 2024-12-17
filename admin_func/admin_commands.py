import disnake
from disnake.ext import commands
import json

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.slash_command(name="admin_commands", description="Показать список всех административных команд")
    async def admin_commands(self, interaction: disnake.ApplicationCommandInteraction):
        """Отправляет эмбед со списком всех административных команд"""
        
        # Проверка прав администратора
        if not any(role.id in self.config["ADMIN"] for role in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        embed = disnake.Embed(
            title="Список административных команд",
            description="Здесь собраны все административные команды:",
            color=disnake.Color.from_rgb(255, 182, 193)  # Нежно-розовый цвет
        )

        commands_list = [
            ("`/ban`", "Заблокировать пользователя"),
            ("`/mute`", "Замутить пользователя на определенный срок"),
            ("`/unmute`", "Размутить пользователя"),
            ("`/channel_lock`", "Закрыть канал для выбранной роли"),
            ("`/channel_unlock`", "Открыть канал для выбранной роли"),
            ("`/role_create`", "Создает роль на сервере"),
            ("`/role_add`", "Добавить роль выбранному участнику"),
            ("`/role_remove`", "Удалить роль у выбранного участника"),
            ("`/role_add_all`", "Выдать роль всем участникам сервера"),
            ("`/role_remove_all`", "Удалить роль у всех участников сервера"),
            ("`/nickname`", "Изменить никнейм выбранного участника"),
            ("`/clear`", "Удалить указанное количество сообщений в канале"),
            ("`/slowmode`", "Установить задержку между сообщениями в канале"),
            ("`/ticket_msg`", "Отправить сообщение c формой открытия тикета")
        ]

        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.set_image(url=self.config["FAQ_IMAGE"])
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(AdminCommands(bot))

