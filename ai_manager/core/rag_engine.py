import os
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb
from .git_sync import sync_obsidian_repo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_DIR = os.path.join(BASE_DIR, 'obsidian_data') 
DB_DIR = os.path.join(BASE_DIR, 'chroma_db')
CONFIG_FILE = os.path.join(BASE_DIR, 'app_config.json')
GITHUB_REPO_URL = "https://github.com/Lol4ik0/myObsidian.git"

_chat_engine = None

def load_ai_settings():
    """Считывает выбранную на сайте модель и температуру"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ai_model', 'llama3'), float(data.get('temperature', 0.7))
    except:
        pass
    return "llama3", 0.7

def reset_chat_engine():
    """Обнуляет движок чата (вызывается из views.py при сохранении настроек)"""
    global _chat_engine
    _chat_engine = None

def initialize_index():
    sync_obsidian_repo(GITHUB_REPO_URL, NOTES_DIR)
    documents = SimpleDirectoryReader(NOTES_DIR, required_exts=[".md"], recursive=True).load_data()
    
    db = chromadb.PersistentClient(path=DB_DIR)
    chroma_collection = db.get_or_create_collection("second_brain")
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print("Индексация успешно завершена!")
    return index

def ask_second_brain(user_query):
    global _chat_engine
    
    try:
        if _chat_engine is None:
            model_name, temperature = load_ai_settings()
            print(f"🤖 Инициализация ядра ИИ. Модель: {model_name}, Температура: {temperature}")
            
            Settings.llm = Ollama(model=model_name, temperature=temperature, request_timeout=600.0)
            Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
            
            db = chromadb.PersistentClient(path=DB_DIR)
            chroma_collection = db.get_collection("second_brain")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            index = VectorStoreIndex.from_vector_store(vector_store)
            
            _chat_engine = index.as_chat_engine(
                chat_mode="context",
                similarity_top_k=3,
                system_prompt=(
                    "Ты — персональный ИИ-ассистент 'Second Brain'. "
                    "Отвечай на вопросы пользователя ТОЛЬКО опираясь на предоставленный контекст заметок. "
                    "Если в контексте нет ответа, честно скажи: 'В твоих заметках нет информации об этом'. Отвечай на русском языке."
                )
            )
        
        response = _chat_engine.chat(user_query)
        return str(response)
        
    except Exception as e:
        print(f"Ошибка RAG: {e}")
        return f"Произошла ошибка конфигурации ИИ: {str(e)}"