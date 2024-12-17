import disnake
from disnake.ext import commands
from disnake import Embed
import os
import json

class UserLevel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Путь к файлу с данными пользователей
        self.base_path = os.path.dirname(os.path.abspath(__file__))  # Путь до server_func
        self.file_path = os.path.join(self.base_path, "../data/member_level.json")  # В папку data

    def read_data(self):
        """Чтение данных из JSON."""
        with open(self.file_path, "r") as file:
            return json.load(file)

    @commands.slash_command(name="level", description="Получить информацию о текущем уровне пользователя")
    async def level(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        """Отображает уровень участника или вызывающего команду."""

        # Если участник не выбран, то используем автора команды
        if not member:
            member = interaction.user

        # Получаем данные о пользователе из JSON
        data = self.read_data()
        user_data = data.get(str(member.id))

        # Если пользователь не найден в базе, то создаем его
        if not user_data:
            await interaction.response.send_message(f"{member.mention} еще не имеет данных о уровне.", ephemeral=True)
            return

        level = user_data["level"]
        xp = user_data["xp"]
        # Квадратичное увеличение опыта
        level_up_xp = 100 * (level ** 2)  # Базовое количество XP для следующего уровня

        xp_needed = level_up_xp - xp  # Необходимый опыт для следующего уровня
        progress = xp / level_up_xp  # Процент заполненности шкалы XP

        # Создаем Embed
        embed = Embed(
            title=f"Статистика участника",
            description=f"Информация о текущем уровне {member.mention}",
            color=disnake.Color.blurple()
        )

        # Добавляем поля с уровнем и опытом
        embed.add_field(name="💎 Текущий уровень", value=level, inline=False)
        embed.add_field(name="⚡ Текущий опыт", value=f"{xp} XP", inline=False)
        embed.add_field(name="⚡ Необходимый опыт для следующего уровня", value=f"{xp_needed} XP", inline=False)

        # Создаем ползунок XP
        progress_bar = self.create_xp_bar(progress)
        embed.add_field(name="🔋 Прогресс", value=progress_bar, inline=False)

        # Добавляем footer с информацией о том, кто запросил команду
        embed.set_footer(
            text=f"Запрашивает: {interaction.user.display_name}", 
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )

        # Отправляем Embed
        await interaction.response.send_message(embed=embed)

    def create_xp_bar(self, progress):
        """Создание визуального ползунка XP в виде строки."""
        total_length = 20  # Длина ползунка
        filled_length = int(total_length * progress)  # Заполненная часть
        bar = "█" * filled_length + "▒" * (total_length - filled_length)  # Ползунок
        return bar

def setup(bot):
    bot.add_cog(UserLevel(bot))
