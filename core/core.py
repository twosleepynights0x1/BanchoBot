import disnake
from disnake.ext import commands
import threading
import os
import json
from pathlib import Path
from colorama import Fore, Style, init
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Устанавливаем заголовок окна
os.system('title Bancho [Server Bandicoot]')

# Инициализация colorama
init()

# Загружаем конфигурацию из JSON файла
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

# Загружаем статус бота из JSON файла
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/status.json'), 'r', encoding='utf-8') as f:
    status_config = json.load(f)

# Загружаем список папок с когами
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/cogs.json'), 'r', encoding='utf-8') as f:
    cogs_config = json.load(f)

# Включаем все намерения для работы с контентом сообщений, пользователями и событиями
intents = disnake.Intents.default()
intents.message_content = True      # Включаем намерение для работы с контентом сообщений
intents.members = True            # Для получения данных о членах сервера
intents.reactions = True         # Для работы с реакциями на сообщения  
intents.guilds = True           # Для работы с серверами

# Указываем ID тестовой гильдии для быстрого тестирования слэш-команд
bot = commands.Bot(
    command_prefix=config['prefix'],
    intents=intents,
    test_guilds=[config['test_guild_id']]
)

# Функция для загрузки когов
def load_cogs():
    # Получаем путь к корневой директории проекта
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    for folder in cogs_config['cog_folders']:
        cogs_path = Path(os.path.join(root_dir, folder))
        if not cogs_path.exists():
            print(f"\033[1m{Fore.LIGHTGREEN_EX}Папка {folder} не найдена{Style.RESET_ALL}")
            continue
            
        for cog_file in cogs_path.glob("*.py"):
            if cog_file.stem.startswith("_"):
                continue
                
            cog_name = f"{folder}.{cog_file.stem}"
            try:
                bot.load_extension(cog_name)
                print(f"\033[1m{Fore.LIGHTGREEN_EX}Загружен ког: {cog_name}{Style.RESET_ALL}")
            except Exception as e:
                print(f"\033[1m{Fore.LIGHTGREEN_EX}Ошибка при загрузке кога {cog_name}: {e}{Style.RESET_ALL}")

# Загрузка расширений ДО старта бота
@bot.event
async def on_ready():
    print(f'\033[1m{Fore.LIGHTGREEN_EX}Мы подключились как {bot.user}{Style.RESET_ALL}')
    
    try:
        # Загружаем коги
        load_cogs()
        
        # Устанавливаем статус бота из конфигурации
        activity = disnake.Activity(
            type=getattr(disnake.ActivityType, status_config['type']), 
            name=status_config['name']
        )
        await bot.change_presence(activity=activity)

        print(f"\033[1m{Fore.LIGHTGREEN_EX}Команды синхронизированы успешно.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\033[1m{Fore.LIGHTGREEN_EX}Ошибка при синхронизации команд: {e}{Style.RESET_ALL}")

# Запуск бота
bot.run(config['token'])
