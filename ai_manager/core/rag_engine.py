import os
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.vector_stores.types import ExactMatchFilter, FilterCondition, MetadataFilters
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
_user_indexes = {}
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
    global _user_chat_engines, _user_indexes
    if user_id and user_id in _user_chat_engines:
        del _user_chat_engines[user_id]
        _user_indexes.pop(user_id, None)
    else:
        _user_chat_engines.clear()
        _user_indexes.clear()

def get_user_paths(user):
    user_folder = f"user_{user.id}"
    return {
        "notes_dir": os.path.join(BASE_DIR, 'obsidian_data', user_folder),
        "collection_name": f"collection_user_{user.id}"
    }

def ask_second_brain(user_query, user, selected_files=None):
    global _user_chat_engines, _user_indexes
    selected_files = selected_files or []
    
    settings = user.settings
    paths = get_user_paths(user)
    ai_strategy = settings.ai_strategy or 'auto'
    try:
        temp = float(settings.temperature)
    except (TypeError, ValueError):
        temp = 0.7
    
    logger.info(f"Обработка запроса: {user_query}")
    
    if not settings.github_repo_url:
        return "System Notification: Please configure your GitHub link."

    try:
        local_online = is_local_ai_ready()

        if ai_strategy == 'local_only' and not local_online:
            return "System Error: Local AI is strictly selected but the PC is offline"

        use_local_ai = (
            ai_strategy == 'local_only'
            or (ai_strategy == 'auto' and local_online)
        )
        
        if user.id in _user_chat_engines:
            if getattr(_user_chat_engines[user.id], '_is_local_engine', False) != use_local_ai:
                logger.info("Смена состояния ПК. Сброс кэша LLM.")
                reset_chat_engine(user.id)

        if user.id not in _user_chat_engines:
            sync_success = sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])
            
            # МАРШРУТИЗАЦИЯ ТОЛЬКО ДЛЯ ТЕКСТА (LLM)
            if use_local_ai:
                logger.info("ПК Включен. Текст генерирует Ollama.")
                Settings.llm = Ollama(
                    model="llama3:latest",
                    base_url=LOCAL_OLLAMA_URL,
                    temperature=temp,
                    request_timeout=600.0
                )
            else:
                logger.info("Текст генерирует Gemini 3.6 Flash.")
                gemini_key = os.getenv("GEMINI_API_KEY")
                Settings.llm = GoogleGenAI(
                    model="gemini-3.6-flash",
                    api_key=gemini_key,
                    temperature=temp,
                )
            
            # Инициализация ChromaDB
            db = chromadb.PersistentClient(path=DB_DIR)
            
            # get_or_create_collection сам создаст базу, если её нет, без ошибок
            chroma_collection = db.get_or_create_collection(paths["collection_name"])
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Проверяем количество векторов напрямую в базе
            if chroma_collection.count() == 0:
                logger.info("База пуста. Начинаем создание векторов (CPU сервера)...")
                documents = []
                if sync_success and os.path.exists(paths["notes_dir"]):
                    documents = SimpleDirectoryReader(paths["notes_dir"], required_exts=[".md"], recursive=True).load_data()
                
                if documents:
                    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
                else:
                    index = VectorStoreIndex.from_vector_store(vector_store)
            else:
                logger.info(f"База найдена (векторов: {chroma_collection.count()}). Загружаем из ChromaDB.")
                index = VectorStoreIndex.from_vector_store(vector_store)
                
                # УМНОЕ ОБНОВЛЕНИЕ (Smart Sync)
                if sync_success and os.path.exists(paths["notes_dir"]):
                    logger.info("Обнаружены изменения в GitHub! Синхронизируем векторную базу...")
                    documents = SimpleDirectoryReader(paths["notes_dir"], required_exts=[".md"], recursive=True).load_data()
                    
                    # refresh_ref_docs сверяет хэши файлов и векторизует только новые/измененные
                    refreshed = index.refresh_ref_docs(documents)
                    logger.info(f"Синхронизация векторов завершена. Обновлено/добавлено файлов: {sum(refreshed)}")
                
            _user_indexes[user.id] = index

        chat_engine_options = {}
        if selected_files:
            file_names = [
                file_name if file_name.lower().endswith(".md") else f"{file_name}.md"
                for file_name in selected_files
            ]
            my_filters = MetadataFilters(
                filters=[
                    ExactMatchFilter(key="file_name", value=file_name)
                    for file_name in file_names
                ],
                condition=FilterCondition.OR,
            )
            chat_engine_options["filters"] = my_filters

        engine = _user_indexes[user.id].as_chat_engine(
            chat_mode="context",
            similarity_top_k=5,
            system_prompt=(
                f"You are the secure personal AI Assistant of {user.username}. "
                "Answer questions ONLY based on the provided personal notes context."
            ),
            **chat_engine_options,
        )
        engine._is_local_engine = use_local_ai
        _user_chat_engines[user.id] = engine
        response = engine.chat(user_query)
        return str(response)
        
    except Exception as e:
        logger.exception(f"Ошибка RAG: {e}")
        return f"System Error: {str(e)}"