import disnake
from disnake.ext import commands
import json

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.slash_command(name="commands", description="Показать список всех доступных команд")
    async def commands(self, interaction: disnake.ApplicationCommandInteraction):
        """Отправляет эмбед со списком всех доступных команд"""
        
        embed = disnake.Embed(
            title="Список доступных команд",
            description="Здесь собраны все команды, которые вы можете использовать:",
            color=disnake.Color.from_rgb(255, 182, 193)  # Нежно-розовый цвет
        )

        commands_list = [
            ("`/color_picker`", "Генерация случайного цвета"),
            ("`/roll`", "Бросить кубик и получить результат"), 
            ("`/history`", "Создает интерактивную историю на основе ваших ответов"),
            ("`/engagement`", "Показать общую вовлечённость сервера"),
            ("`/activity_day_leaderboard`", "Показать активность сервера за текущий день"),
            ("`/invite_leaderboard`", "Показать топ участников по количеству приглашений"),
            ("`/level_leaderboard`", "Таблица лидеров по уровням"),
            ("`/reaction_leaderboard`", "Показать топ участников по реакциям"),
            ("`/level`", "Получить информацию о текущем уровне пользователя"),
            ("`/profile`", "Получить подробную информацию о участнике")
        ]

        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.set_image(url=self.config["FAQ_IMAGE"])
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Commands(bot))

