# 🧠 S.A.T.O.R.I. AI

## ✨ Tagline

Awaken Intelligence. Automate Workflows. Empower Creation.

## 🌟 Overview

S.A.T.O.R.I. AI (System for Agentic Tasks, Orchestration, and Real-time Intelligence) is an advanced multi-agent AI platform designed to guide users through transformative journeys of self-discovery, alignment, and growth while streamlining personal and professional workflows.

## 🚀 Features

- 🤖 **Multi-Agent Orchestration**: Dynamic framework powered by LangGraph and LangChain
- ⚡ **Task Automation**: Streamline personal and professional workflows
- 🧠 **Real-Time Intelligence**: Immediate, actionable insights
- 🎯 **Multimodal Capabilities**: Support for text, voice, image, and video interactions
- 📚 **Integrated Knowledge Management**: AI-powered retrieval-augmented systems
- 🏗️ **Scalable Architecture**: Built with modern, robust technologies

## 🛠️ Tech Stack

- 🔧 **Backend**: FastAPI, LangChain, LangGraph
- 🎨 **Frontend**: Streamlit (POC phase)
- 💾 **Database**: ChromaDB, PostgreSQL with pgvector
- 👨‍💻 **Development**: Python 3.10+

## 🏁 Getting Started

### 📋 Prerequisites

- 🐍 Python 3.10 or higher
- 🗄️ PostgreSQL 14+ with pgvector extension
- 📦 Git

### ⚙️ Installation

1. 📥 Clone the repository:

```bash
git clone https://github.com/yourusername/SATORI-AI.git
cd SATORI-AI
```

1. 🔨 Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

1. 📦 Install dependencies:

```bash
pip install -r requirements.txt
```

1. 🔐 Set up environment variables:

```bash
# Copy the example environment file
cp .env.example .env
# Edit .env with your configuration
```

### 🚀 Running the Application

1. 🔧 Start the FastAPI backend:

```bash
# From the project root
cd backend/api
python main.py
```

1. 🎨 Start the Streamlit frontend (in a new terminal):

```bash
# From the project root
cd frontend
streamlit run app.py
```

📱 The application will be available at:

- 🌐 Frontend: <http://localhost:8501>
- ⚡ Backend API: <http://localhost:8000>
- 📚 API Documentation: <http://localhost:8000/docs>

## 📁 Project Structure

```curl
SATORI-AI/
├── backend/
│   ├── agents/      # 🤖 Multi-agent system components
│   ├── api/         # ⚡ FastAPI routes and endpoints
│   └── db/          # 💾 Database models and connections
├── frontend/
│   └── components/  # 🎨 Streamlit UI components
├── docs/
│   ├── api/         # 📚 API documentation
│   └── architecture/# 🏗️ System architecture docs
└── tests/
    ├── unit/        # 🧪 Unit tests
    └── integration/ # 🔄 Integration tests
```

## 👨‍💻 Development

### 🛠️ Setup Development Environment

1. 📦 Install development dependencies:

```bash
pip install -r requirements.txt
```

1. 🔧 Set up pre-commit hooks:

```bash
pre-commit install
```

### 🌿 Git Workflow

1. 🔄 Create a new branch for your feature:

```bash
git checkout -b feature/your-feature-name
```

1. 💾 Make your changes and commit:

```bash
git add .
git commit -m "Description of your changes"
```

1. 🚀 Push your changes:

```bash
git push origin feature/your-feature-name
```

1. 🔄 Create a Pull Request on GitHub

## 🤝 Contributing

1. 🔱 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m "Add some AmazingFeature"`)
4. 🚀 Push to the branch (`git push origin feature/AmazingFeature`)
5. 📬 Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💖 Acknowledgments

- 🌟 Built with ❤️ and powered by @hams_ollo
- 🧘 Inspired by the Zen concept of Satori - sudden enlightenment
