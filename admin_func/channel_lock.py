import disnake
from disnake.ext import commands
import json  # Импортируем json для чтения конфига

class ChannelLock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("conf/config.json", "r") as f:
            self.config = json.load(f)

    async def log_action(self, interaction, action):
        """Создает embed для логирования и отправляет его в лог-канал."""
        log_channel_id = self.config["ADMIN_LOG_CHANNEL"]
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            try:
                log_embed = disnake.Embed(
                    title="Log",
                    color=disnake.Color.blue()
                )
                log_embed.add_field(name="Команда:", value=f"/{action}", inline=False)
                log_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                log_embed.set_footer(
                    text=f"Администратор: {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url
                )
                log_embed.timestamp = interaction.created_at

                await log_channel.send(embed=log_embed)
                print(f"Лог отправлен: {action}")
            except Exception as e:
                print(f"Ошибка при отправке лога: {e}")
                # Если ошибка, попробуем отправить сообщение в общий канал
                await interaction.followup.send("Не удалось отправить лог в канал.", ephemeral=True)
        else:
            print(f"Канал для логирования с ID {log_channel_id} не найден.")
            # Если канал не найден, отправим сообщение в общий канал
            await interaction.followup.send("Канал для логирования не найден.", ephemeral=True)

    @commands.slash_command(name="channel_lock", description="Закрыть канал для выбранной роли")
    async def channel_lock(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        channel: disnake.TextChannel, 
        role: disnake.Role
    ):
        """Закрывает канал для выбранной роли"""
        
        # Проверка, что у пользователя есть нужная роль
        if not any(r.id in self.config["ADMIN"] for r in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Получаем разрешения для роли
        permissions = channel.overwrites_for(role)
        
        # Блокируем канал для роли
        permissions.send_messages = False
        permissions.view_channel = False  # Роль не будет видеть канал

        # Применяем изменения
        await channel.set_permissions(role, overwrite=permissions)

        # Создаем embed для подтверждения
        embed = disnake.Embed(
            title="Канал закрыт для роли!",
            description=f"Канал {channel.mention} был закрыт для роли {role.mention}. Пользователи с этой ролью не могут отправлять сообщения и видеть канал.",
            color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
        )
        
        # Устанавливаем аватарку бота справа сверху
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Устанавливаем footer с именем и аватаркой администратора, который использовал команду
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправляем embed
        await interaction.response.send_message(embed=embed)

        # Логируем действие
        await self.log_action(interaction, "channel_lock")

    @commands.slash_command(name="channel_unlock", description="Открыть канал для выбранной роли")
    async def channel_unlock(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        channel: disnake.TextChannel, 
        role: disnake.Role
    ):
        """Открывает канал для выбранной роли"""
        
        # Проверка, что у пользователя есть нужная роль
        if not any(r.id in self.config["ADMIN"] for r in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Получаем разрешения для роли
        permissions = channel.overwrites_for(role)
        
        # Разблокируем канал для роли
        permissions.send_messages = True
        permissions.view_channel = True  # Роль будет видеть канал

        # Применяем изменения
        await channel.set_permissions(role, overwrite=permissions)

        # Создаем embed для подтверждения
        embed = disnake.Embed(
            title="Канал открыт для роли!",
            description=f"Канал {channel.mention} был открыт для роли {role.mention}. Пользователи с этой ролью теперь могут отправлять сообщения и видеть канал.",
            color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
        )
        
        # Устанавливаем аватарку бота справа сверху
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Устанавливаем footer с именем и аватаркой администратора, который использовал команду
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправляем embed
        await interaction.response.send_message(embed=embed)

        # Логируем действие
        await self.log_action(interaction, "channel_unlock")

def setup(bot):
    bot.add_cog(ChannelLock(bot))
