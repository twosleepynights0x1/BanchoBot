import disnake
from disnake.ext import commands, tasks
from datetime import datetime, time
import json
import os

class ServerActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_message_count = self.load_activity_data()
        self.reset_daily_activity.start()  # Запуск задачи сброса данных

    def load_activity_data(self):
        # Загрузка данных из файла activity_day.json или инициализация пустого словаря
        if os.path.exists("data/activity_day.json"):
            try:
                with open("data/activity_day.json", "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Если файл пуст или повреждён, возвращаем пустой словарь
                print("Файл activity_day.json пуст или повреждён. Инициализация пустого словаря.")
                return {}
        return {}

    def save_activity_data(self):
        # Сохранение данных в файл activity_day.json
        with open("data/activity_day.json", "w") as f:
            json.dump(self.daily_message_count, f)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # Игнорировать сообщения бота и ботов
        if message.author == self.bot.user or message.author.bot:
            return

        # Получаем текущую дату в формате строки
        today = datetime.now().strftime('%Y-%m-%d')

        # Инициализация данных по сообщениям для текущего дня
        if today not in self.daily_message_count:
            self.daily_message_count[today] = {}

        # Увеличение счётчика сообщений для пользователя
        user_id = str(message.author.id)
        if user_id not in self.daily_message_count[today]:
            self.daily_message_count[today][user_id] = 0
        self.daily_message_count[today][user_id] += 1

        # Сохранение данных в файл
        self.save_activity_data()

    @commands.slash_command(description="Показать активность сервера за текущий день.")
    async def activity_day_leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Загрузка конфигурации
        with open("conf/config.json", "r") as f:
            config = json.load(f)
        
        # Проверка, есть ли данные за сегодня
        if today not in self.daily_message_count or not self.daily_message_count[today]:
            await inter.send("Сегодня ещё нет данных для активности участников.", ephemeral=True)
            return

        # Сортировка участников по количеству сообщений
        sorted_users = sorted(
            self.daily_message_count[today].items(),
            key=lambda item: item[1],
            reverse=True
        )
        
        # Ограничиваем вывод до топ-10 участников
        top_10_users = sorted_users[:10]

        # Создание embed для вывода топ-10
        embed = disnake.Embed(
            title="🏆 Топ 10 участников по активности за сегодняшний день",
            description=f"Дата: {today}",
            color=disnake.Color.gold()
        )

        # Заполнение данных по каждому участнику с использованием имён и упоминаний в значениях
        for index, (user_id, message_count) in enumerate(top_10_users, start=1):
            user = await self.bot.fetch_user(int(user_id))
            mention = f"<@{user_id}>"
            embed.add_field(
                name=f"{index}. {user.display_name}",
                value=f"{mention} — Сообщений: {message_count}",
                inline=False
            )

        # Установка изображения для embed из config.json
        embed.set_image(url=config["ACTIVITY_DAY_IMAGE"])

        embed.set_footer(text="Статистика обновляется в реальном времени.")
        await inter.send(embed=embed)

    @tasks.loop(time=time(0, 0))
    async def reset_daily_activity(self):
        # Очистка данных в полночь
        self.daily_message_count = {}
        self.save_activity_data()
        print("Данные активности сброшены и сохранены в 00:00.")

    @reset_daily_activity.before_loop
    async def before_reset(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(ServerActivity(bot))
