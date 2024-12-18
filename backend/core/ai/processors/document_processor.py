"""
Document processing pipeline for SATORI AI.
Handles document loading, text extraction, and chunking.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from langchain.document_loaders import (
    TextLoader, PDFLoader, Docx2txtLoader,
    UnstructuredMarkdownLoader, JSONLoader,
    CSVLoader, UnstructuredHTMLLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from ..config import ai_settings, SUPPORTED_DOCUMENT_TYPES

# Set up logging
logger = logging.getLogger("satori.document_processor")

class DocumentProcessor:
    """Handles document processing pipeline"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=ai_settings.chunk_size,
            chunk_overlap=ai_settings.chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        
        # Map file extensions to appropriate loaders
        self.loader_map = {
            ".txt": TextLoader,
            ".pdf": PDFLoader,
            ".doc": Docx2txtLoader,
            ".docx": Docx2txtLoader,
            ".md": UnstructuredMarkdownLoader,
            ".json": JSONLoader,
            ".csv": CSVLoader,
            ".html": UnstructuredHTMLLoader
        }
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document from file path
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of Document objects
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in SUPPORTED_DOCUMENT_TYPES:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        try:
            logger.info(f"Loading document: {file_path}")
            loader = self.loader_map[path.suffix.lower()](file_path)
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def process_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Process raw text into chunks
        
        Args:
            text: Raw text to process
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of Document objects
        """
        try:
            logger.info("Processing text input")
            doc = Document(page_content=text, metadata=metadata or {})
            return self.text_splitter.split_documents([doc])
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            raise
    
    def process_document(self, file_path: str) -> List[Document]:
        """
        Process a document through the complete pipeline
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of processed Document chunks
        """
        try:
            # Load the document
            docs = self.load_document(file_path)
            
            # Split into chunks
            logger.info(f"Splitting document into chunks: {file_path}")
            chunks = self.text_splitter.split_documents(docs)
            
            # Add source metadata
            for chunk in chunks:
                chunk.metadata["source"] = file_path
                chunk.metadata["chunk_size"] = len(chunk.page_content)
            
            logger.info(f"Successfully processed document into {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Error in document processing pipeline: {str(e)}")
            raise
    
    def batch_process(self, file_paths: List[str]) -> List[Document]:
        """
        Process multiple documents
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of processed Document chunks
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                chunks = self.process_document(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue
        
        return all_chunks 