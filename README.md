# 🧠 Second Brain AI - Knowledge Matrix

![UI Theme](https://img.shields.io/badge/UI-Cyberpunk%20%2F%20Glassmorphism-00F0FF?style=flat-square)
![Django](https://img.shields.io/badge/Backend-Django-092E20?style=flat-square&logo=django)
![AI](https://img.shields.io/badge/AI%20Core-LlamaIndex%20%7C%20Ollama-B026FF?style=flat-square)
![Tailwind](https://img.shields.io/badge/CSS-Tailwind_v4-38B2AC?style=flat-square&logo=tailwind-css)

Second Brain AI is a modern, multi-tenant personal workspace that integrates a Kanban task manager, a dynamic Obsidian-style knowledge base, and a local AI Assistant (RAG system). 

The AI acts as your personal secure tutor, reading your synchronized GitHub notes and answering queries based *strictly* on your private data vault. Designed with a sleek, responsive Cyberpunk/Glassmorphism interface.

## ✨ Key Features

- **Isolated Multi-Tenant Architecture:** Each user has their own database rows, secure settings, and isolated file directories for their notes.
- **RAG AI Engine:** Powered by `LlamaIndex` and `ChromaDB`. Connects to a local `Ollama` instance (Llama 3 / Phi 3) for completely private, offline LLM inference.
- **GitHub Vault Sync:** Securely connects to your private Obsidian repositories using Personal Access Tokens (encrypted in the database using AES-128).
- **Advanced Notes Explorer (SPA):** Seamlessly navigate your Markdown notes without page reloads. Includes support for Obsidian WikiLinks (`[[Note]]`) and dynamic Backlinks (Linked Mentions).
- **Kanban Task Matrix:** Track active projects, priorities, and deadlines.
- **Secret Admin Dashboard:** A hidden, global control matrix for superusers to manage database entities securely.
- **Modern Build System:** Lightning-fast styling powered by the latest zero-config Tailwind CSS v4 CLI.

## 🛠️ Technology Stack

- **Backend:** Python 3, Django, SQLite
- **AI Core:** LlamaIndex, ChromaDB, Ollama (Local LLMs)
- **Frontend:** HTML5, Vanilla JavaScript (ES6+), Tailwind CSS v4
- **Security:** `python-dotenv` for secrets, `cryptography` (Fernet) for token encryption.

---

## 🚀 Getting Started

Follow these instructions to set up the project on your local machine.

### Prerequisites

You must have the following installed on your system:
1. **[Python 3.10+](https://www.python.org/downloads/)**
2. **[Node.js (LTS)](https://nodejs.org/)** (Required for Tailwind CSS compilation)
3. **[Ollama](https://ollama.com/)** (Required for local AI models)
4. Git

Before running the app, pull your preferred AI model via Ollama in your terminal:
```bash
ollama run llama3
# or
ollama run phi3
```

### Installation
**1. Clone the repository**

```Bash
git clone [https://github.com/yourusername/second_brain_ai.git](https://github.com/yourusername/second_brain_ai.git)
cd second_brain_ai/ai_manager
```
**2. Set up the Python Virtual Environment**

```Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install backend dependencies (Make sure to create a requirements.txt or install packages manually)
pip install django llama-index llama-index-vector-stores-chroma llama-index-embeddings-ollama llama-index-llms-ollama chromadb gitpython markdown cryptography python-dotenv
```

**3. Set up Environment Variables**
Create a `.env` file in the same directory as `manage.py` and add your secure configurations:

```Code snippet
SECRET_KEY=your-super-secret-django-key-here
DEBUG=True
```

**4. Install Frontend Dependencies (Tailwind v4)**

```Bash
npm install
```

**5. Initialize the Database**
Apply migrations to build the SQLite database and create a superuser for the Admin Dashboard.

```Bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## ⚡ Running the Application
Because this project uses a modern frontend build system alongside Django, you need to run two separate terminal windows during development.

**Terminal 1: Start the Django Backend**

```Bash
# Make sure your venv is activated
python manage.py runserver
```

**Terminal 2: Start the Tailwind CSS Watcher**

```Bash
# This will watch your HTML/JS files and instantly compile CSS changes
npm run dev
```
Open your browser and navigate to `http://127.0.0.1:8000`.

*(Note: When deploying to production, run `npm run build` instead of `npm run dev` to minify the CSS).*

## ⚙️ Configuration & Usage
**1. Create an Account:** Register a new user or log in with your superuser account.

**2. Configure Settings:** Go to the "Settings" tab.

**3. Connect GitHub:** Enter your Private GitHub Repository HTTPS URL (e.g., `https://github.com/username/my-obsidian-vault.git`) and your GitHub Personal Access Token (PAT) with repo scope.

**4. Sync:** Navigate to the "Notes" or "AI Chat" tab. The system will automatically clone your vault into an isolated secure folder and build the ChromaDB vector embeddings.

**5. Ask the AI:** Open Terminal Chat and start asking questions about your personal data!

## 🛡️ Security Notes
1. Never commit your `.env` file or `db.sqlite3` to version control.

2. GitHub tokens are encrypted at rest in the SQLite database using your `.env` `SECRET_KEY`.

*Developed as a next-generation personal knowledge management tool.*
