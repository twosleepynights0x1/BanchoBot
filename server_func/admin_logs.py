import disnake
from disnake import Embed
from disnake.ext import commands
import json

class RoleAndMessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("conf/config.json", "r") as f:
            config = json.load(f)
        self.log_channel_id = config["ADMIN_LOG_CHANNEL"]

    async def send_log(self, embed: Embed):
        """Отправка логов в указанный канал."""
        if self.log_channel_id:
            channel = self.bot.get_channel(self.log_channel_id)
            if channel:
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        """Логирование событий редактирования сообщений."""
        if before.author.bot or before.content == after.content:
            return  # Игнорируем ботов или если текст не изменился

        embed = Embed(
            title="📝 Сообщение отредактировано",
            color=disnake.Color.orange(),
            timestamp=disnake.utils.utcnow()
        )
        embed.set_thumbnail(url=before.author.avatar.url if before.author.avatar else None)

        # Форматирование текста в Markdown-блоки
        embed.add_field(
            name="Сообщение до изменения", 
            value=f"```{before.content[:1024]}```" if before.content else "```[Пусто]```", 
            inline=False
        )
        embed.add_field(
            name="Сообщение после изменения", 
            value=f"```{after.content[:1024]}```" if after.content else "```[Пусто]```", 
            inline=False
        )
        embed.add_field(name="Автор", value=before.author.mention, inline=False)
        embed.add_field(name="Канал", value=before.channel.mention, inline=False)
        embed.add_field(
            name="Действие",
            value=f"[Перейти к сообщению](https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id})",
            inline=False
        )
        embed.set_footer(
            text=f"Редактировал: {before.author.name} • {disnake.utils.utcnow().strftime('%d.%m.%Y %H:%M')}",
            icon_url=before.author.avatar.url if before.author.avatar else None
        )
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        """Логирование изменений ролей."""
        embed = Embed(color=disnake.Color.blurple(), timestamp=disnake.utils.utcnow())
        embed.set_thumbnail(url=after.avatar.url if after.avatar else None)
        embed.set_footer(
            text=f"[Role Logs]",
            icon_url=after.avatar.url if after.avatar else None
        )

        # Проверяем изменения ролей
        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        if added_roles:
            role_names = ', '.join([role.mention for role in added_roles])
            embed.title = "✨ Роль добавлена"
            embed.add_field(name="Добавлено", value=role_names, inline=False)
        if removed_roles:
            role_names = ', '.join([role.mention for role in removed_roles])
            embed.title = "❌ Роль удалена"
            embed.add_field(name="Удалено", value=role_names, inline=False)

        # Добавляем общую информацию
        embed.add_field(name="Пользователь", value=after.mention, inline=False)

        # Отправляем лог только если есть изменения
        if added_roles or removed_roles:
            await self.send_log(embed)

def setup(bot):
    bot.add_cog(RoleAndMessageLogs(bot))
