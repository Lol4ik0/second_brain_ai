import os
import shutil
from git import Repo

def sync_obsidian_repo(repo_url, token, local_dir):
    """
    Safely synchronizes a user's GitHub repository to their isolated local sandbox.
    Supports private repositories via dynamic Personal Access Token injection.
    """
    if not repo_url:
        print(f"⚠️ Sync aborted: No repository URL assigned for target directory: {local_dir}")
        return False

    # Security measure: Authenticate via token if provided by injecting it securely
    authenticated_url = repo_url
    if token and "https://" in repo_url:
        # ИСПРАВЛЕНИЕ 1: Убрали 'oauth2:'. GitHub PAT работает напрямую через токен
        authenticated_url = repo_url.replace("https://", f"https://{token}@")

    print(f"🔄 Checking sync integrity for node workspace: {local_dir}")
    
    try:
        # Если папка существует и внутри есть .git - делаем pull
        if os.path.exists(local_dir) and os.path.exists(os.path.join(local_dir, '.git')):
            print("📥 Target path detected. Running git pull to synchronize updates...")
            repo = Repo(local_dir)
            repo.remotes.origin.set_url(authenticated_url)
            repo.remotes.origin.pull()
            print("✅ Synchronization completed successfully!")
            return True
        else:
            print("🚚 Local target instance not found (or incomplete). Initializing clone sequence...")
            
            # ИСПРАВЛЕНИЕ 2: Если папка создана, но внутри нет .git (клонирование прервалось),
            # GitPython выдаст ошибку. Поэтому мы удаляем поврежденную папку перед клонированием.
            if os.path.exists(local_dir):
                shutil.rmtree(local_dir)
            
            # Убеждаемся, что существует общая директория obsidian_data (родительская)
            parent_dir = os.path.dirname(local_dir)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                
            # Позволяем Git самому создать папку local_dir при клонировании
            Repo.clone_from(authenticated_url, local_dir)
            print("✅ Repository cloned into secure cluster partition successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Core Git synchronization failure: {str(e)}")
        return False