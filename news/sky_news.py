import disnake
from disnake.ext import commands
from translate import Translator
import re
import html
from langdetect import detect
import json
import os

class NewsSky(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Загружаем конфигурацию из JSON файла
        self.config = self.load_config()
        self.source_channel_id = self.config["source_channel_id"]  # ID канала с новостями
        self.target_channel_id = self.config["target_channel_id"]  # ID канала для перевода 
        self.notify_role_id = self.config["notify_role_id"]  # ID роли для пинга
        self.translator = Translator(from_lang="en", to_lang="ru")  # Инициализация переводчика

    def load_config(self):
        """Загружает конфигурацию из JSON файла."""
        config_path = os.path.join("data", "sky_news.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл конфигурации {config_path} не найден")
            return {
                "source_channel_id": 0,
                "target_channel_id": 0,
                "notify_role_id": 0
            }
        except json.JSONDecodeError:
            print(f"Ошибка при чтении файла конфигурации {config_path}")
            return {
                "source_channel_id": 0,
                "target_channel_id": 0,
                "notify_role_id": 0
            }

    def preserve_time_tags(self, text):
        """Заменяет метки времени на уникальные маркеры для сохранения."""
        time_tags = re.findall(r"<t:\d+(:[a-zA-Z]+)?>", text)
        preserved_text = text
        for idx, tag in enumerate(time_tags):
            preserved_text = preserved_text.replace(tag, f"{{TIME_TAG_{idx}}}")
        return preserved_text, time_tags

    def restore_time_tags(self, text, time_tags):
        """Восстанавливает метки времени в исходных местах текста."""
        for idx, tag in enumerate(time_tags):
            text = text.replace(f"{{TIME_TAG_{idx}}}", tag)
        return text

    def clean_message(self, text):
        """Удаляет серверные эмодзи и стикеры из текста, оставляя стандартные эмодзи."""
        text = re.sub(r"<a?:\w+:\d+>", "", text)
        text = re.sub(r":\w+:", "", text)
        return text.strip()

    def split_text(self, text, max_length=500):
        """Разделение текста на части, чтобы каждая была не длиннее max_length."""
        parts = []
        while len(text) > max_length:
            split_index = text.rfind(" ", 0, max_length)
            if split_index == -1:
                split_index = max_length
            parts.append(text[:split_index])
            text = text[split_index:].strip()
        parts.append(text)
        return parts

    def decode_html_entities(self, text):
        """Декодирует HTML-сущности, такие как &gt;, &lt;, &amp;."""
        return html.unescape(text)

    def is_russian(self, text):
        """Проверяет, является ли текст на русском языке."""
        try:
            return detect(text) == 'ru'
        except:
            return False

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # Игнорируем сообщения не из нужного канала и от ботов
        if message.channel.id != self.source_channel_id:
            return
        if message.author.bot and not message.webhook_id:
            return

        try:
            # Если это сообщение с вложенными автоэмбедами (которые Discord создает для ссылок)
            if message.embeds and not message.content.strip():
                print("Сообщение содержит автоэмбед, пропускаем.")
                return

            # Если это обычное текстовое сообщение с новостью
            if message.content.strip():
                original_text = message.content.strip()

                # Сохраняем метки времени и очищаем текст
                preserved_text, time_tags = self.preserve_time_tags(original_text)
                cleaned_text = self.clean_message(preserved_text)

                # Если это не русский текст, переводим
                if not self.is_russian(cleaned_text):
                    translated_parts = [
                        self.translator.translate(part)
                        for part in self.split_text(cleaned_text)
                    ]
                    translated_text = "\n\n".join(translated_parts)
                    translated_text = self.decode_html_entities(translated_text)
                else:
                    translated_text = cleaned_text

                # Восстанавливаем метки времени
                translated_text = self.restore_time_tags(translated_text, time_tags)

                # Создаем embed для текста
                embed = disnake.Embed(
                    title="Sky News",
                    description=translated_text,
                    color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
                )

                # Добавляем изображение из вложений, если оно есть
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type and attachment.content_type.startswith("image"):
                            embed.set_image(url=attachment.url)
                            break

                # Отправляем embed с пингом роли в канал
                target_channel = self.bot.get_channel(self.target_channel_id)
                if target_channel:
                    role_mention = f"<@&{self.notify_role_id}>"  # Упоминание роли
                    await target_channel.send(
                        content=role_mention,
                        embed=embed,
                        allowed_mentions=disnake.AllowedMentions(roles=True)  # Разрешаем пинг роли
                    )
                    print(f"Сообщение отправлено: {translated_text}")
                else:
                    print("Целевой канал не найден.")

        except Exception as e:
            print(f"Ошибка при обработке сообщения: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(NewsSky(bot))
