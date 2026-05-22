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
