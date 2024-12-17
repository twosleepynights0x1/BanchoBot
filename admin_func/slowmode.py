import disnake
from disnake.ext import commands
import json # Для работы с JSON файлом

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @commands.slash_command(name="slowmode", description="Установить задержку между сообщениями в канале")
    async def slowmode(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        channel: disnake.TextChannel, 
        time: int
    ):
        """Устанавливает задержку (slowmode) для выбранного канала"""
        
        # Проверка, что у пользователя есть нужная роль
        if not any(role.id in self.config["ADMIN"] for role in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Создание embed для основного ответа
        if time == 0:
            await channel.edit(slowmode_delay=0)
            embed = disnake.Embed(
                title="Режим замедления отключен!",
                description=f"В канале {channel.mention} была отключена задержка между сообщениями.",
                color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
            )
            action_text = "Режим замедления отключен"
        else:
            await channel.edit(slowmode_delay=time)
            embed = disnake.Embed(
                title="Режим замедления установлен!",
                description=f"В канале {channel.mention} была установлена задержка между сообщениями: {time} секунд.",
                color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
            )
            action_text = f"Режим замедления активирован на {time} секунд"
        
        # Устанавливаем аватарку бота справа сверху
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # Устанавливаем footer с именем и аватаркой администратора, который использовал команду
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправляем embed-ответ
        await interaction.response.send_message(embed=embed)

        # Логирование действия в канал ADMIN_LOG_CHANNEL
        log_channel_id = self.config["ADMIN_LOG_CHANNEL"]
        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel:
            log_embed = disnake.Embed(
                title="Log",
                color=disnake.Color.blue()
            )
            # Поле с информацией о команде
            log_embed.add_field(name="Команда:", value="slowmode", inline=False)
            log_embed.add_field(name="Канал:", value=channel.mention, inline=False)
            log_embed.add_field(name="Задержка:", value=f"{time} секунд" if time > 0 else "Отключена", inline=False)

            # Аватарка администратора справа сверху
            log_embed.set_thumbnail(url=interaction.user.display_avatar.url)

            # Footer с именем администратора и его аватаркой
            log_embed.set_footer(
                text=f"Администратор: {interaction.user.display_name}", 
                icon_url=interaction.user.display_avatar.url
            )
            log_embed.timestamp = interaction.created_at
            
            await log_channel.send(embed=log_embed)

def setup(bot):
    bot.add_cog(Slowmode(bot))
