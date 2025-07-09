"""
EU eTranslation API Service
Handles all communication with the EU eTranslation REST API
"""
import requests
from requests.auth import HTTPDigestAuth
import json
from datetime import datetime
from typing import Dict, Any, Optional
from config import config


class ETranslationService:
    """Service class for EU eTranslation API operations"""
    
    def __init__(self):
        self.rest_url = config.rest_url
        self.application_name = config.application_name
        self.email = config.email
        self.api_password = config.api_password
        
    def create_auth(self) -> HTTPDigestAuth:
        """Create HTTP Digest Authentication object"""
        return HTTPDigestAuth(self.application_name, self.api_password)
    
    def build_translation_request(self, 
                                source_language: str, 
                                target_language: str, 
                                text_to_translate: str, 
                                callback_url: str) -> Dict[str, Any]:
        """Build a translation request payload"""
        return {
            'sourceLanguage': source_language,
            'targetLanguages': [target_language],
            'callerInformation': {
                "application": self.application_name,
                "username": self.email
            },
            'textToTranslate': text_to_translate,
            'requesterCallback': callback_url
        }
    
    def submit_translation_request(self, 
                                 source_language: str, 
                                 target_language: str, 
                                 text_to_translate: str, 
                                 callback_url: str,
                                 timeout: int = 30) -> requests.Response:
        """Submit a translation request to the EU eTranslation API"""
        
        request_payload = self.build_translation_request(
            source_language, target_language, text_to_translate, callback_url
        )
        
        headers = {'Content-Type': 'application/json'}
        json_request = json.dumps(request_payload)
        
        return requests.post(
            self.rest_url,
            auth=self.create_auth(),
            headers=headers,
            data=json_request,
            timeout=timeout
        )
    
    def submit_test_request(self, callback_url: str, timeout: int = 30) -> requests.Response:
        """Submit a simple test request"""
        return self.submit_translation_request(
            source_language='EN',
            target_language='FR',
            text_to_translate='Hello',
            callback_url=callback_url,
            timeout=timeout
        )


# Global service instance
etranslation_service = ETranslationService()
