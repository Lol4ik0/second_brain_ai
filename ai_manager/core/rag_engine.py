import os
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from .git_sync import sync_obsidian_repo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'chroma_db')

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

log_file_path = os.path.join(LOGS_DIR, 'rag_engine.log')
file_handler = TimedRotatingFileHandler(log_file_path, when="W0", interval=1, backupCount=4, encoding='utf-8')
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

# ГЛОБАЛЬНАЯ НАСТРОЙКА ВЕКТОРОВ (Локально на сервере, размерность 384)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

def is_local_ai_ready(timeout=0.5):
    try:
        response = requests.get(f"{LOCAL_OLLAMA_URL}/api/tags", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def reset_chat_engine(user_id=None):
    global _user_chat_engines
    if user_id and user_id in _user_chat_engines:
        del _user_chat_engines[user_id]
    else:
        _user_chat_engines.clear()

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
    
    logger.info(f"Обработка запроса: {user_query}")
    
    if not settings.github_repo_url:
        return "System Notification: Please configure your GitHub link."

    try:
        local_online = is_local_ai_ready()
        
        if user.id in _user_chat_engines:
            if getattr(_user_chat_engines[user.id], '_is_local_engine', False) != local_online:
                logger.info("Смена состояния ПК. Сброс кэша LLM.")
                reset_chat_engine(user.id)

        if user.id not in _user_chat_engines:
            sync_success = sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])
            
            # МАРШРУТИЗАЦИЯ ТОЛЬКО ДЛЯ ТЕКСТА (LLM)
            if local_online:
                logger.info("ПК Включен. Текст генерирует Ollama.")
                Settings.llm = Ollama(
                    model=settings.ai_model if settings.ai_model != "gemini" else "llama3:latest", 
                    base_url=LOCAL_OLLAMA_URL,
                    temperature=settings.temperature, 
                    request_timeout=600.0
                )
            else:
                logger.info("ПК Выключен. Текст генерирует Gemini 3.6 Flash.")
                gemini_key = os.getenv("GEMINI_API_KEY")
                Settings.llm = GoogleGenAI(model="gemini-3.6-flash", api_key=gemini_key)
            
            # Инициализация ChromaDB
            db = chromadb.PersistentClient(path=DB_DIR)
            
            # get_or_create_collection сам создаст базу, если её нет, без ошибок
            chroma_collection = db.get_or_create_collection(paths["collection_name"])
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Проверяем, пустая ли коллекция
            if chroma_collection.count() == 0:
                logger.info("База пуста. Начинаем создание векторов (CPU сервера)...")
                documents = SimpleDirectoryReader(paths["notes_dir"], required_exts=[".md"], recursive=True).load_data() if sync_success and os.path.exists(paths["notes_dir"]) else []
                
                if documents:
                    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
                else:
                    index = VectorStoreIndex.from_vector_store(vector_store)
            else:
                logger.info(f"База найдена (векторов: {chroma_collection.count()}). Загружаем из ChromaDB.")
                index = VectorStoreIndex.from_vector_store(vector_store)
                
            engine = index.as_chat_engine(
                chat_mode="context",
                similarity_top_k=3,
                system_prompt=(
                    f"You are the secure personal AI Assistant of {user.username}. "
                    "Answer questions ONLY based on the provided personal notes context."
                )
            )
            engine._is_local_engine = local_online
            _user_chat_engines[user.id] = engine

        response = _user_chat_engines[user.id].chat(user_query)
        return str(response)
        
    except Exception as e:
        logger.exception(f"Ошибка RAG: {e}")
        return f"System Error: {str(e)}"