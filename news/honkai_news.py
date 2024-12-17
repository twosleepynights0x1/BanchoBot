import disnake
from disnake.ext import commands
from translate import Translator
import re  # Для работы с регулярными выражениями
import html  # Для декодирования HTML-символов
from langdetect import detect  # Для определения языка
import json
import os

class NewsHonkai(commands.Cog):
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
        config_path = os.path.join("data", "honkai_news.json")
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

    def clean_message(self, text):
        """Удаляет серверные эмодзи и стикеры из текста, оставляя стандартные эмодзи."""
        # Удаляем серверные эмодзи вида <:name:id> и <a:name:id>
        text = re.sub(r"<a?:\w+:\d+>", "", text)
        # Удаляем стикеры вида :stickerName:
        text = re.sub(r":\w+:", "", text)
        # Убираем лишние пробелы
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
        if message.channel.id != self.source_channel_id:
            return

        if message.author.bot and not message.webhook_id:
            return

        try:
            # Если это обычное сообщение
            if message.content.strip():
                original_text = message.content.strip()
                cleaned_text = self.clean_message(original_text)

                # Проверяем, на каком языке текст
                if self.is_russian(cleaned_text):
                    print("Сообщение на русском, отправляем как есть.")
                    translated_text = cleaned_text
                else:
                    # Разделяем текст и переводим каждую часть
                    translated_parts = [
                        self.translator.translate(part)
                        for part in self.split_text(cleaned_text)
                    ]
                    translated_text = "\n\n".join(translated_parts)

                    # Декодируем HTML-сущности (например, &gt; -> >)
                    translated_text = self.decode_html_entities(translated_text)

                # Создаем embed для текста
                embed = disnake.Embed(
                    title="Honkai News",
                    description=translated_text,
                    color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
                )

                # Добавляем изображение из вложений
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type and attachment.content_type.startswith("image"):
                            embed.set_image(url=attachment.url)
                            break

                # Отправляем embed с пингом роли
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

            # Если это embed-сообщение
            if message.embeds:
                for embed in message.embeds:
                    # Переводим описание и заголовок embed, если они не на русском
                    if embed.title and not self.is_russian(embed.title):
                        translated_title = self.translator.translate(embed.title)
                    else:
                        translated_title = embed.title

                    if embed.description and not self.is_russian(embed.description):
                        translated_description = self.translator.translate(embed.description)
                    else:
                        translated_description = embed.description

                    # Декодируем HTML-сущности
                    translated_title = self.decode_html_entities(translated_title) if translated_title else None
                    translated_description = self.decode_html_entities(translated_description) if translated_description else None

                    # Создаем новый переведенный embed
                    translated_embed = disnake.Embed(
                        title=translated_title,
                        description=translated_description,
                        color=disnake.Color.from_rgb(255, 182, 193)  # Нежный розовый цвет
                    )

                    # Добавляем изображение из оригинального embed (если есть)
                    if embed.image and embed.image.url:
                        translated_embed.set_image(url=embed.image.url)

                    # Добавляем дополнительные элементы, такие как thumbnail, footer, author и поля
                    if embed.thumbnail and embed.thumbnail.url:
                        translated_embed.set_thumbnail(url=embed.thumbnail.url)

                    if embed.footer:
                        translated_embed.set_footer(text=self.translator.translate(embed.footer.text))

                    if embed.author:
                        translated_embed.set_author(name=self.translator.translate(embed.author.name))

                    for field in embed.fields:
                        translated_embed.add_field(
                            name=self.translator.translate(field.name),
                            value=self.translator.translate(field.value),
                            inline=field.inline
                        )

                    # Отправляем переведенный embed в канал
                    target_channel = self.bot.get_channel(self.target_channel_id)
                    if target_channel:
                        role_mention = f"<@&{self.notify_role_id}>"  # Упоминание роли
                        await target_channel.send(
                            content=role_mention,
                            embed=translated_embed,
                            allowed_mentions=disnake.AllowedMentions(roles=True)  # Разрешаем пинг роли
                        )
                        print("Переведенный embed отправлен.")
                    else:
                        print("Целевой канал не найден.")

        except Exception as e:
            print(f"Ошибка при обработке сообщения: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(NewsHonkai(bot))
