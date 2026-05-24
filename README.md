Second Brain AI

Second Brain AI is a personal workspace combining an Obsidian-style knowledge base, a Kanban task tracker, and a local AI assistant based on RAG (Retrieval-Augmented Generation).

The project is focused on complete privacy: the artificial intelligence runs locally on your hardware, analyzes your synchronized Markdown notes, and answers questions strictly based on your personal knowledge base without sending any data to external servers.

Key Features:
- Local AI Assistant: Built on LlamaIndex and ChromaDB. Connects to Ollama (supporting Llama 3 and Phi 3 models) for autonomous offline operation.
- Obsidian Synchronization: Secure connection to private GitHub repositories using Personal Access Tokens (PAT). Tokens are encrypted in the database using the AES-128 algorithm (via the cryptography/Fernet library).
- Note Viewer: Fast navigation through Markdown files without page reloads (SPA). Fully supports Obsidian WikiLinks ([[Note Title]]) and automatic Backlinks generation.
- Task Manager: Kanban task board with To Do, In Progress, and Done statuses, featuring priority and tag filtering.
- Themes: Responsive interface supporting both dark and light themes, along with customizable accent colors.
- Multi-Tenant Architecture: Each account is isolated at the database level, has its own settings, and gets a personal directory for storing notes.

Tech Stack:
- Backend: Python, Django, SQLite
- AI Components: LlamaIndex, ChromaDB, Ollama (local LLMs and embeddings)
- Frontend: HTML5, Vanilla JavaScript, Tailwind CSS v4 CLI
- Security: python-dotenv for environment variables, cryptography for DB token encryption

Prerequisites:
To run the project, you need:
1. Python 3.10 or higher
2. Node.js (for compiling Tailwind CSS v4 styles)
3. Ollama with downloaded models

Before starting the application, run the following commands in your terminal:
ollama run llama3
or
ollama run phi3

Note: The nomic-embed-text embedding model will download automatically during the first indexing of the note base.

Installation and Setup:

1. Clone the repository and navigate to the working directory:
git clone https://github.com/yourusername/second_brain_ai.git
cd second_brain_ai/ai_manager

2. Create and activate a virtual environment:
python -m venv venv
For Windows:
venv\Scripts\activate
For Mac/Linux:
source venv/bin/activate

3. Install backend dependencies:
pip install django llama-index llama-index-vector-stores-chroma llama-index-embeddings-ollama llama-index-llms-ollama chromadb gitpython markdown cryptography python-dotenv

4. Create a .env file in the ai_manager folder (next to manage.py) and set the core variables:
SECRET_KEY=your-super-secret-django-key-here
DEBUG=True

5. Install frontend dependencies:
npm install

6. Apply database migrations and create a superuser:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

Running the Application:

For Windows, there is a ready-made script for automatically starting all modules:
run_matrix.bat

For manual startup, open two separate terminals with the activated venv environment:
- Terminal 1 (Django Server):
  python manage.py runserver
- Terminal 2 (Tailwind Compiler):
  npm run dev

After that, the web interface will be available at: http://127.0.0.1:8000

First Run and Indexing:
1. Register an account or log in with the superuser credentials.
2. Navigate to the Settings section.
3. Provide the URL of your private GitHub repository containing your Obsidian notes and your Personal Access Token (PAT).
4. Select the local model you want to use (Llama 3 or Phi 3) and save the settings.
5. Go to the Notes or AI Chat section. The system will automatically clone the repository, start indexing, and create a local vector database in ChromaDB.
