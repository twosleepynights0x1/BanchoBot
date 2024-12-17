import disnake
from disnake.ext import commands
import json
from pathlib import Path


class LevelLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = Path("data/member_level.json")

    def load_level_data(self):
        if self.data_file.exists():
            with open(self.data_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def generate_leaderboard_page(self, sorted_members, ctx, page=1, per_page=10):
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        filtered_members = [
            (member_id, stats)
            for member_id, stats in sorted_members
            if ctx.guild.get_member(int(member_id)) is not None
        ]

        leaderboard_text = ""
        for index, (member_id, stats) in enumerate(filtered_members[start_index:end_index], start=start_index + 1):
            member = ctx.guild.get_member(int(member_id))
            member_tag = member.mention
            leaderboard_text += f"**{index}. {member_tag}** Уровень: {stats['level']}\n"

        return leaderboard_text if leaderboard_text else "Нет данных для отображения."

    @commands.slash_command()
    async def level_leaderboard(self, ctx: disnake.ApplicationCommandInteraction):
        level_data = self.load_level_data()
        sorted_members = sorted(level_data.items(), key=lambda item: item[1].get("level", 0), reverse=True)

        if not sorted_members:
            await ctx.send(embed=disnake.Embed(description="❌ Нет данных для отображения.", color=disnake.Color.red()), ephemeral=True)
            return

        page = 1
        embed = disnake.Embed(
            title="📋 Таблица лидеров по уровням",
            description=self.generate_leaderboard_page(sorted_members, ctx, page),
            color=disnake.Color.gold()
        )
        embed.set_footer(text=f"Страница {page}/{(len(sorted_members) - 1) // 10 + 1}")

        # Создаем действия для кнопок
        buttons = disnake.ui.ActionRow(
            disnake.ui.Button(label="⬅", style=disnake.ButtonStyle.primary, custom_id="leaderboard_prev_page"),
            disnake.ui.Button(label="⏸", style=disnake.ButtonStyle.secondary, custom_id="leaderboard_stop"),
            disnake.ui.Button(label="➡", style=disnake.ButtonStyle.primary, custom_id="leaderboard_next_page")
        )

        # Создаем View, который будет управлять кнопками в пределах этого конкретного сообщения
        view = LevelLeaderboardView(sorted_members, ctx, embed, page)

        message = await ctx.send(embed=embed, view=view)  # Используем только view, без components


class LevelLeaderboardView(disnake.ui.View):
    def __init__(self, sorted_members, ctx, embed, page):
        super().__init__(timeout=180.0)
        self.sorted_members = sorted_members
        self.ctx = ctx
        self.embed = embed
        self.page = page

    @disnake.ui.button(label="⬅", style=disnake.ButtonStyle.primary, custom_id="leaderboard_prev_page")
    async def prev_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author != self.ctx.author:
            await inter.response.send_message("Вы не можете управлять этой таблицей!", ephemeral=True)
            return
        self.page = max(1, self.page - 1)
        self.embed.description = self.generate_leaderboard_page(self.sorted_members, self.ctx, self.page)
        self.embed.set_footer(text=f"Страница {self.page}/{(len(self.sorted_members) - 1) // 10 + 1}")
        await inter.response.edit_message(embed=self.embed, view=self)

    @disnake.ui.button(label="⏸", style=disnake.ButtonStyle.secondary, custom_id="leaderboard_stop")
    async def stop(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author != self.ctx.author:
            await inter.response.send_message("Вы не можете управлять этой таблицей!", ephemeral=True)
            return
        await inter.response.defer()

    @disnake.ui.button(label="➡", style=disnake.ButtonStyle.primary, custom_id="leaderboard_next_page")
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author != self.ctx.author:
            await inter.response.send_message("Вы не можете управлять этой таблицей!", ephemeral=True)
            return
        self.page = min((len(self.sorted_members) - 1) // 10 + 1, self.page + 1)
        self.embed.description = self.generate_leaderboard_page(self.sorted_members, self.ctx, self.page)
        self.embed.set_footer(text=f"Страница {self.page}/{(len(self.sorted_members) - 1) // 10 + 1}")
        await inter.response.edit_message(embed=self.embed, view=self)

    def generate_leaderboard_page(self, sorted_members, ctx, page=1, per_page=10):
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        filtered_members = [
            (member_id, stats)
            for member_id, stats in sorted_members
            if ctx.guild.get_member(int(member_id)) is not None
        ]

        leaderboard_text = ""
        for index, (member_id, stats) in enumerate(filtered_members[start_index:end_index], start=start_index + 1):
            member = ctx.guild.get_member(int(member_id))
            member_tag = member.mention
            leaderboard_text += f"**{index}. {member_tag}** Уровень: {stats['level']}\n"

        return leaderboard_text if leaderboard_text else "Нет данных для отображения."


def setup(bot):
    bot.add_cog(LevelLeaderboard(bot))
