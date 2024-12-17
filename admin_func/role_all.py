import disnake
from disnake.ext import commands
from disnake.ui import Button, View
import json  # Для работы с JSON файлом
import asyncio  # Для асинхронной работы с длительными операциями

class ServerRoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cancelled = False  # Флаг для отмены операции
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    async def cancel_operation(self, interaction, embed, action):
        """Отменяет операцию и отправляет embed с сообщением об отмене."""
        self.cancelled = True  # Устанавливаем флаг отмены
        embed.title = f"Операция {action} отменена!"
        embed.description = f"Процесс {action} был отменен администраторами в процессе выполнения."
        
        # Отправляем сообщение об отмене
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                await interaction.followup.send(embed=embed, ephemeral=False)
        except Exception as e:
            print(f"Ошибка при отправке сообщения об отмене: {e}")
            await interaction.followup.send("Не удалось отправить сообщение.", ephemeral=True)

    async def log_action(self, interaction, role, action):
        """Создает embed для логирования и отправляет его в лог-канал."""
        log_channel_id = self.config["ADMIN_LOG_CHANNEL"]
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            try:
                log_embed = disnake.Embed(
                    title="Log",
                    color=disnake.Color.blue()
                )
                log_embed.add_field(name="Команда:", value=action, inline=False)
                log_embed.add_field(name="Роль:", value=role.mention, inline=False)
                log_embed.add_field(name="Канал:", value=interaction.channel.mention, inline=False)
                log_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                log_embed.set_footer(
                    text=f"Администратор: {interaction.user.display_name}", 
                    icon_url=interaction.user.display_avatar.url
                )
                log_embed.timestamp = interaction.created_at

                await log_channel.send(embed=log_embed)
                print(f"Лог отправлен: {action} для роли {role.name}")
            except Exception as e:
                print(f"Ошибка при отправке лога: {e}")
                # Если ошибка, попробуем отправить сообщение в общий канал
                await interaction.followup.send("Не удалось отправить лог в канал.", ephemeral=True)
        else:
            print(f"Канал для логирования с ID {log_channel_id} не найден.")
            # Если канал не найден, отправим сообщение в общий канал
            await interaction.followup.send("Канал для логирования не найден.", ephemeral=True)

    @commands.slash_command(name="role_add_all", description="Выдать роль всем участникам сервера")
    async def role_add_all(self, interaction: disnake.ApplicationCommandInteraction, role: disnake.Role):
        """Выдает указанную роль всем участникам на сервере"""
        
        if not any(r.id in self.config["ADMIN"] for r in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        members = [member for member in interaction.guild.members if role not in member.roles]
        count = len(members)

        cancel_button = Button(label="Отменить", style=disnake.ButtonStyle.red)
        embed = disnake.Embed(
            title="Роль выдается всем участникам!",
            description=f"Роль {role.mention} будет выдана {count} пользователям сервера. Процесс начнется немедленно.",
            color=disnake.Color.from_rgb(255, 182, 193)
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        view = View(timeout=None)
        view.add_item(cancel_button)

        try:
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            await interaction.followup.send("Не удалось отправить сообщение.", ephemeral=True)
            return

        async def cancel_button_callback(interaction):
            await self.cancel_operation(interaction, embed, "выдачи ролей")

        cancel_button.callback = cancel_button_callback

        async def add_roles_to_all():
            for member in members:
                if self.cancelled:
                    break
                await member.add_roles(role)
                await asyncio.sleep(1)

            if not self.cancelled:
                success_embed = disnake.Embed(
                    title="Роль успешно выдана всем участникам!",
                    description=f"Роль {role.mention} была выдана {count} пользователям сервера.",
                    color=disnake.Color.green()
                )
                success_embed.set_thumbnail(url=self.bot.user.avatar.url)
                success_embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

                await interaction.followup.send(embed=success_embed)
                await self.log_action(interaction, role, "role_add_all")

        self.cancelled = False
        await add_roles_to_all()

    @commands.slash_command(name="role_remove_all", description="Удалить роль у всех участников сервера")
    async def role_remove_all(self, interaction: disnake.ApplicationCommandInteraction, role: disnake.Role):
        """Удаляет указанную роль у всех участников на сервере"""
        
        if not any(r.id in self.config["ADMIN"] for r in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        members = [member for member in interaction.guild.members if role in member.roles]
        count = len(members)

        cancel_button = Button(label="Отменить", style=disnake.ButtonStyle.red)
        embed = disnake.Embed(
            title="Роль удаляется у всех участников!",
            description=f"Роль {role.mention} будет удалена у {count} пользователей. Процесс начнется немедленно.",
            color=disnake.Color.from_rgb(255, 182, 193)
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        view = View(timeout=None)
        view.add_item(cancel_button)

        try:
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            await interaction.followup.send("Не удалось отправить сообщение.", ephemeral=True)
            return

        async def cancel_button_callback(interaction):
            await self.cancel_operation(interaction, embed, "удаления ролей")

        cancel_button.callback = cancel_button_callback

        async def remove_roles_from_all():
            for member in members:
                if self.cancelled:
                    break
                await member.remove_roles(role)
                await asyncio.sleep(1)

            if not self.cancelled:
                success_embed = disnake.Embed(
                    title="Роль успешно удалена у всех участников!",
                    description=f"Роль {role.mention} была удалена у {count} пользователей.",
                    color=disnake.Color.green()
                )
                success_embed.set_thumbnail(url=self.bot.user.avatar.url)
                success_embed.set_footer(text=f"Администратор: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

                await interaction.followup.send(embed=success_embed)
                await self.log_action(interaction, role, "role_remove_all")

        self.cancelled = False
        await remove_roles_from_all()

    @commands.Cog.listener()
    async def on_ready(self):
        self.cancelled = False

def setup(bot):
    bot.add_cog(ServerRoleManagement(bot))
