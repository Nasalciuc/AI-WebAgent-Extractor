"""
Centralized environment configuration loader for AI-WebAgent-Extractor
Standardizes loading of API keys and configuration across all modules.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import logging

# Try to import python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv(*args, **kwargs):
        pass

# Try to import streamlit for secrets
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Configure logging
logger = logging.getLogger(__name__)

class EnvironmentConfig:
    """Centralized environment configuration management"""
    
    def __init__(self):
        """Initialize environment configuration loader"""
        # Load environment variables from various sources
        self._load_environment_files()
        
        # Cache for loaded values
        self._cache = {}
        
    def _load_environment_files(self):
        """Load environment files from multiple possible locations"""
        if not DOTENV_AVAILABLE:
            logger.warning("python-dotenv not available. Using system environment only.")
            return
            
        # Find project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Possible .env file locations (in order of priority)
        env_locations = [
            project_root / "config" / ".env",      # Primary location
            project_root / ".env",                 # Root level
            current_dir / ".env",                  # Config directory
            project_root / "AI-WebAgent-Extractor" / ".env",  # Legacy location
        ]
        
        # Load each .env file that exists
        for env_path in env_locations:
            if env_path.exists():
                logger.info(f"Loading environment from: {env_path}")
                load_dotenv(env_path, override=False)  # Don't override already set variables
            else:
                logger.debug(f"Environment file not found: {env_path}")
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """
        Get API key from environment with multiple fallback sources
        
        Args:
            key_name: Name of the environment variable (e.g., 'OPENAI_API_KEY')
            
        Returns:
            API key string or None if not found
        """
        # Check cache first
        if key_name in self._cache:
            return self._cache[key_name]
            
        # 1. Environment variables (highest priority)
        key_value = os.getenv(key_name)
        if key_value:
            self._cache[key_name] = key_value
            logger.debug(f"Found {key_name} in environment variables")
            return key_value
        
        # 2. Streamlit secrets (if available)
        if STREAMLIT_AVAILABLE and st and hasattr(st, 'secrets'):
            try:
                key_value = st.secrets.get(key_name)
                if key_value:
                    self._cache[key_name] = key_value
                    logger.debug(f"Found {key_name} in Streamlit secrets")
                    return key_value
            except Exception as e:
                logger.debug(f"Error accessing Streamlit secrets: {e}")
        
        # 3. Not found
        logger.warning(f"API key '{key_name}' not found in any configuration source")
        return None
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return self.get_api_key("OPENAI_API_KEY")
    
    def get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key"""
        return self.get_api_key("GEMINI_API_KEY")
    
    def get_semrush_api_key(self) -> Optional[str]:
        """Get SEMrush API key"""
        return self.get_api_key("SEMRUSH_API_KEY")
    
    def get_similarweb_api_key(self) -> Optional[str]:
        """Get SimilarWeb API key"""
        return self.get_api_key("SIMILARWEB_API_KEY")
    
    def get_ai_provider(self) -> str:
        """
        Get preferred AI provider
        
        Returns:
            'openai', 'gemini', or 'auto'
        """
        provider = os.getenv("AI_PROVIDER", "auto").lower()
        if provider not in ["openai", "gemini", "auto"]:
            logger.warning(f"Invalid AI_PROVIDER '{provider}', defaulting to 'auto'")
            return "auto"
        return provider
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get scraping configuration parameters"""
        return {
            "default_delay": int(os.getenv("DEFAULT_DELAY", "2")),
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "max_workers": int(os.getenv("MAX_WORKERS", "5")),
        }
    
    def select_ai_provider(self) -> tuple[Optional[str], Optional[str]]:
        """
        Select best available AI provider based on available keys
        
        Returns:
            Tuple of (provider_name, api_key) or (None, None) if no provider available
        """
        preference = self.get_ai_provider()
        
        openai_key = self.get_openai_api_key()
        gemini_key = self.get_gemini_api_key()
        
        if preference == "openai" and openai_key:
            return ("openai", openai_key)
        elif preference == "gemini" and gemini_key:
            return ("gemini", gemini_key)
        elif preference == "auto":
            # Auto-select based on availability (prefer Gemini if both available)
            if gemini_key:
                return ("gemini", gemini_key)
            elif openai_key:
                return ("openai", openai_key)
        
        logger.error(f"No API key available for preferred provider '{preference}'")
        return (None, None)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration and return status
        
        Returns:
            Dictionary with validation results
        """
        status = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "available_providers": [],
            "config": {}
        }
        
        # Check API keys
        openai_key = self.get_openai_api_key()
        gemini_key = self.get_gemini_api_key()
        
        if openai_key:
            status["available_providers"].append("openai")
        if gemini_key:
            status["available_providers"].append("gemini")
            
        if not openai_key and not gemini_key:
            status["valid"] = False
            status["errors"].append("No AI API keys configured (OPENAI_API_KEY or GEMINI_API_KEY required)")
        
        # Check optional keys
        semrush_key = self.get_semrush_api_key()
        similarweb_key = self.get_similarweb_api_key()
        
        if not semrush_key:
            status["warnings"].append("SEMrush API key not configured (traffic analysis will be limited)")
        if not similarweb_key:
            status["warnings"].append("SimilarWeb API key not configured (traffic analysis will be limited)")
        
        # Get configuration
        status["config"] = {
            "ai_provider": self.get_ai_provider(),
            "scraping_config": self.get_scraping_config(),
            "selected_provider": self.select_ai_provider()[0]
        }
        
        return status

# Global instance
_env_config = None

def get_environment_config() -> EnvironmentConfig:
    """Get global environment configuration instance"""
    global _env_config
    if _env_config is None:
        _env_config = EnvironmentConfig()
    return _env_config

# Convenience functions for backward compatibility
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key (backward compatibility)"""
    return get_environment_config().get_openai_api_key()

def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key"""
    return get_environment_config().get_gemini_api_key()

def select_ai_provider() -> tuple[Optional[str], Optional[str]]:
    """Select best available AI provider"""
    return get_environment_config().select_ai_provider()

def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration"""
    return get_environment_config().validate_configuration()

if __name__ == "__main__":
    # Test configuration loading
    print("=== Environment Configuration Test ===")
    
    config = get_environment_config()
    validation = validate_environment()
    
    print(f"Configuration valid: {validation['valid']}")
    print(f"Available providers: {validation['available_providers']}")
    print(f"Selected provider: {validation['config']['selected_provider']}")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['errors']:
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    print(f"Scraping config: {validation['config']['scraping_config']}")