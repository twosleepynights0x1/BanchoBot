import disnake
from disnake.ext import commands
import json

# Загружаем конфигурацию из JSON файла
with open('conf/config.json', 'r') as f:
    config = json.load(f)

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, interaction, member, action):
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
                log_embed.add_field(name="Новый никнейм:", value=action["new_nickname"], inline=False)
                log_embed.set_thumbnail(url=member.display_avatar.url)
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

    @commands.slash_command(name="nickname", description="Изменить никнейм выбранного участника")
    async def change_nickname(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        member: disnake.Member, 
        new_nickname: str
    ):
        """Изменяет никнейм выбранного участника и отправляет embed с подтверждением"""
        
        # Меняем никнейм участника
        await member.edit(nick=new_nickname)
        
        # Создаем embed для подтверждения
        embed = disnake.Embed(
            title="Никнейм успешно изменен",
            description=f'Параметры участника {member.mention} были успешно изменены',
            color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
        )
        
        # Устанавливаем аватарку участника справа сверху
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Устанавливаем footer с именем и аватаркой администратора, который использовал команду
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправляем embed
        await interaction.response.send_message(embed=embed)

        # Логируем действие
        action = {
            "command": "nickname",   # Строка с командой
            "new_nickname": new_nickname          # Новый никнейм
        }
        await self.log_action(interaction, member, action)  # Логируем действие

def setup(bot):
    bot.add_cog(Nickname(bot))
