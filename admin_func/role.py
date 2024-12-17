import disnake
from disnake.ext import commands
import json

# Загружаем конфигурацию из JSON файла
with open('conf/config.json', 'r') as f:
    config = json.load(f)

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, interaction, member, role, action):
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
                log_embed.add_field(name="Пользователь:", value=member.mention, inline=False)
                log_embed.add_field(name="Роль:", value=role.mention, inline=False)
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

    @commands.slash_command(name="role_add", description="Добавить роль выбранному участнику")
    async def role_add(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        member: disnake.Member, 
        role: disnake.Role
    ):
        """Добавляет роль участнику и отправляет embed с подтверждением"""
        
        # Проверка, что у пользователя есть нужная роль
        admin_roles = config.get('ADMIN', [])
        if not any(r.id in admin_roles for r in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Проверка, что у участника уже нет этой роли
        if role in member.roles:
            await interaction.response.send_message("Этот участник уже имеет эту роль.", ephemeral=True)
            return
        
        # Добавляем роль участнику
        await member.add_roles(role)

        # Создаем embed для подтверждения
        embed = disnake.Embed(
            title="Роль успешно добавлена",
            description=f'Роль {role.mention} была успешно добавлена участнику {member.mention}.',
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
            "command": "role_add",  # Строка с командой
            "role_name": role.name,       # Имя роли
        }
        await self.log_action(interaction, member, role, action)  # Логируем добавление роли

    @commands.slash_command(name="role_remove", description="Удалить роль у выбранного участника")
    async def role_remove(
        self, 
        interaction: disnake.ApplicationCommandInteraction, 
        member: disnake.Member, 
        role: disnake.Role
    ):
        """Удаляет роль у участника и отправляет embed с подтверждением"""
        
        # Проверка, что у пользователя есть нужная роль
        admin_roles = config.get('ADMIN', [])
        if not any(r.id in admin_roles for r in interaction.author.roles):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Проверка, что у участника есть эта роль
        if role not in member.roles:
            await interaction.response.send_message("У участника нет этой роли.", ephemeral=True)
            return
        
        # Удаляем роль у участника
        await member.remove_roles(role)

        # Создаем embed для подтверждения
        embed = disnake.Embed(
            title="Роль успешно удалена",
            description=f'Роль {role.mention} была успешно удалена у участника {member.mention}.',
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
            "command": "role_remove",  # Строка с командой
            "role_name": role.name,          # Имя роли
        }
        await self.log_action(interaction, member, role, action)  # Логируем удаление роли

def setup(bot):
    bot.add_cog(RoleManagement(bot))
