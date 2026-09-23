import os
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from .git_sync import sync_obsidian_repo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'chroma_db')

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

log_file_path = os.path.join(LOGS_DIR, 'rag_engine.log')

# Ротация: W0 = каждый понедельник в полночь, backupCount = 4 (хранить архив за 4 недели)
file_handler = TimedRotatingFileHandler(
    log_file_path, 
    when="W0", 
    interval=1, 
    backupCount=4, 
    encoding='utf-8'
)
console_handler = logging.StreamHandler()

log_format = logging.Formatter('[RAG ENGINE] %(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
console_handler.setFormatter(log_format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)
logger.addHandler(console_handler)
# -----------------------------

_user_chat_engines = {}
LOCAL_OLLAMA_URL = "http://192.168.1.128:11434"

def is_local_ai_ready(timeout=0.5):
    """Проверка доступности локальной Ollama."""
    try:
        response = requests.get(f"{LOCAL_OLLAMA_URL}/api/tags", timeout=timeout)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name') for m in models]
            logger.info(f"Ollama доступна. Модели в наличии: {model_names}")
            return True
        return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"Локальный ПК недоступен: {e}")
        return False

def reset_chat_engine(user_id=None):
    global _user_chat_engines
    if user_id:
        if user_id in _user_chat_engines:
            del _user_chat_engines[user_id]
            logger.info(f"Сброшен кэш сессии для пользователя {user_id}")
    else:
        _user_chat_engines.clear()
        logger.info("Кэш сессий полностью очищен")

def get_user_paths(user):
    user_folder = f"user_{user.id}"
    return {
        "notes_dir": os.path.join(BASE_DIR, 'obsidian_data', user_folder),
        "collection_name": f"collection_user_{user.id}"
    }

def ask_second_brain(user_query, user):
    global _user_chat_engines
    
    settings = user.settings
    paths = get_user_paths(user)
    
    logger.info(f"Обработка запроса пользователя {user.username}: {user_query}")
    
    if not settings.github_repo_url:
        return "System Notification: Please configure your personal GitHub Obsidian repository link in the Settings panel."

    try:
        # Если ПК отключился во время активной сессии, сбрасываем кэш для переключения
        local_online = is_local_ai_ready()
        if user.id in _user_chat_engines:
            current_engine_is_local = getattr(_user_chat_engines[user.id], '_is_local_engine', False)
            if current_engine_is_local != local_online:
                logger.info("Статус доступности локального ПК изменился. Пересоздаем сессию.")
                reset_chat_engine(user.id)

        if user.id not in _user_chat_engines:
            logger.info(f"Инициализация контекстного движка для пользователя: {user.username}")
            sync_success = sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])
            
            # Настройка эмбеддингов
            # Settings.embed_model = OllamaEmbedding(
            #     model_name="nomic-embed-text", 
            #     base_url=LOCAL_OLLAMA_URL
            # )

            # Маршрутизация LLM
            if local_online:
                model_to_use = settings.ai_model if settings.ai_model != "gemini" else "llama3:latest"
                logger.info(f"Назначена локальная модель LLM: {model_to_use} и локальные эмбеддинги.")
                
                # Локальная генерация текста
                Settings.llm = Ollama(
                    model=model_to_use, 
                    base_url=LOCAL_OLLAMA_URL,
                    temperature=settings.temperature, 
                    request_timeout=600.0
                )
                
                # Локальные векторы
                Settings.embed_model = OllamaEmbedding(
                    model_name="nomic-embed-text", 
                    base_url=LOCAL_OLLAMA_URL
                )
            else:
                logger.info("Переключение на облачное API Gemini (LLM + Эмбеддинги).")
                gemini_key = os.getenv("GEMINI_API_KEY")
                if not gemini_key:
                    return "System Status Alert: GEMINI_API_KEY is missing in your .env configuration."
                
                # Облачная генерация текста
                Settings.llm = GoogleGenAI(
                    model="gemini-2.5-flash", 
                    api_key=gemini_key
                )
                
                # Облачные векторы (ВАЖНО! Заменили локальную модель на облачную)
                from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
                Settings.embed_model = GoogleGenAIEmbedding(
                    model_name="gemini-embedding-2-preview", 
                    api_key=gemini_key
                )
            
            db = chromadb.PersistentClient(path=DB_DIR)
            chroma_collection = db.get_or_create_collection(paths["collection_name"])
            
            documents = []
            if sync_success and os.path.exists(paths["notes_dir"]):
                documents = SimpleDirectoryReader(paths["notes_dir"], required_exts=[".md"], recursive=True).load_data()
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            if documents:
                index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            else:
                index = VectorStoreIndex.from_vector_store(vector_store)
                
            engine = index.as_chat_engine(
                chat_mode="context",
                similarity_top_k=3,
                system_prompt=(
                    f"You are the secure personal AI Assistant of {user.username}. "
                    "Answer questions ONLY based on the provided personal notes context. "
                    "If the answer cannot be found in the user notes context, state: 'No data matching this query found in your synchronized notes database.' "
                    "Always answer questions in English language."
                )
            )
            engine._is_local_engine = local_online
            _user_chat_engines[user.id] = engine

        response = _user_chat_engines[user.id].chat(user_query)
        logger.info("Ответ успешно сформирован.")
        return str(response)
        
    except Exception as e:
        logger.exception(f"Критическая ошибка RAG: {e}")
        return f"Core System Error: Failed to compute query. Details: {str(e)}"