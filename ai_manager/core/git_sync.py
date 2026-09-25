"""GitPython adapter that clones or updates each user's private Obsidian vault."""
import os
import shutil
import logging
from git import Repo

logger = logging.getLogger(__name__)

def sync_obsidian_repo(repo_url, token, local_dir):
    """
    Synchronize a user's remote vault into the account-specific local directory.

    Args:
        repo_url: GitHub clone URL stored in the user's settings.
        token: Optional personal access token for private repositories.
        local_dir: Isolated filesystem directory assigned to this user.

    Returns:
        True when a clone or pull completes; False when configuration or Git I/O fails.
    """
    if not repo_url:
        logger.warning("Repository sync skipped: repository URL is not configured.")
        return False

    # Inject credentials only into the URL used by GitPython; persisted settings
    # continue to keep the token in the encrypted model field.
    authenticated_url = repo_url
    if token and "https://" in repo_url:
        # GitHub accepts a personal access token as the HTTPS password component.
        authenticated_url = repo_url.replace("https://", f"https://{token}@")

    logger.info("Repository sync started.")
    
    try:
        # Existing Git metadata means this directory is a clone that can be pulled.
        if os.path.exists(local_dir) and os.path.exists(os.path.join(local_dir, '.git')):
            logger.info("Repository clone found; pulling updates.")
            repo = Repo(local_dir)
            repo.remotes.origin.set_url(authenticated_url)
            repo.remotes.origin.pull()
            logger.info("Repository pull completed.")
            return True
        else:
            logger.info("Repository clone missing; cloning repository.")
            
            # Remove an incomplete prior clone before retrying, otherwise GitPython
            # may refuse to initialize a repository in the damaged directory.
            if os.path.exists(local_dir):
                shutil.rmtree(local_dir)
            
            # Ensure the shared parent directory exists before asking Git to clone.
            parent_dir = os.path.dirname(local_dir)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                
            # Let GitPython create the account-specific target directory.
            Repo.clone_from(authenticated_url, local_dir)
            logger.info("Repository clone completed.")
            return True
            
    except Exception as error:
        logger.error("Repository sync failed: %s.", type(error).__name__)
        return False