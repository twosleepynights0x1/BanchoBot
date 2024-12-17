import disnake
from disnake.ext import commands
from disnake.ui import Button, View
from disnake import Interaction
import json
import os


class SelfRolePings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.admin_roles = self.config.get("ADMIN", [])

    def load_config(self):
        """Загружает конфигурацию из JSON файла."""
        config_path = os.path.join("conf", "config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл конфигурации {config_path} не найден")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка при чтении файла конфигурации {config_path}")
            return {}

    async def send_embeds(self, channel: disnake.TextChannel):
        """Отправляет Embed'ы с ролями новостей и событий для пинга."""

        # Первый эмбед (Роли для пинга новостей)
        news_embed = disnake.Embed(
            title="📰 Роли для пинга новостей",
            description=(
                "__Вы можете подписаться на новости по этим играм и получать уведомления, связанные с ними:__\n\n"
                "<@&1311089355686805514> – пинг по новостям Sky: Children of Light\n\n"
                "<@&1311189352533065808> – пинг по новостям Honkai: Star Rail\n\n"
                "<@&1311189464730832977> – пинг по новостям Genshin Impact"
            ),
            color=disnake.Color.blue()
        )

        # Второй эмбед (Роли для пинга событий в игре)
        event_embed = disnake.Embed(
            title="🎮 Роли для пинга событий в игре",
            description=(
                "__Получайте уведомления о событиях в игре Sky: Children of Light с этой ролью:__\n\n"
                "<@&1311189081467916399> – пинг по событиям в игре Sky"
            ),
            color=disnake.Color.green()
        )

        # Создание кнопок для первого эмбеда (новости)
        news_button_view = View()
        news_button_view.add_item(Button(label="Sky Новости", custom_id="self_roles_role_sky_news", style=disnake.ButtonStyle.primary))
        news_button_view.add_item(Button(label="Honkai Новости", custom_id="self_roles_role_honkai_news", style=disnake.ButtonStyle.primary))
        news_button_view.add_item(Button(label="Genshin Impact Новости", custom_id="self_roles_role_genshin_news", style=disnake.ButtonStyle.primary))
        news_button_view.add_item(Button(label="Сбросить роли", custom_id="self_roles_reset_news_roles", style=disnake.ButtonStyle.danger))

        # Создание кнопок для второго эмбеда (события)
        event_button_view = View()
        event_button_view.add_item(Button(label="Sky События", custom_id="self_roles_role_sky_events", style=disnake.ButtonStyle.primary))
        event_button_view.add_item(Button(label="Сбросить роли", custom_id="self_roles_reset_event_roles", style=disnake.ButtonStyle.danger))

        # Отправка Embed'ов с ролями
        await channel.send(embed=news_embed, view=news_button_view)
        await channel.send(embed=event_embed, view=event_button_view)

    @commands.slash_command(name="server_role_pings", description="Выберите роли для получения пингов.")
    async def server_role_pings(self, inter: disnake.CommandInteraction, channel: disnake.TextChannel = None):
        """Команда для выбора ролей для пинга новостей и событий."""
        await inter.response.defer()

        user_roles = [role.id for role in inter.user.roles]

        if not any(role_id in user_roles for role_id in self.admin_roles):
            await inter.send("У вас нет прав для использования этой команды.", ephemeral=True)
            return

        if not channel:
            channel = inter.channel

        await self.send_embeds(channel)

    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        """Обработчик нажатия кнопок для добавления ролей и сброса ролей."""
        if not interaction.data['custom_id'].startswith("self_roles_"):
            return  # Игнорируем кнопки, которые не относятся к SelfRolePings

        role_mapping = {
            "self_roles_role_sky_news": 1311089355686805514,
            "self_roles_role_honkai_news": 1311189352533065808,
            "self_roles_role_genshin_news": 1311189464730832977,
            "self_roles_role_sky_events": 1311189081467916399,
        }

        custom_id = interaction.data['custom_id']
        role_id = role_mapping.get(custom_id)

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"Вам была выдана роль {role.name}!", ephemeral=True)
            else:
                await interaction.response.send_message("Произошла ошибка при добавлении роли.", ephemeral=True)
            return

        if custom_id == "self_roles_reset_news_roles":
            news_roles = [1311089355686805514, 1311189352533065808, 1311189464730832977]
            roles_to_remove = [role for role in interaction.user.roles if role.id in news_roles]

            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Все новости роли были сброшены!", ephemeral=True)
            else:
                await interaction.response.send_message("У вас нет ролей для новостей для сброса.", ephemeral=True)

        elif custom_id == "self_roles_reset_event_roles":
            event_roles = [1311189081467916399]
            roles_to_remove = [role for role in interaction.user.roles if role.id in event_roles]

            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Все события роли были сброшены!", ephemeral=True)
            else:
                await interaction.response.send_message("У вас нет ролей для событий для сброса.", ephemeral=True)


def setup(bot):
    bot.add_cog(SelfRolePings(bot))
