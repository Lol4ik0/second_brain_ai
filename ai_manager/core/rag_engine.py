import os
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb
from .git_sync import sync_obsidian_repo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'chroma_db')

# Use a multi-tenant dictionary to cache chat engines for active users in memory securely
_user_chat_engines = {}

def reset_chat_engine(user_id=None):
    global _user_chat_engines
    if user_id:
        if user_id in _user_chat_engines:
            del _user_chat_engines[user_id]
    else:
        _user_chat_engines.clear()

def get_user_paths(user):
    """Generates strictly isolated path points for individual user assets."""
    user_folder = f"user_{user.id}"
    return {
        "notes_dir": os.path.join(BASE_DIR, 'obsidian_data', user_folder),
        "collection_name": f"collection_user_{user.id}"
    }

def ask_second_brain(user_query, user):
    global _user_chat_engines
    
    # Extract user-specific settings from the database row
    settings = user.settings
    paths = get_user_paths(user)
    
    # If this user hasn't set up a repo yet, notify them securely
    if not settings.github_repo_url:
        return "System Notification: Please configure your personal GitHub Obsidian repository link in the Settings panel to enable the AI Core."

    try:
        # Check if we need to synchronize and index new data for this specific session
        if user.id not in _user_chat_engines:
            print(f"🤖 Initializing dedicated AI Core for User: {user.username} [Model: {settings.ai_model}]")
            
            # Sync the repository to the user's isolated folder
            sync_success = sync_obsidian_repo(settings.github_repo_url, settings.github_token, paths["notes_dir"])
            
            # Load global LLM parameters
            # --- DYNAMIC AI ENGINE ROUTER BASED ON USER SETTINGS ---
            if settings.ai_model == "gemini":
                # Lazy import Gemini extensions to preserve local memory if not used
                from llama_index.llms.gemini import Gemini
                from llama_index.embeddings.gemini import GeminiEmbedding
                
                gemini_key = os.getenv("GEMINI_API_KEY")
                if not gemini_key:
                    return "System Status Alert: GEMINI_API_KEY is missing inside your secure server .env matrix."
                
                # Configure ultra-fast Google API architecture
                Settings.llm = Gemini(model="models/gemini-1.5-pro", api_key=gemini_key)
                Settings.embed_model = GeminiEmbedding(model_name="models/text-embedding-004", api_key=gemini_key)
                print(f"Connected to Cloud Neural Cluster: Gemini 1.5 Pro for Operator {user.username}")
            else:
                # Fallback to local offline Ollama processing clusters
                Settings.llm = Ollama(model=settings.ai_model, temperature=settings.temperature, request_timeout=600.0)
                Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
                print(f"Initialized Local Processing Cluster: {settings.ai_model} via Ollama")
            
            # Connect to ChromaDB client instance
            db = chromadb.PersistentClient(path=DB_DIR)
            chroma_collection = db.get_or_create_collection(paths["collection_name"])
            
            # Read files only if they exist in the directory
            documents = []
            if sync_success and os.path.exists(paths["notes_dir"]):
                documents = SimpleDirectoryReader(paths["notes_dir"], required_exts=[".md"], recursive=True).load_data()
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index from user documents or load vectors if documents are empty but store exists
            if documents:
                index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            else:
                index = VectorStoreIndex.from_vector_store(vector_store)
                
            # Build an isolated contextual chat execution window
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
        
        # Execute chat sequence within the isolated sandbox
        response = _user_chat_engines[user.id].chat(user_query)
        return str(response)
        
    except Exception as e:
        print(f"Dedicated Multi-Tenant RAG Error: {str(e)}")
        return f"Core System Error: Failed to compute query maps inside your data matrix partition. Details: {str(e)}"