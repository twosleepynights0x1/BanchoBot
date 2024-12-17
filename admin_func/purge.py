import disnake
from disnake.ext import commands
import json
import os

class ClearMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_path, "conf/config.json")
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

    async def log_action(self, interaction, channel, action):
        """Создает embed для логирования и отправляет его в лог-канал."""
        log_channel_id = self.config["ADMIN_LOG_CHANNEL"]
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            try:
                log_embed = disnake.Embed(
                    title="Log",
                    color=disnake.Color.blue()
                )
                log_embed.add_field(name="Команда:", value=action["command"], inline=False)
                log_embed.add_field(name="Канал:", value=channel.mention, inline=False)
                log_embed.add_field(name="Удалено сообщений:", value=str(action["deleted_count"]), inline=False)
                log_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                log_embed.set_footer(
                    text=f"Администратор: {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url
                )
                log_embed.timestamp = interaction.created_at

                await log_channel.send(embed=log_embed)
                print(f"Лог отправлен: {action['command']} для канала {channel.name}")
            except Exception as e:
                print(f"Ошибка при отправке лога: {e}")
                # Если ошибка, попробуем отправить сообщение в общий канал
                await interaction.followup.send("Не удалось отправить лог в канал.", ephemeral=True)
        else:
            print(f"Канал для логирования с ID {log_channel_id} не найден.")
            # Если канал не найден, отправим сообщение в общий канал
            await interaction.followup.send("Канал для логирования не найден.", ephemeral=True)

    @commands.slash_command(name="clear", description="Удалить указанное количество сообщений в канале")
    async def clear(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        channel: disnake.TextChannel, 
        amount: int
    ):
        """Удаляет указанное количество сообщений в выбранном канале"""
        
        # Проверка, что у пользователя есть нужная роль
        if not any(role.id in self.config["ADMIN"] for role in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Проверка на допустимое количество сообщений (от 1 до 100)
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Количество сообщений должно быть от 1 до 100.", ephemeral=True)
            return
        
        # Удаляем сообщения
        deleted = await channel.purge(limit=amount)

        # Создаем embed для подтверждения
        embed = disnake.Embed(
            title="Канал очищен!",
            description=f"В канале {channel.mention} было удалено {len(deleted)} сообщений.",
            color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
        )
        
        # Устанавливаем аватарку бота справа сверху
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Устанавливаем footer с именем и аватаркой администратора, который использовал команду
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправляем embed с подтверждением
        await interaction.response.send_message(embed=embed)

        # Логируем действие
        action = {
            "command": "clear",           # Строка с командой
            "deleted_count": len(deleted)  # Количество удаленных сообщений
        }
        await self.log_action(interaction, channel, action)  # Теперь передаем словарь
        
def setup(bot):
    bot.add_cog(ClearMessages(bot))
