import disnake
from disnake.ext import commands
from disnake import Embed
import json
import os

class ServerMemberInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Путь к файлу с данными пользователей
        self.base_path = os.path.dirname(os.path.abspath(__file__))  # Путь до server_func
        self.file_path = os.path.join(self.base_path, "../data/member_level.json")  # В папку data

    def read_data(self):
        """Чтение данных из JSON."""
        with open(self.file_path, "r") as file:
            return json.load(file)

    @commands.slash_command(name="profile", description="Получить подробную информацию о участнике")
    async def server_member_info(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member):
        """Отправляет embed с подробной информацией о пользователе и его ролях в обратном порядке."""
        
        # Форматируем время присоединения
        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")

        # Получаем роли участника в обратном порядке
        roles = [role.mention for role in reversed(member.roles) if role != interaction.guild.default_role]
        roles = roles if roles else ["Нет ролей"]

        # Попробуем получить баннер через fetch_member
        try:
            fetched_member = await interaction.guild.fetch_member(member.id)  # Загружаем полные данные

            # Проверяем, есть ли баннер
            if fetched_member.banner:
                banner_url = fetched_member.banner.url  # Получаем URL баннера
            else:
                banner_url = None
        except Exception as e:
            print(f"Ошибка при получении данных о баннере для {member.display_name}: {e}")
            banner_url = None  # Если возникла ошибка, установим баннер как None

        # Делаем defer, чтобы отложить ответ
        await interaction.response.defer()

        # Получаем данные из JSON о пользователе
        data = self.read_data()
        user_data = data.get(str(member.id))
        
        # Устанавливаем информацию о уровне и опыте (если пользователь есть в данных)
        level = user_data["level"] if user_data else "Не доступно"
        xp = user_data["xp"] if user_data else "Не доступно"

        # Создаем Embed сообщение
        embed = Embed(
            title=f"Информация о участнике {member.display_name}",
            description=f"Информация о пользователе {member.mention}",
            color=disnake.Color.blurple()
        )

        # Добавляем баннер, если он есть
        if banner_url:
            embed.set_image(url=banner_url)  # Если баннер существует, показываем его
        else:
            embed.set_image(url=None)  # Если нет баннера, ничего не выводим

        # Добавляем аватар пользователя
        embed.set_thumbnail(url=member.avatar.url)

        # Добавляем дополнительные поля
        embed.add_field(name="🆔 ID", value=member.id, inline=False)
        embed.add_field(name="📅 Присоединился", value=joined_at, inline=False)
        embed.add_field(name="📅 Создан", value=created_at, inline=False)
        embed.add_field(name="💎 Уровень", value=level, inline=False)
        embed.add_field(name="⚡ Опыт", value=f"{xp} XP", inline=False)

        # Роли добавляем последним
        embed.add_field(name="👥 Роли", value=" ".join(roles), inline=False)

        # Отправляем Embed
        await interaction.edit_original_response(embed=embed)

def setup(bot):
    bot.add_cog(ServerMemberInfo(bot))
