import os
import json
from disnake.ext import commands
from disnake import Embed
import disnake

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Получаем путь до корневой директории проекта
        self.base_path = os.path.dirname(os.path.abspath(__file__))  # Путь до server_func
        self.file_path = os.path.join(self.base_path, "../data/member_level.json")  # Путь к файлу в папке data
        self.level_up_xp = 100  # Базовое количество опыта для повышения уровня
        self.level_roles = {
            5: "784159073385840651",  # Замените на реальные RoleID
            15: "1091074897473720501",  # Замените на реальные RoleID
            25: "1091078506986885212",  # Замените на реальные RoleID
            35: "1091079383210541066",  # Замените на реальные RoleID
            45: "1091079976025075852",  # Замените на реальные RoleID
            55: "1091080623478812724"  # Замените на реальные RoleID
            # Добавь свои уровни и соответствующие им RoleID
        }

        # Проверка на наличие файла
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump({}, file)

    def read_data(self):
        """Чтение данных из JSON."""
        with open(self.file_path, "r") as file:
            return json.load(file)

    def write_data(self, data):
        """Запись данных в JSON."""
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def add_user(self, user_id):
        """Добавление нового пользователя в JSON."""
        data = self.read_data()
        if str(user_id) not in data:
            data[str(user_id)] = {
                "xp": 0, 
                "level": 1, 
                "messages_sent": 0, 
                "level_ups_sent": []  # Инициализация пустого списка для новых пользователей
            }
            self.write_data(data)

    def update_user(self, user_id, xp_gain):
        """Обновление данных пользователя: опыт, сообщения, уровень."""
        data = self.read_data()
        user_data = data.get(str(user_id))
        
        if not user_data:
            self.add_user(user_id)
            user_data = data[str(user_id)]

        # Проверка наличия ключа 'level_ups_sent' и его создание при необходимости
        if 'level_ups_sent' not in user_data:
            user_data['level_ups_sent'] = []

        # Обновляем данные
        user_data["xp"] += xp_gain
        user_data["messages_sent"] += 1
        
        # Квадратичное увеличение опыта
        next_level_xp = self.level_up_xp * (user_data["level"] ** 2)  # Квадратичное увеличение

        # Проверка уровня
        level_up_occurred = False
        if user_data["xp"] >= next_level_xp:
            user_data["level"] += 1
            user_data["xp"] -= next_level_xp  # Убираем избыточный опыт
            level_up_occurred = True
        
        # Проверка, был ли уже отправлен уровень
        if level_up_occurred and user_data["level"] not in user_data["level_ups_sent"]:
            user_data["level_ups_sent"].append(user_data["level"])  # Записываем, что уровень был отправлен
            data[str(user_id)] = user_data
            self.write_data(data)
            return user_data["level"], True  # Уведомление должно быть отправлено
        else:
            data[str(user_id)] = user_data
            self.write_data(data)
            return user_data["level"], False  # Уведомление не требуется

    async def assign_role(self, member, level):
        """Выдача роли в зависимости от уровня."""
        role_id = self.level_roles.get(level)
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role)
                return role.name
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        """Обработка сообщений участников."""
        if message.author.bot:
            return  # Игнорируем сообщения ботов
        
        # Пропускаем начисление XP, если это слэш-команда
        if hasattr(message, 'interaction') and message.interaction:
            return  # Это слэш-команда, не начисляем XP

        # Обработка обычных сообщений
        user_id = message.author.id
        xp_gain = 10  # Опыт за сообщение
        self.add_user(user_id)  # Убедимся, что пользователь есть в базе
        new_level, level_up_sent = self.update_user(user_id, xp_gain)
        
        # Отправка уведомления о повышении уровня, только если еще не отправлялось
        if new_level > 1 and level_up_sent and message.channel:
            member = message.guild.get_member(user_id)
            role_name = await self.assign_role(member, new_level)

            # Создаем Embed сообщение
            embed = Embed(
                title="",  # Пустой заголовок
                description=f"🎉 {message.author.mention} достиг уровня {new_level}!\n\n"
                            f"{f'**Роль за уровень:** {role_name}' if role_name else ''}",
                color=disnake.Color.from_rgb(255, 182, 193)  # Нежно-розовый цвет
            )

            # Отправляем Embed
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_application_command(self, interaction):
        """Перехват слэш-команд."""
        # Просто игнорируем команды - нет начисления опыта
        return

def setup(bot):
    bot.add_cog(LevelSystem(bot))
