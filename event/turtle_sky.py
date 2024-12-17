import disnake
from disnake.ext import commands, tasks
from datetime import datetime, time, timedelta
import logging
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class TurtleEvent(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Загружаем ID канала и роли из JSON файла
        self.config = self.load_config()
        self.channel_id = self.config["channel_id"]
        self.role_id = self.config["role_id"]
        self.image_url = "https://i.pinimg.com/736x/5b/4f/af/5b4faf4e54af4df1c1f636ebe1c9cf03.jpg"  # Ссылка на изображение
        self.event_schedule = self.get_event_schedule()  # Получение расписания
        self.last_event_time = None  # Отслеживание последнего времени события

        self.check_event.start()  # Запуск проверки событий

    def load_config(self):
        """Загружает конфигурацию из JSON файла."""
        config_path = os.path.join("data", "event_sky.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Файл конфигурации {config_path} не найден")
            return {"channel_id": 0, "role_id": 0}
        except json.JSONDecodeError:
            logging.error(f"Ошибка при чтении файла конфигурации {config_path}")
            return {"channel_id": 0, "role_id": 0}

    def get_event_schedule(self):
        """Расписание событий (московское время)."""
        summer_time = [
            time(10, 45), time(12, 45), time(14, 45), time(16, 45), time(18, 45),
            time(20, 45), time(22, 45), time(0, 45), time(2, 45), time(4, 45),
            time(6, 45), time(8, 45)
        ]
        winter_time = [
            time(11, 45), time(13, 45), time(15, 45), time(17, 45), time(19, 45),
            time(21, 45), time(23, 45), time(1, 45), time(3, 45), time(5, 45),
            time(7, 45), time(9, 45)
        ]

        # Определяем, какое сейчас время года
        now = datetime.now()
        if (3, 15) <= (now.month, now.day) <= (11, 15):  # Летнее время
            return summer_time
        else:  # Зимнее время
            return winter_time

    @tasks.loop(seconds=30)  # Проверяем каждые 30 секунд
    async def check_event(self):
        """Проверяет, совпадает ли текущее время с расписанием событий."""
        now = datetime.now()  # Местное время
        current_time = now.time().replace(second=0, microsecond=0)

        # Если событие уже отправлено для этого времени, пропускаем итерацию
        if self.last_event_time == current_time:
            return

        if current_time in self.event_schedule:
            # Обновляем последнее время
            self.last_event_time = current_time

            # Получаем канал для отправки сообщения
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                role_ping = f"<@&{self.role_id}>"

                # Вычисляем время начала события (реальное)
                event_start = datetime.combine(now.date(), current_time)

                # Добавляем 5 минут для отображения времени начала активности в эмбедде
                event_start_plus_5 = event_start + timedelta(minutes=5)

                embed = disnake.Embed(
                    title="⁣ 🐢 **Событие с черепахой скоро начнется!**",
                    description="Вас ждет сбор диковинных ракушек в закатных лучах Островов укрытия. Торопитесь, чтобы получить как можно больше воска!",
                    color=disnake.Color.from_rgb(255, 182, 193)
                )
                embed.add_field(
                    name="📅 Начало активности",
                    value=f"{event_start_plus_5.strftime('%H:%M')}",  # Показываем время на 5 минут позже
                    inline=False
                )
                embed.add_field(
                    name="⏳ Длительность активности",
                    value="10 минут",
                    inline=False
                )
                embed.set_image(url=self.image_url)
                embed.set_footer(text=f"Sky CotL")

                # Отправляем сообщение с пингом роли и embed'ом
                await channel.send(content=role_ping, embed=embed)

    @check_event.before_loop
    async def before_check_event(self):
        """Ждем, пока бот не будет готов перед запуском цикла."""
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(TurtleEvent(bot))
