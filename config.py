"""
Configuration management for EU eTranslation App
Handles environment variables and settings
"""
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # Fallback if python-dotenv is not installed
    pass

class Config:
    """Application configuration loaded from environment variables"""
    
    def __init__(self):
        # python-dotenv will handle loading if available
        pass
    
    @property
    def application_name(self) -> str:
        """EU eTranslation application name"""
        value = os.getenv('ETRANSLATION_APPLICATION_NAME')
        if not value:
            raise ValueError("ETRANSLATION_APPLICATION_NAME environment variable is required")
        return value
    
    @property
    def email(self) -> str:
        """EU eTranslation registered email"""
        value = os.getenv('ETRANSLATION_EMAIL')
        if not value:
            raise ValueError("ETRANSLATION_EMAIL environment variable is required")
        return value
    
    @property
    def api_password(self) -> str:
        """EU eTranslation API password"""
        value = os.getenv('ETRANSLATION_API_PASSWORD')
        if not value:
            raise ValueError("ETRANSLATION_API_PASSWORD environment variable is required")
        return value
    
    @property
    def rest_url(self) -> str:
        """EU eTranslation REST API endpoint"""
        return os.getenv('ETRANSLATION_REST_URL', 'https://webgate.ec.europa.eu/etranslation/si/translate')
    
    @property
    def flask_host(self) -> str:
        """Flask host binding"""
        return os.getenv('FLASK_HOST', '0.0.0.0')
    
    @property
    def flask_port(self) -> int:
        """Flask port"""
        return int(os.getenv('FLASK_PORT', '5001'))
    
    @property
    def flask_debug(self) -> bool:
        """Flask debug mode"""
        return os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes', 'on')
    
    def validate(self) -> bool:
        """Validate that all required configuration is present"""
        try:
            # Access all required properties to trigger validation
            self.application_name
            self.email
            self.api_password
            return True
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            return False

# Global config instance
config = Config()
