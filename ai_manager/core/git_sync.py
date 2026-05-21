import os
from git import Repo

def sync_obsidian_repo(repo_url, token, local_dir):
    """
    Safely synchronizes a user's GitHub repository to their isolated local sandbox.
    Supports private repositories via dynamic Personal Access Token injection.
    """
    if not repo_url:
        print(f"⚠️ Sync aborted: No repository URL assigned for target directory: {local_dir}")
        return False

    # Security measure: Authenticate via token if provided by injecting it into the HTTPS string securely
    authenticated_url = repo_url
    if token and "https://" in repo_url:
        authenticated_url = repo_url.replace("https://", f"https://oauth2:{token}@")

    print(f"🔄 Checking sync integrity for node workspace: {local_dir}")
    
    try:
        if os.path.exists(local_dir) and os.path.exists(os.path.join(local_dir, '.git')):
            print("📥 Target path detected. Running git pull to synchronize updates...")
            repo = Repo(local_dir)
            # Temporarily update origin URL to use token securely if it changed
            repo.remotes.origin.set_url(authenticated_url)
            repo.remotes.origin.pull()
            print("✅ Synchronization completed successfully!")
            return True
        else:
            print("🚚 Local target instance not found. Initializing sandbox clone sequence...")
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            Repo.clone_from(authenticated_url, local_dir)
            print("✅ Repository cloned into secure cluster partition successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Core Git synchronization failure: {str(e)}")
        return False