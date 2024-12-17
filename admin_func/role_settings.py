import disnake
from disnake.ext import commands
from disnake import Color
import json # Для работы с JSON файлом


class ServerRoleSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    async def log_action(self, interaction, role, action):
        """Создает embed для логирования и отправляет его в лог-канал."""
        log_channel_id = self.config["ADMIN_LOG_CHANNEL"]
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            try:
                log_embed = disnake.Embed(
                    title="Лог создания роли",
                    color=disnake.Color.blue()
                )
                log_embed.add_field(name="Команда:", value=action["command"], inline=False)
                log_embed.add_field(name="Роль:", value=f"**{role.name}**", inline=False)
                log_embed.add_field(name="Цвет:", value=action["color"], inline=False)
                log_embed.add_field(name="Позиция:", value=action["position"], inline=False)
                log_embed.set_footer(
                    text=f"Администратор: {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url
                )
                log_embed.timestamp = interaction.created_at

                await log_channel.send(embed=log_embed)
                print(f"Лог отправлен: {action['command']} для роли {role.name}")
            except Exception as e:
                print(f"Ошибка при отправке лога: {e}")
                await interaction.followup.send("Не удалось отправить лог в канал.", ephemeral=True)
        else:
            print(f"Канал для логирования с ID {log_channel_id} не найден.")
            await interaction.followup.send("Канал для логирования не найден.", ephemeral=True)

    @commands.slash_command(name="role_create")
    async def role_create(
        self, 
        ctx: disnake.ApplicationCommandInteraction, 
        name: str, 
        position: int, 
        color: str = None
    ):
        """
        Создать роль на сервере.
        """
        # Проверка прав доступа
        if not any(role.id in self.config["ADMIN"] for role in ctx.author.roles):
            await ctx.send(
                embed=disnake.Embed(
                    description="❌ У вас недостаточно прав для выполнения этой команды.",
                    color=disnake.Color.red()
                ),
                ephemeral=True
            )
            return

        # Обработка цвета
        try:
            role_color = disnake.Color(int(color.lstrip("#"), 16)) if color else disnake.Color.from_rgb(255, 182, 193)
        except ValueError:
            await ctx.send(
                embed=disnake.Embed(
                    description="❌ Неверный формат цвета. Используйте HEX-код, например: `#FF5733`.",
                    color=disnake.Color.red()
                ),
                ephemeral=True
            )
            return

        # Создание роли
        try:
            guild = ctx.guild
            new_role = await guild.create_role(name=name, color=role_color)

            # Перемещение роли на нужную позицию
            await new_role.edit(position=position)

            # Ответ пользователю
            embed = disnake.Embed(
                title="Роль создана",
                description=f"✅ Роль **{name}** успешно создана.",
                color=role_color
            )
            embed.add_field(name="Позиция", value=f"{position}")
            embed.add_field(name="Цвет", value=color if color else "Нежно-розовый")

            await ctx.send(embed=embed)

            # Логируем создание роли
            action = {
                "command": "role_create",
                "color": color if color else "Нежно-розовый",
                "position": position
            }
            await self.log_action(ctx, new_role, action)

        except Exception as e:
            await ctx.send(
                embed=disnake.Embed(
                    description=f"❌ Произошла ошибка при создании роли: {str(e)}",
                    color=disnake.Color.red()
                ),
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(ServerRoleSettings(bot))
