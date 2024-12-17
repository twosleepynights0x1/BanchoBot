import disnake
from disnake.ext import commands
from pathlib import Path
import json

# Загрузка конфигурации
with open('conf/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

class DevCogShow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def core_show(self, inter: disnake.ApplicationCommandInteraction):
        """
        Показывает список всех когов и их статусы (загружен/не загружен).
        Только для администраторов.
        """
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

        # Директории для когов
        directories = [
            "admin_func",
            "dev_func",
            "event",
            "news",
            "server_func",
            "user_func",
        ]

        embed = disnake.Embed(
            title="📜 Список когов",
            description="Здесь перечислены все коги в системе, отсортированные по директориям.\n\n"
                        "✅ — Загружен | ❌ — Не загружен",
            color=disnake.Color.blurple(),
        )

        # Обработка каждой директории
        for directory in directories:
            cog_statuses = []
            # Получение списка файлов в директории
            dir_path = Path(directory)
            if not dir_path.exists():
                continue

            for file in dir_path.iterdir():
                if file.suffix == ".py" and not file.name.startswith("_"):
                    cog_name = file.stem
                    full_cog_name = f"{directory}.{cog_name}"
                    status = "✅ Load" if full_cog_name in self.bot.extensions else "❌ Unload"
                    cog_statuses.append(f"**`{cog_name}`** — {status}")

            # Добавляем информацию в Embed
            if cog_statuses:
                embed.add_field(
                    name=f"📂 {directory}",
                    value="\n".join(cog_statuses),
                    inline=False
                )

        embed.set_footer(
            text=f"Запрошено: {inter.author}",
            icon_url=inter.author.display_avatar.url
        )

        await inter.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(DevCogShow(bot))
