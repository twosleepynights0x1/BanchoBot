import disnake
from disnake.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="server_info", description="Получить информацию о сервере")
    async def server_info(self, interaction: disnake.ApplicationCommandInteraction):
        """Отправляет embed с полной информацией о сервере."""

        # Получаем информацию о сервере
        guild = interaction.guild

        # Создаем Embed с красивыми эмодзи и настройками
        embed = disnake.Embed(
            title=f"Сервер {guild.name}",
            description=f"🌟 **Краткая информация ^_^** 🌟",
            color=disnake.Color.blurple()
        )

        # Добавляем поля с информацией о сервере
        embed.add_field(name="📅 Дата создания:", value=guild.created_at.strftime('%d %B %Y, %H:%M:%S'))
        embed.add_field(name="👥 Количество участников:", value=guild.member_count)
        embed.add_field(name="💬 Количество каналов:", value=len(guild.text_channels) + len(guild.voice_channels))
        embed.add_field(name="🤖 Количество ботов:", value=len([member for member in guild.members if member.bot]))
        embed.add_field(name="🌐 Локаль сервера:", value=guild.preferred_locale)
        embed.add_field(name="🎨 Роли на сервере:", value=len(guild.roles))
        
        # Добавляем ссылку на серверный аватар и добавляем его справа сверху
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправляем сообщение с Embed
        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(ServerInfo(bot))
