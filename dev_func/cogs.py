import disnake
from disnake.ext import commands
from pathlib import Path
import json

# Загрузка конфигурации
with open('conf/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
#1

class DevCogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _handle_cog(self, inter: disnake.ApplicationCommandInteraction, action: str, cog: str):
        # Проверка ролей пользователя
        if not any(role.id in config["ADMIN"] for role in inter.author.roles):
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="🚫 Недостаточно прав",
                    description="У вас недостаточно прав для выполнения этой команды. "
                                "Команда доступна только администраторам.",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
            return

        # Директории для поиска когов
        directories = [
            "admin_func",
            "dev_func",
            "event",
            "news",
            "server_func",
            "user_func",
        ]

        cog_path = None
        # Поиск когов по директориям
        for directory in directories:
            potential_path = f"{directory}.{cog}"
            if action != "load" and potential_path in self.bot.extensions:
                cog_path = potential_path
                break
            elif action == "load" and Path(f"{directory}/{cog}.py").exists():
                cog_path = potential_path
                break

        # Если ког не найден
        if cog_path is None:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="❌ Ког не найден",
                    description=f"Ког **{cog}** не найден в указанных директориях:\n\n"
                                + "\n".join(f"`{d}`" for d in directories),
                    color=disnake.Color.red(),
                )
            )
            return

        # Выполнение действия (загрузка, выгрузка, перезагрузка)
        try:
            if action == "load":
                self.bot.load_extension(cog_path)
                result = f"Ког **`{cog_path}`** успешно загружен."
                color = disnake.Color.green()
                icon = "✅"
            elif action == "unload":
                self.bot.unload_extension(cog_path)
                result = f"Ког **`{cog_path}`** успешно выгружен."
                color = disnake.Color.orange()
                icon = "🟧"
            elif action == "reload":
                self.bot.reload_extension(cog_path)
                result = f"Ког **`{cog_path}`** успешно перезагружен."
                color = disnake.Color.blurple()
                icon = "🔄"
        except Exception as e:
            result = f"Произошла ошибка при выполнении операции с когом **`{cog_path}`**:\n```{e}```"
            color = disnake.Color.red()
            icon = "❌"

        # Отправка результата
        embed = disnake.Embed(
            title=f"{icon} Результат команды: {action.capitalize()} Cog",
            description=result,
            color=color,
        )
        embed.add_field(name="Действие", value=f"`{action.capitalize()}`", inline=True)
        embed.add_field(name="Название кoга", value=f"`{cog}`", inline=True)
        if action == "load":
            embed.add_field(name="Статус", value="Ког успешно загружен в систему.", inline=False)
        elif action == "unload":
            embed.add_field(name="Статус", value="Ког был успешно выгружен из системы.", inline=False)
        elif action == "reload":
            embed.add_field(name="Статус", value="Ког был успешно перезагружен.", inline=False)
        else:
            embed.add_field(name="Статус", value="Операция завершена.", inline=False)

        embed.set_footer(text=f"Выполнено: {inter.author}", icon_url=inter.author.display_avatar.url)

        await inter.response.send_message(embed=embed)

    @commands.slash_command()
    async def core(
        self,
        inter: disnake.ApplicationCommandInteraction,
        action: str = commands.Param(choices=["load", "unload", "reload"]),
        cog: str = commands.Param(description="Название ког файла (без .py)"),
    ):
        """
        Управление когами (загрузка, выгрузка, перезагрузка).
        Только для администраторов.
        """
        await self._handle_cog(inter, action, cog)


def setup(bot):
    bot.add_cog(DevCogManager(bot))
