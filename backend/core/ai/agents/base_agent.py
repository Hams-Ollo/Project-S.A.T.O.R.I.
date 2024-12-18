"""
Base agent class for SATORI AI.
Provides common functionality for all specialized agents.
"""

from typing import List, Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage
)

from ..config import ai_settings
from ..embeddings.embedding_manager import EmbeddingManager

# Set up logging
logger = logging.getLogger("satori.base_agent")

class BaseAgent(ABC):
    """Base class for all SATORI AI agents"""
    
    def __init__(
        self,
        agent_type: str,
        embedding_manager: Optional[EmbeddingManager] = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        """
        Initialize base agent
        
        Args:
            agent_type: Type of agent (discovery, task, knowledge, mentor)
            embedding_manager: Optional embedding manager instance
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
        """
        if agent_type not in ai_settings.agent_roles:
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        self.agent_type = agent_type
        self.role = ai_settings.agent_roles[agent_type]
        self.system_prompt = ai_settings.system_prompts[agent_type]
        
        # Initialize chat model
        self.llm = ChatOpenAI(
            model=ai_settings.chat_model,
            temperature=temperature or ai_settings.agent_temperature,
            max_tokens=max_tokens or ai_settings.max_token_limit,
            openai_api_key=ai_settings.openai_api_key
        )
        
        # Initialize embedding manager if provided
        self.embedding_manager = embedding_manager
        
        # Initialize conversation history
        self.conversation_history: List[BaseMessage] = [
            SystemMessage(content=self.system_prompt)
        ]
        
        logger.info(f"Initialized {agent_type} agent")
    
    def add_message(self, message: str, is_human: bool = True) -> None:
        """
        Add a message to the conversation history
        
        Args:
            message: Message content
            is_human: Whether the message is from a human
        """
        message_obj = HumanMessage(content=message) if is_human else AIMessage(content=message)
        self.conversation_history.append(message_obj)
        
        # Trim history if needed
        self._trim_history()
    
    def _trim_history(self) -> None:
        """Trim conversation history to prevent token overflow"""
        if len(self.conversation_history) > ai_settings.memory_window_size:
            # Keep system prompt and last N messages
            self.conversation_history = [
                self.conversation_history[0],  # System prompt
                *self.conversation_history[-ai_settings.memory_window_size:]
            ]
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """
        Get relevant context from vector store
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            Relevant context as string
        """
        if not self.embedding_manager:
            return ""
        
        try:
            results = self.embedding_manager.similarity_search(query, k=k)
            context = "\n\n".join(doc.page_content for doc in results)
            return f"\nRelevant context:\n{context}\n"
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return ""
    
    @abstractmethod
    async def process_message(self, message: str) -> str:
        """
        Process a message and generate a response
        
        Args:
            message: Input message
            
        Returns:
            Agent's response
        """
        pass
    
    async def _generate_response(self, message: str, include_context: bool = True) -> str:
        """
        Generate a response using the LLM
        
        Args:
            message: Input message
            include_context: Whether to include relevant context
            
        Returns:
            Generated response
        """
        try:
            # Add user message to history
            self.add_message(message, is_human=True)
            
            # Get relevant context if needed
            context = self.get_relevant_context(message) if include_context else ""
            
            # Generate response
            if context:
                enhanced_message = f"{message}\n{context}"
                self.conversation_history[-1] = HumanMessage(content=enhanced_message)
            
            response = await self.llm.agenerate(
                messages=[self.conversation_history]
            )
            
            # Extract and store response
            response_text = response.generations[0][0].text
            self.add_message(response_text, is_human=False)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history in a structured format
        
        Returns:
            List of message dictionaries
        """
        return [
            {
                "role": "system" if isinstance(msg, SystemMessage) else
                       "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content
            }
            for msg in self.conversation_history
        ] 