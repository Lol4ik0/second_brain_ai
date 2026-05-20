import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb

# Импортируем нашу функцию синхронизации
from .git_sync import sync_obsidian_repo

# Указываем пути к папкам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ТЕПЕРЬ ТУТ БУДУТ ЛЕЖАТЬ ТВОИ РЕАЛЬНЫЕ ЗАМЕТКИ ИЗ GITHUB
NOTES_DIR = os.path.join(BASE_DIR, 'obsidian_data') 
DB_DIR = os.path.join(BASE_DIR, 'chroma_db')

# Ссылка на твой репозиторий
# ВАЖНО: Если репозиторий приватный, лучше использовать SSH ссылку (git@github.com:Lol4ik0/myObsidian.git)
GITHUB_REPO_URL = "https://github.com/Lol4ik0/myObsidian.git"


# НАСТРАИВАЕМ ЛОКАЛЬНЫЕ БЕСПЛАТНЫЕ МОДЕЛИ OLLAMA
Settings.llm = Ollama(model="llama3", request_timeout=1200.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

def initialize_index():
    # 1. СНАЧАЛА СКАЧИВАЕМ/ОБНОВЛЯЕМ ЗАМЕТКИ ИЗ GITHUB
    sync_obsidian_repo(GITHUB_REPO_URL, NOTES_DIR)
    
    # 2. ПОТОМ ЧИТАЕМ ИХ
    print(f"Читаем файлы из папки: {NOTES_DIR}...")
    # Ограничиваем чтение только .md файлами, чтобы не читать системные файлы git и картинки
    documents = SimpleDirectoryReader(NOTES_DIR, required_exts=[".md"], recursive=True).load_data()
    
    print("Инициализируем локальную ChromaDB...")
    db = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db.get_or_create_collection("second_brain")
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    print("Создаем векторы и сохраняем...")
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    print("Индексация успешно завершена!")
    return index


# Глобальная переменная для хранения памяти чата
_chat_engine = None

def ask_second_brain(user_query):
    global _chat_engine
    
    try:
        # Если чат запускается впервые, инициализируем базу и создаем движок с памятью
        if _chat_engine is None:
            db = chromadb.PersistentClient(path=DB_DIR)
            chroma_collection = db.get_collection("second_brain")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            index = VectorStoreIndex.from_vector_store(vector_store)
            
            # ВАЖНО: Используем as_chat_engine вместо as_query_engine
            # chat_mode="context" заставляет ИИ держать в оперативной памяти историю текущей беседы
            _chat_engine = index.as_chat_engine(
                chat_mode="context",
                similarity_top_k=3,
                system_prompt=(
                    "Ты — персональный ИИ-ассистент 'Second Brain'. "
                    "Отвечай на вопросы пользователя ТОЛЬКО опираясь на предоставленный контекст. "
                    "Если в контексте нет ответа, честно скажи: 'В твоих заметках нет информации об этом'. Отвечай на русском языке."
                )
            )
        
        # ВАЖНО: Используем метод .chat() вместо .query()
        response = _chat_engine.chat(user_query)
        return str(response)
        
    except Exception as e:
        print(f"Ошибка RAG: {e}")
        return "Система еще не проиндексирована. Пожалуйста, проверьте наличие заметок."