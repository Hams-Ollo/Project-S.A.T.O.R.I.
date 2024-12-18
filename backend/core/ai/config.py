"""
Configuration settings for SATORI AI components.
"""
from typing import Dict, List
from pydantic import BaseSettings, Field

class AISettings(BaseSettings):
    """AI Component Configuration"""
    
    # Llama Settings
    llama_api_url: str = Field("http://localhost:8080", env='LLAMA_API_URL')
    llama_model: str = Field("llama-3.3-70b-versatile", env='LLAMA_MODEL')
    embedding_model: str = Field("llama-3.3-70b-versatile", env='EMBEDDING_MODEL')
    
    # ChromaDB Settings
    chroma_db_dir: str = Field("data/chromadb", env='CHROMA_DB_DIR')
    collection_name: str = Field("satori_knowledge", env='COLLECTION_NAME')
    
    # Document Processing
    chunk_size: int = Field(1000, env='CHUNK_SIZE')
    chunk_overlap: int = Field(200, env='CHUNK_OVERLAP')
    
    # Memory Settings
    memory_window_size: int = Field(5, env='MEMORY_WINDOW_SIZE')
    max_token_limit: int = Field(4000, env='MAX_TOKEN_LIMIT')
    
    # Agent Settings
    agent_temperature: float = Field(0.7, env='AGENT_TEMPERATURE')
    max_iterations: int = Field(5, env='MAX_ITERATIONS')
    
    # Agent Roles and Descriptions
    agent_roles: Dict[str, str] = {
        "discovery": "Self-reflection and personal growth guide",
        "task": "Task automation and workflow optimization",
        "knowledge": "Information retrieval and knowledge management",
        "mentor": "Guidance and strategic planning"
    }
    
    # Agent Prompts
    system_prompts: Dict[str, str] = {
        "discovery": """You are the Discovery Agent, focused on helping users achieve personal growth and self-discovery.
Your role is to guide introspection, identify patterns, and facilitate transformative insights.""",
        
        "task": """You are the Task Agent, specialized in workflow optimization and automation.
Your role is to help users streamline their processes and achieve maximum efficiency.""",
        
        "knowledge": """You are the Knowledge Agent, responsible for information retrieval and knowledge management.
Your role is to help users organize, understand, and leverage their information effectively.""",
        
        "mentor": """You are the Mentor Agent, providing guidance and strategic planning support.
Your role is to help users develop long-term strategies and make informed decisions."""
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Initialize settings
ai_settings = AISettings()

# Logging configuration for AI components
LOGGING_CONFIG = {
    "ai_logger": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

# Token limits for different models
TOKEN_LIMITS = {
    "llama-3.3-70b-versatile": 4096,
}

# Supported document types for ingestion
SUPPORTED_DOCUMENT_TYPES = [
    ".txt", ".pdf", ".doc", ".docx", 
    ".md", ".json", ".csv", ".html"
] 