import subprocess
import os
import sys

def install_requirements():
    # Получаем путь к директории, где находится текущий скрипт
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Путь к requirements.txt в той же директории
    req_path = os.path.join(current_dir, 'requirements.txt')
    
    # Проверяем существование файла
    if not os.path.exists(req_path):
        print("Файл requirements.txt не найден!")
        return False
        
    try:
        # Устанавливаем пакеты через pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_path])
        print("Все зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей: {e}")
        return False

if __name__ == "__main__":
    install_requirements()
