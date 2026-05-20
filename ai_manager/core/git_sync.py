import os
from git import Repo

def sync_obsidian_repo(repo_url, local_dir):
    """
    Проверяет, скачан ли репозиторий. 
    Если нет — клонирует. Если да — делает git pull.
    """
    print(f"🔄 Проверка репозитория Obsidian: {local_dir}")
    
    try:
        # Проверяем, существует ли папка и есть ли внутри нее скрытая папка .git
        if os.path.exists(local_dir) and os.path.exists(os.path.join(local_dir, '.git')):
            print("📥 Папка найдена. Выполняем 'git pull' для получения новых заметок...")
            repo = Repo(local_dir)
            origin = repo.remotes.origin
            origin.pull()
            print("✅ Заметки успешно обновлены!")
        else:
            print("🚚 Локальная копия не найдена. Клонируем репозиторий...")
            # Создаем папку, если ее вообще нет
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            Repo.clone_from(repo_url, local_dir)
            print("✅ Репозиторий успешно склонирован!")
            
    except Exception as e:
        print(f"❌ Ошибка при синхронизации с GitHub: {e}")
        # Если будет ошибка доступа, мы ее здесь увидим