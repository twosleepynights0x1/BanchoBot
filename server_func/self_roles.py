import disnake
from disnake.ext import commands
from disnake.ui import Button, View
from disnake import Interaction
import json

with open('conf/config.json') as f:
    config = json.load(f)

class SelfRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embeds(self, channel: disnake.TextChannel):
        """Отправляет Embed'ы с кнопками в канал."""
        embeds = [
            disnake.Embed(
                title="🎭 Роли Сервера",
                description="🎭 Здесь вы можете ознакомиться с основными ролями, которые существуют на нашем сервере, а также получить некоторые из них 🎭",
                color=disnake.Color.blurple()
            ),
            disnake.Embed(
                title="💎 Административные Роли 💎",
                description=( 
                    "__Люди с этими ролями – представители администрации, следящие за порядком на сервере и занимающиеся его поддержкой и развитием:__\n\n"
                    "<@&1294045225873833999> – глобальные администраторы на разных проектах, имеют полномочия на уровне владельца сервера\n\n"
                    "<@&1294045970975428628> – главы сервера, которые имеют полный доступ ко всем настройкам\n\n"
                    "<@&784160890761117767> – правая рука и личные помощники глав сервера\n\n"
                    "<@&1025668964447158322> – админы сервера, которые решают различные вопросы и организуют ивенты\n\n"
                    "<@&1253683368135233577> – стражи порядка, все видят и всех накажут по заслугам"
                ),
                color=disnake.Color.gold()
            ),
            disnake.Embed(
                title="✨ Роли Персонала ✨",
                description=( 
                    "__Люди с этими ролями – управляющие игровыми категориями и ответственные за ведение новостных каналов:__\n\n"
                    "<@&1105831610391216168> – владелец и руководитель категории <#784172182145466369>\n\n"
                    "<@&1105831009808822374> – владелец и руководитель категории <#810212950932586527>\n\n"
                    "<@&1142091411655770234> – владелец и руководитель категории <#1142092089098764358>"
                ),
                color=disnake.Color.green()
            ),
            disnake.Embed(
                title="🎮 Игровые Роли 🎮",
                description=( 
                    "__На нашем сервере существуют специальные категории для различных игр, где вы можете общаться по внутриигровым вопросам и заводить друзей:__\n\n"
                    "<@&791556122128678934> – категория по игре Sky: Children of Light\n\n"
                    "<@&810915472664690689> – категория по игре Genshin Impact\n\n"
                    "<@&1142091192222359573> – категория по игре Honkai: Star Rail"
                ),
                color=disnake.Color.blue()
            ),
            disnake.Embed(
                title="👥 Гендерные Роли 👥",
                description=( 
                    "__При желании вы можете указать свой пол, выбрав подходящую роль:__\n\n"
                    "<@&866427253490450492> – парень\n\n"
                    "<@&866426767639183411> – девушка"
                ),
                color=disnake.Color.purple()
            ),
            disnake.Embed(
                title="🌸 Роли за Уровень 🌸",
                description=( 
                    "Общаясь и взаимодействуя на нашем сервере, вы можете копить опыт активности и повышать свой **уровень**\n"
                    "За достижение определенного уровня вам автоматически будет выдаваться роль:\n\n"
                    "<@&784159073385840651> – 5 уровень\n\n"
                    "<@&1091074897473720501> – 15 уровень\n\n"
                    "<@&1091078506986885212> – 25 уровень\n\n"
                    "<@&1091079383210541066> – 35 уровень\n\n"
                    "<@&1091079976025075852> – 45 уровень\n\n"
                    "<@&1091080623478812724> – 55 уровень\n\n"
                    "> Проверить текущий уровень можно командой **«/level»**"
                ),
                color=disnake.Color.orange()
            ),
            disnake.Embed(
                title="⚡️ Особые Роли ⚡️",
                description=( 
                    "__На нашем сервере также есть ряд эксклюзивных ролей, которые можно получить за различные действия или напрямую от администрации:__\n\n"
                    "<@&798286377757704212> – человек с доступом к бета-версиям игр, актуальных на сервере\n"
                    "`Способ получения: связаться с администрацией через #⭐┋𝚂𝚞𝚙𝚙𝚘𝚛𝚝 и предоставить запрашиваемые доказательства`\n\n"
                    "<@&1266081292181835846> – друг сервера, оказывающий различную поддержку его развитию\n"
                    "`Способ получения: выдается на усмотрение администрации`\n\n"
                    "<@&850536622062698527> – человек, оказавший личную материальную поддержку Бандикуту\n\n"
                    "<@&854234816303595532> – человек, забустивший сервер\n\n"
                    "<@&1261858451366346862> – роль, которая предоставляет доступ к различным плюшкам и дополнительным функциям\n"
                    "`Способ получения: покупка за серверную валюту у Akemi в канале` <#832814956499828766>\n\n"
                    "<@&796308168719728651>  – роль для нарушителей, получивших мут по каким-либо причинам\n"
                    "`Бонус: открывает доступ к каналу <#1272281772092166214>, где можно выплеснуть эмоции или оспорить свое наказание`<:interesting:873242359482171422>"
                ),
                color=disnake.Color.red()
            ),
            disnake.Embed(
                title="⚠️ Дополнительные Роли ⚠️",
                description=( 
                    "> Помимо вышеперечисленных ролей на нашем сервере присутствуют и другие\n"
                    "⚠️ Если интересующей вас роли нет в списке, значит она может быть __архивной__ и/или ее получение на данный момент **невозможно**\n\n"
                    "Если у вас возникли вопросы по получению какой-либо роли, свяжитесь с нами в <#1253754782359752865>"
                ),
                color=disnake.Color.dark_gray()
            )
        ]

        # Создание кнопок для ролей
        game_button_view = View()
        game_button_view.add_item(Button(label="Sky: Children of Light", custom_id="role_sky", style=disnake.ButtonStyle.success))
        game_button_view.add_item(Button(label="Genshin Impact", custom_id="role_genshin", style=disnake.ButtonStyle.success))
        game_button_view.add_item(Button(label="Honkai: Star Rail", custom_id="role_honkai", style=disnake.ButtonStyle.success))
        game_button_view.add_item(Button(label="Сбросить игровые роли", custom_id="reset_game_roles", style=disnake.ButtonStyle.danger))

        gender_button_view = View()
        gender_button_view.add_item(Button(label="Парень", custom_id="role_male", style=disnake.ButtonStyle.primary))
        gender_button_view.add_item(Button(label="Девушка", custom_id="role_female", style=disnake.ButtonStyle.primary))
        gender_button_view.add_item(Button(label="Сбросить гендерную роль", custom_id="reset_gender_role", style=disnake.ButtonStyle.danger))

        # Кнопка сброса ролей
        reset_button_view = View()
        reset_button_view.add_item(Button(label="Сбросить роли", custom_id="reset_roles", style=disnake.ButtonStyle.danger))

        # Отправка Embed'ов
        for index, embed in enumerate(embeds):
            if index == 3:  # Роли игр (4-й Embed)
                await channel.send(embed=embed, view=game_button_view)
            elif index == 4:  # Гендерные роли (5-й Embed)
                await channel.send(embed=embed, view=gender_button_view)
            else:
                await channel.send(embed=embed)

    @commands.slash_command(name="server_role_welcome", description="Отправляет сообщения с ролями для приветствия на сервере.")
    async def server_role_welcome(self, inter: disnake.CommandInteraction, channel: disnake.TextChannel = None):
        """Команда для администраторов для отправки сообщений с ролями."""
        # Деферим ответ, чтобы избежать тайм-аута
        await inter.response.defer()
        # Проверка прав администратора
        user_roles = [role.id for role in inter.user.roles]
        allowed_roles = config["ADMIN"]

        if not any(role_id in user_roles for role_id in allowed_roles):
            await inter.send("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        
        # Если канал не указан, используем канал, в котором была вызвана команда
        if not channel:
            channel = inter.channel

        # Отправка Embed'ов с ролями
        await self.send_embeds(channel)

    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        """Обработчик нажатия кнопок для добавления ролей и сброса ролей."""
        role_mapping = {
            "role_sky": 791556122128678934,  # Sky роль
            "role_genshin": 810915472664690689,  # Genshin роль
            "role_honkai": 1142091192222359573,  # Honkai роль
            "role_male": 866427253490450492,  # Мужчина роль
            "role_female": 866426767639183411,  # Женщина роль
        }

        role_id = role_mapping.get(interaction.data['custom_id'])

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"Вам была выдана роль {role.name}!", ephemeral=True)
            else:
                await interaction.response.send_message("Произошла ошибка при добавлении роли.", ephemeral=True)

        # Сброс игровых ролей
        if interaction.data['custom_id'] == "reset_game_roles":
            game_roles = [791556122128678934, 810915472664690689, 1142091192222359573]
            roles_to_remove = [role for role in interaction.user.roles if role.id in game_roles]
            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Все игровые роли были сброшены!", ephemeral=True)
            else:
                await interaction.response.send_message("У вас нет игровых ролей для сброса.", ephemeral=True)

        # Сброс гендерной роли
        if interaction.data['custom_id'] == "reset_gender_role":
            gender_roles = [866427253490450492, 866426767639183411]
            roles_to_remove = [role for role in interaction.user.roles if role.id in gender_roles]
            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Ваша гендерная роль была сброшена!", ephemeral=True)
            else:
                await interaction.response.send_message("У вас нет гендерной роли для сброса.", ephemeral=True)

        # Сброс всех ролей
        if interaction.data['custom_id'] == "reset_roles":
            for role in interaction.user.roles:
                if role.id in role_mapping.values():
                    await interaction.user.remove_roles(role)
            await interaction.response.send_message("Все роли сброшены!", ephemeral=True)

def setup(bot):
    bot.add_cog(SelfRole(bot))
