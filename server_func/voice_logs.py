import disnake
from disnake import Embed
from disnake.ext import commands
import json

class VoiceLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.voice_log_channel_id = self.config["voice_log_channel"]

    async def send_log(self, embed: Embed):
        if self.voice_log_channel_id:
            channel = self.bot.get_channel(self.voice_log_channel_id)
            if channel:
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        embed = Embed(color=disnake.Color.blurple(), timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar.url if member.avatar else None)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)

        # Join/Leave Events
        if before.channel != after.channel:
            if before.channel is None:
                embed.title = "Пользователь присоединился к голосовому каналу"
                embed.description = (
                    f"**{member.mention}** присоединился к каналу:\n"
                    f"🔊 **{after.channel.name}** *(ID: {after.channel.id})*"
                )
                embed.color = disnake.Color.green()
            elif after.channel is None:
                embed.title = "Пользователь покинул голосовой канал"
                embed.description = (
                    f"**{member.mention}** покинул канал:\n"
                    f"🔊 **{before.channel.name}** *(ID: {before.channel.id})*"
                )
                embed.color = disnake.Color.red()
            else:
                embed.title = "Пользователь переключился между голосовыми каналами"
                embed.description = (
                    f"**{member.mention}** переключился:\n"
                    f"🔊 Из канала **{before.channel.name}** *(ID: {before.channel.id})*\n"
                    f"➡️ В канал **{after.channel.name}** *(ID: {after.channel.id})*"
                )
                embed.color = disnake.Color.orange()

        # Mute/Unmute Events
        if before.self_mute != after.self_mute:
            embed.title = "Событие: Изменение состояния микрофона"
            embed.description = (
                f"**{member.mention}** {'🔇 заглушил' if after.self_mute else '🔊 включил'} микрофон.\n"
                f"Текущий канал: **{after.channel.name if after.channel else 'Не в канале'}**"
            )
            embed.color = disnake.Color.purple()

        # Deafen/Undeafen Events
        if before.self_deaf != after.self_deaf:
            embed.title = "Событие: Изменение состояния звука"
            embed.description = (
                f"**{member.mention}** {'🔇 заглушил звук' if after.self_deaf else '🔊 включил звук'} для себя.\n"
                f"Текущий канал: **{after.channel.name if after.channel else 'Не в канале'}**"
            )
            embed.color = disnake.Color.teal()

        # Stream Events
        if before.self_stream != after.self_stream:
            embed.title = "Событие: Стриминг"
            embed.description = (
                f"**{member.mention}** {'📺 начал стримить' if after.self_stream else '📴 закончил стрим'}.\n"
                f"Текущий канал: **{after.channel.name if after.channel else 'Не в канале'}**"
            )
            embed.color = disnake.Color.gold()

        # Camera Events
        if before.self_video != after.self_video:
            embed.title = "Событие: Камера"
            embed.description = (
                f"**{member.mention}** {'📹 включил камеру' if after.self_video else '📴 выключил камеру'}.\n"
                f"Текущий канал: **{after.channel.name if after.channel else 'Не в канале'}**"
            )
            embed.color = disnake.Color.magenta()

        # Send the log if any relevant changes occurred
        if embed.description:
            embed.set_footer(
                text=f"ID пользователя: {member.id}",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            await self.send_log(embed)

def setup(bot):
    bot.add_cog(VoiceLogs(bot))
