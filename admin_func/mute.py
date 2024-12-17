import disnake
from disnake.ext import commands
from disnake import Embed
import datetime
import asyncio  # Мы добавляем asyncio для работы с асинхронными задержками
import json

# Загружаем конфигурацию из JSON файла
with open('conf/config.json', 'r') as f:
    config = json.load(f)

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_role_id = config.get('MuteRole')  # ID роли мьюта
        self.allowed_roles = config.get('ADMIN', [])  # ID ролей, которые могут использовать команду мьют

    async def log_action(self, interaction, member, action, duration=None):
        """Создает embed для логирования и отправляет его в лог-канал."""
        log_channel_id = config.get('ADMIN_LOG_CHANNEL')
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            try:
                log_embed = disnake.Embed(
                    title="Log",
                    color=disnake.Color.blue()
                )
                log_embed.add_field(name="Команда:", value=action["command"], inline=False)
                log_embed.add_field(name="Пользователь:", value=member.mention, inline=False)
                log_embed.add_field(name="Причина:", value=action["reason"], inline=False)
                if duration:
                    log_embed.add_field(name="Срок мьюта:", value=duration, inline=False)
                log_embed.set_thumbnail(url=member.avatar.url)
                log_embed.set_footer(
                    text=f"Администратор: {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url
                )
                log_embed.timestamp = interaction.created_at

                await log_channel.send(embed=log_embed)
                print(f"Лог отправлен: {action['command']} для пользователя {member.name}")
            except Exception as e:
                print(f"Ошибка при отправке лога: {e}")
                await interaction.followup.send("Не удалось отправить лог в канал.", ephemeral=True)
        else:
            print(f"Канал для логирования с ID {log_channel_id} не найден.")
            await interaction.followup.send("Канал для логирования не найден.", ephemeral=True)

    @commands.slash_command(name="mute", description="Замутить пользователя на определенный срок.")
    async def mute(self, inter, member: disnake.Member, duration: str, reason: str = "По решению администрации"):
        """Выдача роли мьюта на указанное время."""
        # Проверка на наличие роли у пользователя, вызывающего команду
        if not any(role.id in self.allowed_roles for role in inter.user.roles):
            await inter.send("У вас нет прав для использования этой команды.")
            return

        # Проверяем, есть ли у пользователя роль мьюта
        mute_role = inter.guild.get_role(self.mute_role_id)
        if mute_role in member.roles:
            await inter.send(f"{member.mention} уже замьючен!")
            return

        # Преобразуем строку в объект времени (например, '1m', '2h', '3d')
        try:
            duration_timedelta = self.convert_duration_to_timedelta(duration)
        except ValueError:
            await inter.send("Неверный формат времени. Пример: 1m (минута), 2h (час), 3d (день).")
            return

        # Выдаем роль мьюта
        await member.add_roles(mute_role)
        unmute_time = datetime.datetime.utcnow() + duration_timedelta

        # Создаем Embed сообщение о мьюте
        embed = Embed(
            title="Пользователь замучен",
            description=f"Пользователь {member.mention} был замьючен на {duration}.",
            color=disnake.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)  # Аватар участника справа сверху
        embed.add_field(name="Срок мьюта", value=f"До {unmute_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        embed.add_field(name="Причина", value=reason)  # Добавляем причину мьюта
        embed.set_footer(text=f"Администратор: {inter.user.name}", icon_url=inter.user.avatar.url)  # Администратор в footer с аватаром
        await inter.send(embed=embed)

        # Логируем действие
        action = {
            "command": "mute",   # Строка с командой
            "reason": reason           # Причина мьюта
        }
        await self.log_action(inter, member, action, unmute_time.strftime('%Y-%m-%d %H:%M:%S UTC'))  # Логируем действие

        # Устанавливаем задачу для размьюта через определенное время
        await asyncio.sleep(duration_timedelta.total_seconds())
        await member.remove_roles(mute_role)

        # Отправляем уведомление о размьюте
        embed = Embed(
            title="Пользователь размучен",
            description=f"Пользователь {member.mention} был размьючен.",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)  # Аватар участника справа сверху
        embed.set_footer(text=f"Администратор: {inter.user.name}", icon_url=inter.user.avatar.url)  # Администратор в footer с аватаром
        await inter.send(embed=embed)

    @commands.slash_command(name="unmute", description="Размутить пользователя.")
    async def unmute(self, inter, member: disnake.Member):
        """Удалить роль мьюта."""
        # Проверка на наличие роли у пользователя, вызывающего команду
        if not any(role.id in self.allowed_roles for role in inter.user.roles):
            await inter.send("У вас нет прав для использования этой команды.")
            return

        mute_role = inter.guild.get_role(self.mute_role_id)
        if mute_role not in member.roles:
            await inter.send(f"{member.mention} не замьючен!")
            return

        # Убираем роль мьюта
        await member.remove_roles(mute_role)

        # Создаем Embed сообщение о размьюте
        embed = Embed(
            title="Пользователь размучен",
            description=f"Пользователь {member.mention} был размьючен.",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)  # Аватар участника справа сверху
        embed.set_footer(text=f"Администратор: {inter.user.name}", icon_url=inter.user.avatar.url)  # Администратор в footer с аватаром
        await inter.send(embed=embed)

        # Логируем действие
        action = {
            "command": "unmute",   # Строка с командой
            "reason": "Нет"              # Причина (уничтожение роли мьюта)
        }
        await self.log_action(inter, member, action)  # Логируем действие

    def convert_duration_to_timedelta(self, duration: str):
        """Конвертировать строку в объект timedelta для времени."""
        if duration.endswith("m"):
            return datetime.timedelta(minutes=int(duration[:-1]))
        elif duration.endswith("h"):
            return datetime.timedelta(hours=int(duration[:-1]))
        elif duration.endswith("d"):
            return datetime.timedelta(days=int(duration[:-1]))
        else:
            raise ValueError("Неверный формат времени.")

# Добавляем Cog в бота
def setup(bot):
    bot.add_cog(Mute(bot))
