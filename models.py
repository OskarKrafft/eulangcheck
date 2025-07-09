"""
Data models for EU eTranslation App
Clean data structures for better organization
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TranslationStatus(Enum):
    """Translation request status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TranslationRequest:
    """Data class for translation request information"""
    request_id: str
    source_language: str
    target_language: str
    original_text: str
    timestamp: datetime
    status: TranslationStatus = TranslationStatus.PENDING
    translation: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'request_id': self.request_id,
            'source_language': self.source_language,
            'target_language': self.target_language,
            'original_text': self.original_text,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'translation': self.translation,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'has_translation': bool(self.translation),
            'original_text_length': len(self.original_text),
            'translation_length': len(self.translation) if self.translation else 0
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationRequest':
        """Create instance from dictionary"""
        return cls(
            request_id=data['request_id'],
            source_language=data['source_language'],
            target_language=data['target_language'],
            original_text=data['original_text'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            status=TranslationStatus(data.get('status', 'pending')),
            translation=data.get('translation'),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            duration_seconds=data.get('duration_seconds'),
            error_message=data.get('error_message')
        )
    
    def mark_completed(self, translation: str):
        """Mark translation as completed with result"""
        self.status = TranslationStatus.COMPLETED
        self.translation = translation
        self.completed_at = datetime.now()
        if self.completed_at:
            self.duration_seconds = (self.completed_at - self.timestamp).total_seconds()
    
    def mark_failed(self, error_message: str):
        """Mark translation as failed with error"""
        self.status = TranslationStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()


class TranslationStore:
    """In-memory store for translation requests"""
    
    def __init__(self):
        self._store: Dict[str, TranslationRequest] = {}
    
    def add_request(self, request: TranslationRequest):
        """Add a new translation request"""
        self._store[request.request_id] = request
    
    def get_request(self, request_id: str) -> Optional[TranslationRequest]:
        """Get a translation request by ID"""
        return self._store.get(request_id)
    
    def update_request(self, request_id: str, **updates):
        """Update a translation request"""
        if request_id in self._store:
            request = self._store[request_id]
            for key, value in updates.items():
                if hasattr(request, key):
                    setattr(request, key, value)
    
    def get_all_requests(self) -> Dict[str, TranslationRequest]:
        """Get all translation requests"""
        return self._store.copy()
    
    def get_pending_requests(self) -> Dict[str, TranslationRequest]:
        """Get all pending translation requests"""
        return {
            req_id: req for req_id, req in self._store.items() 
            if req.status == TranslationStatus.PENDING
        }
    
    def get_completed_requests(self) -> Dict[str, TranslationRequest]:
        """Get all completed translation requests"""
        return {
            req_id: req for req_id, req in self._store.items() 
            if req.status == TranslationStatus.COMPLETED
        }
    
    def cleanup_old_requests(self, max_age_hours: int = 24):
        """Remove requests older than specified hours"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = [
            req_id for req_id, req in self._store.items()
            if req.timestamp < cutoff_time
        ]
        for req_id in to_remove:
            del self._store[req_id]
        return len(to_remove)


# Global translation store instance
translation_store = TranslationStore()
