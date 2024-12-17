import disnake
from disnake.ext import commands
import random

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="roll", description="Бросить кубик и получить результат")
    async def roll(self, inter: disnake.ApplicationCommandInteraction):
        """Бросает виртуальный кубик и выводит результат."""
        roll_result = random.randint(1, 6)  # Кубик имеет 6 граней
        embed = disnake.Embed(
            title="Результат броска кубика!",
            description=f"Вам выпало число: **{roll_result}**",
            color=disnake.Color.blue()
        )
        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Roll(bot))
