import disnake
from disnake.ext import commands
import json

class ServerInviteLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('conf/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    async def get_invite_data(self):
        invite_data = {}

        for invite in await self.bot.guilds[0].invites():
            inviter_id = str(invite.inviter.id)
            if invite.uses > 0:
                if inviter_id not in invite_data:
                    invite_data[inviter_id] = 0
                invite_data[inviter_id] += invite.uses

        sorted_invite_data = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_invite_data

    @commands.slash_command(description="Показать топ участников по количеству приглашений.")
    async def invite_leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()  # Отправляем defer, чтобы избежать тайм-аута

        invite_data = await self.get_invite_data()

        if not invite_data:
            await inter.edit_original_message(content="На сервере пока нет данных о приглашениях.")
            return

        embed = disnake.Embed(
            title="🏆 Топ участников по приглашениям",
            description="Топ участников, пригласивших больше всего людей на сервер!",
            color=disnake.Color.gold()
        )
        embed.set_image(url=self.config["INVITE_IMAGE"])
        
        # Добавляем аватарку сервера в footer
        server_icon = inter.guild.icon.url if inter.guild.icon else None
        embed.set_footer(text="Спасибо за вклад в рост нашего сообщества!", icon_url=server_icon)

        for index, (user_id, invite_count) in enumerate(invite_data[:10], start=1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{index}. {user.display_name} 🎉",
                value=f"Приглашений: {invite_count} ",
                inline=False
            )

        await inter.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(ServerInviteLeaderboard(bot))
