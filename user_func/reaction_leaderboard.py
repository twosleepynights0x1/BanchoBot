import disnake
from disnake.ext import commands
from collections import Counter
import json
import os

class ServerReactionTop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_path, "conf/config.json")
        self.data_path = os.path.join(self.base_path, "data/reaction_data.json")
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        self.reaction_data = self.load_reaction_data()
        self.save_reaction_data()

    def load_reaction_data(self):
        """Загружаем или инициализируем данные по реакциям"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Файл reaction_data.json пуст или повреждён. Инициализация пустого словаря.")
                return {}
        return {}

    def save_reaction_data(self):
        """Сохраняем данные по реакциям в файл"""
        with open(self.data_path, "w") as f:
            json.dump(self.reaction_data, f)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: disnake.Reaction, user: disnake.User):
        """Отслеживаем реакции, добавляем их в данные"""
        if user.bot:
            return  # Игнорируем ботов
        
        user_id = str(user.id)
        if user_id not in self.reaction_data:
            self.reaction_data[user_id] = 0
        self.reaction_data[user_id] += 1

        self.save_reaction_data()

    @commands.slash_command(description="Показать топ участников по реакциям.")
    async def reaction_leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        """Отображаем топ-участников по количеству реакций"""
        # Сортируем пользователей по количеству реакций
        sorted_users = sorted(self.reaction_data.items(), key=lambda x: x[1], reverse=True)
        top_users = sorted_users[:10]
        
        embed = disnake.Embed(
            title="🏆 Топ участников по реакциям",
            description=f"Топ-реактивных пользователей на сервере на {disnake.utils.format_dt(disnake.utils.utcnow(), 'D')}",
            color=disnake.Color.gold()
        )

        embed.set_image(url=self.config["REACTION_TOP_IMAGE"])

        if top_users:
            for idx, (user_id, reactions) in enumerate(top_users, start=1):
                user = await self.bot.fetch_user(user_id)
                # Форматирование текста с никнеймом, пингом и количеством реакций
                embed.add_field(
                    name=f"{idx}. {user.display_name}",
                    value=f"{user.mention} - Реакций: {reactions} ",
                    inline=False
                )
        else:
            embed.add_field(
                name="Нет данных",
                value="Пока никто не поставил реакции.",
                inline=False
            )

        embed.set_footer(text="Статистика обновляется в реальном времени.")
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerReactionTop(bot))
