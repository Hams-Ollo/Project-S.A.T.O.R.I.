from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import uuid4

class MessageType(str, Enum):
    CHAT = "chat"
    SYSTEM = "system"
    FILE = "file"
    ERROR = "error"

class MessageStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    ERROR = "error"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType
    content: str
    sender_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.PENDING
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatMessage(Message):
    type: MessageType = MessageType.CHAT
    reply_to: Optional[str] = None
    agent_id: Optional[str] = None

class SystemMessage(Message):
    type: MessageType = MessageType.SYSTEM
    severity: str = "info"

class FileMessage(Message):
    type: MessageType = MessageType.FILE
    file_name: str
    file_type: str
    file_size: int
    file_url: Optional[str] = None 