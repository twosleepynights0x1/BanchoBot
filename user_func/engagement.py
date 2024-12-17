import disnake
from disnake.ext import commands
from datetime import datetime, timedelta
import pytz  # Для работы с временными зонами
import os  # Для работы с файловой системой
import json  # Для работы с JSON файлами

class ServerEngagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.engagement_data = self.load_engagement_data()
        self.save_engagement_data()
        with open("conf/config.json", "r") as f:
            self.config = json.load(f)

    def load_engagement_data(self):
        if os.path.exists("data/engagement_data.json"):
            try:
                with open("data/engagement_data.json", "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Файл engagement_data.json пуст или повреждён. Инициализация пустого словаря.")
                return {}
        return {
            'messages_sent': 0,
            'polls_created': 0,
            'poll_participants': 0,
            'reactions_sent': 0,
            'new_members': 0
        }

    def save_engagement_data(self):
        with open("data/engagement_data.json", "w") as f:
            json.dump(self.engagement_data, f)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user or message.author.bot:
            return
        
        self.engagement_data['messages_sent'] += 1
        
        # Приводим datetime.now() к временной зоне UTC
        utc_now = datetime.now(pytz.utc)

        self.save_engagement_data()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: disnake.Reaction, user: disnake.User):
        if user == self.bot.user:
            return

        self.engagement_data['reactions_sent'] += 1
        self.save_engagement_data()

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if member.joined_at and datetime.now(pytz.utc) - member.joined_at <= timedelta(days=30):
            self.engagement_data['new_members'] += 1
        self.save_engagement_data()

    @commands.Cog.listener()
    async def on_poll_create(self, poll):  
        self.engagement_data['polls_created'] += 1
        self.save_engagement_data()

    @commands.Cog.listener()
    async def on_poll_participation(self, participant):  
        self.engagement_data['poll_participants'] += 1
        self.save_engagement_data()

    @commands.slash_command(description="Показать общую вовлечённость сервера.")
    async def engagement(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="📊 Вовлечённость сервера",
            description=f"Данные по вовлечённости на сервере на {datetime.now().strftime('%Y-%m-%d')}",
            color=disnake.Color.gold()
        )

        embed.set_image(url=self.config["ENGAGEMENT_IMAGE"])

        embed.add_field(
            name="💬 Сообщения",
            value=f"Общее количество сообщений: {self.engagement_data['messages_sent']}",
            inline=False
        )
        embed.add_field(
            name="📊 Голосования",
            value=f"Количество голосований: {self.engagement_data['polls_created']}",
            inline=False
        )
        embed.add_field(
            name="🙋‍♂️ Участники опросов",
            value=f"Количество участников опросов: {self.engagement_data['poll_participants']}",
            inline=False
        )
        embed.add_field(
            name="❤️ Реакции",
            value=f"Общее количество реакций: {self.engagement_data['reactions_sent']}",
            inline=False
        )
        embed.add_field(
            name="🆕 Новые участники за месяц",
            value=f"Новых участников: {self.engagement_data['new_members']}",
            inline=False
        )

        if self.engagement_data['messages_sent'] > 0:
            avg_messages_per_day = self.engagement_data['messages_sent'] / (datetime.now().day)
            embed.add_field(
                name="📈 Среднее количество сообщений на пользователя за день",
                value=f"{avg_messages_per_day:.2f}",
                inline=False
            )

        embed.set_footer(text="Статистика обновляется в реальном времени.")
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerEngagement(bot))
