🤖 Qoshi AI — AI Portfolio Assistant with RAG & LLM

<img width="1536" height="1024" alt="ChatGPT Image Jul 20, 2026, 06_55_30 AM" src="https://github.com/user-attachments/assets/531d9d41-eaab-4a4a-a9d6-72405ec8f2af" />

An intelligent AI-powered portfolio assistant that allows visitors to interactively explore my background, experience, projects, technical skills, and certifications through natural conversation.

This project is built using **Retrieval-Augmented Generation (RAG)**, **Large Language Models (LLMs)**, **FastAPI**, and **ChromaDB**, with a custom hybrid retrieval pipeline designed for fast and accurate responses.

---

## 🚀 Live Demo

🌐 Portfolio Website

https://qoshi.framer.website/
---

## ✨ Features

- 🤖 AI-powered portfolio assistant
- 🔍 Retrieval-Augmented Generation (RAG)
- 🧠 Hybrid Retrieval
  - Category Detection
  - Keyword Search
  - Semantic Search
- 💬 Multi-turn conversation memory
- 🌍 Indonesian & English support
- ⚡ Optimized retrieval pipeline
- 📚 ChromaDB vector database
- 🚀 FastAPI REST API
- 🎨 Framer frontend integration
- ☁️ Railway deployment

---

# Architecture

```
                Visitor
                   │
                   ▼
        Framer Portfolio Website
                   │
                   ▼
         React Chat Component
                   │
                   ▼
            FastAPI Backend
                   │
        ┌──────────┴──────────┐
        │ Hybrid Retriever    │
        │─────────────────────│
        │ Category Detection  │
        │ Keyword Search      │
        │ Semantic Search     │
        └──────────┬──────────┘
                   │
          ChromaDB Vector Store
                   │
                   ▼
          Large Language Model
             (Llama / Gemini)
                   │
                   ▼
           Natural AI Response
```

---

# Tech Stack

### Frontend

- Framer
- React
- TypeScript

### Backend

- FastAPI
- Python

### AI

- Llama 3.1
- Gemini
- Sentence Transformers
- Retrieval-Augmented Generation (RAG)

### Database

- ChromaDB

### Deployment

- Railway
- GitHub

---

# Project Structure

```
backend/
│
├── app/
│   ├── chat_service.py
│   ├── retriever.py
│   ├── conversation.py
│   ├── detect_language.py
│   ├── llm_client.py
│   ├── session.py
│   ├── vector_store.py
│   └── ...
│
├── knowledge/
│
├── db/
│
├── ingest.py
├── main.py
└── requirements.txt
```

---

# Retrieval Pipeline

The chatbot uses a custom retrieval pipeline instead of relying on frameworks such as LangChain or LlamaIndex.

```
User Question
      │
      ▼
Category Detection
      │
      ▼
Keyword Search
      │
      ▼
Semantic Search
      │
      ▼
Context Builder
      │
      ▼
Prompt Builder
      │
      ▼
Large Language Model
      │
      ▼
AI Response
```

---

# Performance Optimizations

- Lazy loading embedding model
- Hybrid retrieval
- Query cache
- Category-first retrieval
- Keyword-first retrieval
- Semantic fallback
- Conversation memory
- Optimized prompt engineering
- Reduced token usage
- In-memory indexing

---

# Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
```

Go to project

```bash
cd backend
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```env
GROQ_API_KEY=YOUR_KEY

# or

GEMINI_API_KEY=YOUR_KEY
```

Run the application

```bash
uvicorn main:app --reload
```

API

```
POST /chat
```

Example

```json
{
    "session_id":"12345",
    "question":"Tell me about Qoshi."
}
```

---

# Example Questions

- Tell me about yourself.
- What projects have you built?
- What programming languages do you use?
- Tell me about your internship.
- How can I contact you?
- What AI technologies have you worked with?

---

# Future Improvements

- Voice conversation
- Streaming responses
- Better reranking
- Image retrieval
- Admin dashboard
- Knowledge auto-update
- Document upload
- Tool calling
- MCP integration

---

# Skills Demonstrated

- Retrieval-Augmented Generation (RAG)
- Large Language Models
- Prompt Engineering
- Vector Database
- Semantic Search
- Information Retrieval
- FastAPI
- REST API
- Python
- ChromaDB
- Sentence Transformers
- React
- TypeScript
- Framer
- Railway
- GitHub
- Backend Optimization

---

# License

This project is licensed under the MIT License.

---

# Author

**Qoshirotu Thorfi Gibran Yusuf**

LinkedIn  
https://linkedin.com/in/qoshirotu-thorfi

Portfolio  
https://YOUR-WEBSITE.com

GitHub  
https://github.com/YOUR_USERNAME
