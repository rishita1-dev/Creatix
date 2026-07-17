

---

# 🚀 Creatix

> *An Autonomous AI Coding Assistant that streamlines software development by leveraging Large Language Models, GitHub integration, and Retrieval-Augmented Generation (RAG) to generate, explain, debug, review, and understand code repositories.*

---

# 📖 About Creatix

Explain what the project is, why it exists, and what problem it solves.

---

# ✨ Features

* 💻 AI Code Generation
* 📚 Code Explanation
* 🐞 Intelligent Code Debugging
* 🔍 GitHub Repository Review
* 🤖 Repository Q&A using RAG
* ⚡ FastAPI Backend
* 🎨 Streamlit Web Interface
  

---

# 🏗️ System Architecture





```
                    USER
                      │
                      ▼
             Streamlit Frontend
                      │
             HTTP REST Requests
                      │
                      ▼
              FastAPI Backend
                      │
               Request Router
                      │
      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼
 Code Generator   Code Explainer   Debugger
      │               │                │
      └───────────────┼────────────────┘
                      │
              Google Gemini API
                      │
                      ▼
               Generated Response

                      │

          GitHub Review Flow

GitHub URL
      │
      ▼
 GitHub API
      │
 Repository Loader
      │
 Repository Reviewer
      │
 Gemini
      │
 Review Report

                      │

          Repository Q&A Flow

GitHub URL
      │
      ▼
 Repository Loader
      │
 Code Chunker
      │
 Embedding Generator
      │
 Vector Store (FAISS/Chroma)
      │
 Similarity Search
      │
 Relevant Chunks
      │
 Gemini
      │
 Repository Answer
```

This is much stronger than a simple flowchart.

---

# ⚙️ Tech Stack

| Category                           | Technologies               |
| ---------------------------------- | -------------------------- |
| **Frontend**                       | Streamlit                  |
| **Backend**                        | FastAPI, Uvicorn           |
| **Programming Language**           | Python                     |
| **LLM**                            | Google Gemini API          |
| **Repository Access**              | GitHub API (PyGithub)      |
| **Retrieval-Augmented Generation** | FAISS/Chroma, Embeddings   |
| **Vector Search**                  | Semantic Similarity Search |
| **Environment Management**         | python-dotenv              |
| **Version Control**                | Git, GitHub                |

---

# 📂 Project Structure

```
Creatix/
│
├── agents/
├── backend/
├── frontend/
├── github_tools/
├── rag/
├── tests/
├── requirements.txt
└── README.md
```

---

# 🔄 Workflow

Explain the complete workflow from user input to AI response.

Example:

1. User selects a task.
2. Frontend sends request to FastAPI.
3. Backend validates input.
4. Agent Router selects the appropriate AI agent.
5. GitHub API/RAG is invoked when required.
6. Gemini generates the response.
7. Response is returned to the frontend.

---

# 🚀 Installation

* Clone repository
* Create virtual environment
* Install dependencies
* Configure `.env`
* Run FastAPI
* Run Streamlit

---

# 🔑 Environment Variables

```env
GOOGLE_API_KEY=your_api_key
GITHUB_TOKEN=your_token
```

---

# 🎯 Future Advancements

* Multi-LLM Support (OpenAI, Claude, Groq)
* Docker Deployment
* CI/CD Integration
* Authentication & User Profiles
* PDF Code Review Reports
* Real-Time Code Collaboration
* Voice-Based AI Assistant
* Multi-Language Code Support
* Code Execution Sandbox
* Automated Test Case Generation

---

# 🤝 Team

**Team Name:** **Creatix**

**Team Members:**

* Purnima Rathi
* Rishita
* Ranya Ritsika
* Vanshika Bajaj
* Pankhuri Agrawal 

---

# ⭐ Acknowledgements

* Google Gemini API
* FastAPI
* Streamlit
* GitHub API
* FAISS/Chroma
* Python Community

---

