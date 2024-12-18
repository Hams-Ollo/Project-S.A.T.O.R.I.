"""
Embedding manager for SATORI AI.
Handles document embedding generation and vector storage.
"""

from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

from ..config import ai_settings
from ..processors.document_processor import DocumentProcessor

# Set up logging
logger = logging.getLogger("satori.embedding_manager")

class EmbeddingManager:
    """Manages document embeddings and vector storage"""
    
    def __init__(self):
        """Initialize embedding manager with OpenAI embeddings and ChromaDB"""
        self.embeddings = OpenAIEmbeddings(
            model=ai_settings.embedding_model,
            openai_api_key=ai_settings.openai_api_key
        )
        
        # Ensure vector store directory exists
        Path(ai_settings.chroma_db_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize vector store
        self.vector_store = Chroma(
            collection_name=ai_settings.collection_name,
            embedding_function=self.embeddings,
            persist_directory=ai_settings.chroma_db_dir
        )
        
        self.document_processor = DocumentProcessor()
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of Document objects to add
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            logger.info("Successfully added documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> None:
        """
        Add raw texts to vector store
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts
        """
        try:
            logger.info(f"Adding {len(texts)} texts to vector store")
            self.vector_store.add_texts(texts, metadatas=metadatas)
            self.vector_store.persist()
            logger.info("Successfully added texts to vector store")
        except Exception as e:
            logger.error(f"Error adding texts to vector store: {str(e)}")
            raise
    
    def process_and_store_document(self, file_path: str) -> None:
        """
        Process a document and store its chunks in the vector store
        
        Args:
            file_path: Path to the document to process
        """
        try:
            # Process the document
            chunks = self.document_processor.process_document(file_path)
            
            # Store the chunks
            self.add_documents(chunks)
            
            logger.info(f"Successfully processed and stored document: {file_path}")
        except Exception as e:
            logger.error(f"Error processing and storing document: {str(e)}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents
        """
        try:
            logger.info(f"Performing similarity search for query: {query}")
            results = self.vector_store.similarity_search(
                query,
                k=k,
                filter=filter
            )
            logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        try:
            logger.info(f"Performing scored similarity search for query: {query}")
            results = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=filter
            )
            logger.info(f"Found {len(results)} scored documents")
            return results
        except Exception as e:
            logger.error(f"Error during scored similarity search: {str(e)}")
            raise
    
    def delete_collection(self) -> None:
        """Delete the entire vector store collection"""
        try:
            logger.warning("Deleting entire vector store collection")
            self.vector_store.delete_collection()
            self.vector_store = Chroma(
                collection_name=ai_settings.collection_name,
                embedding_function=self.embeddings,
                persist_directory=ai_settings.chroma_db_dir
            )
            logger.info("Successfully deleted and reinitialized collection")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise 