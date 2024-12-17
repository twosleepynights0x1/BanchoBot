import disnake
from disnake.ext import commands
import random

class ColorPicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="color_picker", description="Генерация случайного цвета")
    async def color_picker(self, inter: disnake.ApplicationCommandInteraction):
        """Генерирует случайный цвет и отображает его."""
        random_color = random.randint(0, 0xFFFFFF)  # Генерация случайного цвета
        embed = disnake.Embed(
            title="Случайный цвет",
            description=f"Выпал цвет: #{random_color:06X}",
            color=random_color
        )
        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(ColorPicker(bot))
