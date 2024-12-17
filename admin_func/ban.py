import disnake
from disnake.ext import commands
from disnake import Embed
import json

# Загружаем конфигурацию из JSON файла
with open('conf/config.json', 'r') as f:
    config = json.load(f)

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, interaction, member, action):
        """Создает embed для логирования и отправляет его в лог-канал."""
        log_channel_id = config.get('ADMIN_LOG_CHANNEL', None)
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            try:
                log_embed = disnake.Embed(
                    title="Log",
                    color=disnake.Color.blue()
                )
                log_embed.add_field(name="Команда:", value=action["command"], inline=False)
                log_embed.add_field(name="Заблокирован пользователь:", value=member.mention, inline=False)
                log_embed.add_field(name="Причина блокировки:", value=action["reason"], inline=False)
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

    @commands.slash_command(name="ban", description="Заблокировать пользователя.")
    async def ban(self, inter, member: disnake.Member, reason: str = "По решению администрации"):
        """Блокировка пользователя с указанием причины."""
        
        # Проверка на наличие роли у пользователя, вызывающего команду
        admin_roles = config.get('ADMIN', [])
        if not any(role.id in admin_roles for role in inter.user.roles):
            await inter.send("У вас нет прав для использования этой команды.")
            return

        try:
            await member.ban(reason=reason)

            # Создаем красивый Embed для блокировки
            embed = Embed(
                title="Пользователь заблокирован",
                description=f"Пользователь {member.mention} был заблокирован.",
                color=disnake.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name="Причина", value=reason, inline=False)
            embed.set_footer(text=f"Администратор: {inter.user.name}", icon_url=inter.user.avatar.url)
            await inter.send(embed=embed)

            # Логируем действие
            action = {
                "command": "ban",           # Строка с командой
                "reason": reason                  # Причина блокировки
            }
            await self.log_action(inter, member, action)  # Логируем действие

        except Exception as e:
            await inter.send(f"Не удалось заблокировать пользователя: {e}")

# Добавляем Cog в бота
def setup(bot):
    bot.add_cog(Ban(bot))
