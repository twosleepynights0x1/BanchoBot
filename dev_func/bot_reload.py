import disnake
from disnake.ext import commands
import os
import sys
import asyncio
import logging
import json
from disnake import Embed
from datetime import datetime

# Загрузка конфигурации
with open('conf/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class DeveloperCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="core_reload", description="Перезагрузить ядро бота")
    async def core_reload(
        self, 
        interaction: disnake.ApplicationCommandInteraction
    ):
        """Перезагружает бота и отправляет embed с подтверждением"""
        
        # Проверка прав: пользователь должен быть владельцем бота
        if interaction.author.id != config["BOT_OWNER"]:
            await interaction.response.send_message(
                "У вас нет прав для использования этой команды.",
                ephemeral=True
            )
            return
        
        # Генерация embed перед перезагрузкой
        embed = Embed(
            title="🚀 Перезагрузка бота",
            description=(  # Описание перезагрузки
                "Бот будет перезагружен. Все настройки и данные будут восстановлены.\n\n"
                "✅ **Разрешения**: Бот перезагружен с полными правами на выполнение команд.\n"
                "⏱ **Время перезагрузки**: Процесс завершится через несколько секунд.\n\n"
                "Это действие было инициировано разработчиком."
            ),
            color=disnake.Color.blue()
        )
        
        embed.add_field(
            name="🔧 Дополнительная информация", 
            value=(  # Дополнительные подробности о перезагрузке
                "Перезагрузка бота может занять несколько секунд. После перезагрузки "
                "бот будет готов к выполнению команд. Все временные данные и настройки "
                "будут восстановлены без потерь."
            ),
            inline=False
        )
        
        # Устанавливаем аватарку бота справа сверху (не в поле автора)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Добавляем footer с именем и аватаром администратора
        embed.set_footer(
            text=f"Перезагружено разработчиком: {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        # Отправка embed перед перезагрузкой
        await interaction.response.send_message(embed=embed)

        # Логируем информацию о перезагрузке в консоль
        logging.info(f"Bot reload initiated by {interaction.user.display_name} ({interaction.user.id}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")

        # Ожидание перед перезагрузкой, чтобы сообщение успело отправиться
        await asyncio.sleep(2)
        
        # Перезагружаем бота
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.Cog.listener()
    async def on_ready(self):
        """Слушатель события, когда бот готов."""
        
        # Генерация embed после успешной перезагрузки
        embed = Embed(
            title="🎉 Бот успешно перезагружен",
            description="Перезагрузка завершена! Все настройки и коги были загружены.",
            color=disnake.Color.green()
        )

        embed.add_field(
            name="🔧 Статус перезагрузки",
            value="Все коги были успешно загружены и бот готов к работе.",
            inline=False
        )
        
        # Получаем список загруженных когов
        loaded_cogs = ", ".join(self.bot.cogs.keys())  # Получаем все ключи из self.bot.cogs
        embed.add_field(
            name="📚 Загруженные коги:",
            value=loaded_cogs,
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Отправка embed в канал, где администратор может увидеть успешную перезагрузку
        channel = self.bot.get_channel(config["ADMIN_LOG_CHANNEL"])
        if channel:
            await channel.send(embed=embed)

        # Логируем успешную перезагрузку
        logging.info(f"Bot successfully reloaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Loaded cogs: {', '.join(self.bot.cogs.keys())}.")

def setup(bot):
    bot.add_cog(DeveloperCommands(bot))
