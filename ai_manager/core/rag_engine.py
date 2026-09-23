import os
import requests
import logging
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
os.makedirs(LOGS_DIR, exist_ok=True) # Создаем папку logs, если её нет

log_file_path = os.path.join(LOGS_DIR, 'rag_engine.log')

# Настраиваем ротацию: W0 = Понедельник, interval=1 (раз в неделю), backupCount=4 (храним логи за месяц)
file_handler = TimedRotatingFileHandler(
    log_file_path, 
    when="W0", 
    interval=1, 
    backupCount=4, 
    encoding='utf-8'
)
console_handler = logging.StreamHandler() # Чтобы логи всё ещё было видно в консоли Docker

formatter = logging.Formatter('[RAG ENGINE] %(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Очищаем старые обработчики, чтобы логи не двоились при перезагрузке Django
if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)
logger.addHandler(console_handler)
# -----------------------------

# Кэш чат-движков для активных пользователей
_user_chat_engines = {}

# Сетевые настройки для основного ПК (Узел Б)
LOCAL_OLLAMA_URL = "http://192.168.1.128:11434"

def is_local_ai_ready(timeout=0.5):
    """
    Проверяет доступность Ollama на основном ПК.
    """
    logger.info(f"==> Проверка доступности Ollama по адресу: {LOCAL_OLLAMA_URL}/api/tags")
    try:
        response = requests.get(f"{LOCAL_OLLAMA_URL}/api/tags", timeout=timeout)
        if response.status_code == 200:
            logger.info("==> Ollama ОТВЕТИЛА (Статус 200).")
            # Для отладки выведем список моделей, которые видит сервер!
            models = response.json().get('models', [])
            model_names = [m.get('name') for m in models]
            logger.info(f"==> Доступные модели в Ollama: {model_names}")
            return True
        else:
            logger.warning(f"==> Ollama вернула странный статус: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"==> Ошибка подключения к Ollama: {e}")
        return False

def reset_chat_engine(user_id=None):
    global _user_chat_engines
    if user_id:
        if user_id in _user_chat_engines:
            del _user_chat_engines[user_id]
            logger.info(f"==> Сброшен кэш чата для пользователя {user_id}")
    else:
        _user_chat_engines.clear()
        logger.info("==> Кэш чата полностью очищен")

def get_user_paths(user):
    """Генерирует изолированные пути для данных пользователя."""
    user_folder = f"user_{user.id}"
    return {
        "notes_dir": os.path.join(BASE_DIR, 'obsidian_data', user_folder),
        "collection_name": f"collection_user_{user.id}"
    }

def ask_second_brain(user_query, user):
    global _user_chat_engines
    
    settings = user.settings
    paths = get_user_paths(user)
    
    logger.info(f"--- НАЧАЛО ОБРАБОТКИ ЗАПРОСА ОТ ПОЛЬЗОВАТЕЛЯ: {user.username} ---")
    logger.info(f"Вопрос: {user_query}")
    
    if not settings.github_repo_url:
        logger.error("Отсутствует ссылка на GitHub репозиторий.")
        return "System Notification: Please configure your personal GitHub Obsidian repository link in the Settings panel."

    try:
        if user.id not in _user_chat_engines:
            logger.info(f"Кэш пуст. Инициализация ИИ-ядра для: {user.username}")
            
            logger.info("Шаг 1: Синхронизация с GitHub...")
            sync_success = sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])
            logger.info(f"Результат синхронизации: {sync_success}")
            
            logger.info(f"Шаг 2: Настройка модели эмбеддингов (URL: {LOCAL_OLLAMA_URL})...")
            # ЯВНО УКАЗЫВАЕМ URL ДЛЯ ЭМБЕДДИНГОВ
            Settings.embed_model = OllamaEmbedding(
                model_name="nomic-embed-text", 
                base_url=LOCAL_OLLAMA_URL
            )

            logger.info("Шаг 3: Маршрутизация LLM (Проверка локального ПК)...")
            if is_local_ai_ready():
                model_to_use = settings.ai_model if settings.ai_model != "gemini" else "llama3"
                logger.info(f"==> ИСПОЛЬЗУЕМ ЛОКАЛЬНУЮ OLLAMA. Модель: {model_to_use}")
                Settings.llm = Ollama(
                    model=model_to_use, 
                    base_url=LOCAL_OLLAMA_URL,
                    temperature=settings.temperature, 
                    request_timeout=600.0
                )
            else:
                logger.info("==> ИСПОЛЬЗУЕМ ОБЛАКО (GEMINI).")
                gemini_key = os.getenv("GEMINI_API_KEY")
                if not gemini_key:
                    logger.error("Ключ GEMINI_API_KEY не найден в .env!")
                    return "System Status Alert: GEMINI_API_KEY is missing inside your secure server .env matrix."
                
                Settings.llm = GoogleGenAI(
                    model="gemini-1.5-pro", 
                    api_key=gemini_key
                )
            
            logger.info("Шаг 4: Инициализация ChromaDB...")
            db = chromadb.PersistentClient(path=DB_DIR)
            chroma_collection = db.get_or_create_collection(paths["collection_name"])
            
            logger.info("Шаг 5: Загрузка документов из папки...")
            documents = []
            if sync_success and os.path.exists(paths["notes_dir"]):
                documents = SimpleDirectoryReader(paths["notes_dir"], required_exts=[".md"], recursive=True).load_data()
                logger.info(f"Загружено документов: {len(documents)}")
            else:
                logger.warning("Папка с заметками не найдена или пуста!")
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            logger.info("Шаг 6: Создание векторного индекса (ТУТ ПРОИСХОДИТ ВЕКТОРИЗАЦИЯ)...")
            if documents:
                logger.info("Создаем индекс из документов...")
                index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            else:
                logger.info("Документов нет, загружаем существующий индекс из БД...")
                index = VectorStoreIndex.from_vector_store(vector_store)
                
            logger.info("Шаг 7: Создание Chat Engine...")
            _user_chat_engines[user.id] = index.as_chat_engine(
                chat_mode="context",
                similarity_top_k=3,
                system_prompt=(
                    f"You are the secure personal AI Assistant of {user.username}. "
                    "Answer questions ONLY based on the provided personal notes context. "
                    "If the answer cannot be found in the user notes context, state: 'No data matching this query found in your synchronized notes database.' "
                    "Always answer questions in English language."
                )
            )
            logger.info("Инициализация успешно завершена!")
        else:
             logger.info(f"Используем готовый кэш чата для: {user.username}")
        
        logger.info("Шаг 8: Генерация ответа ИИ...")
        response = _user_chat_engines[user.id].chat(user_query)
        logger.info(f"Ответ ИИ получен: {str(response)[:50]}...") # Выводим только начало ответа
        logger.info("--- ЗАВЕРШЕНО УСПЕШНО ---")
        return str(response)
        
    except Exception as e:
        logger.exception("!!! КРИТИЧЕСКАЯ ОШИБКА В RAG_ENGINE !!!")
        return f"Core System Error: Failed to compute query. Details: {str(e)}"