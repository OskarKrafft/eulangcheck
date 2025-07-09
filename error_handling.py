"""
Error handling and codes for EU eTranslation App
Centralized error management and user-friendly messages
"""

class ErrorCodes:
    """Standard error codes used throughout the application"""
    
    # Custom application errors
    EMPTY_TEXT = "-1001"
    MISSING_LANGUAGES = "-1002" 
    SAME_SOURCE_TARGET = "-1003"
    INVALID_RESPONSE = "-1004"
    NETWORK_ERROR = "-1005"
    UNEXPECTED_ERROR = "-1006"
    
    # EU eTranslation API specific errors (from documentation)
    CONCURRENCY_QUOTA_EXCEEDED = "-20028"
    AUTHENTICATION_FAILED = "-20001"
    INVALID_LANGUAGE_PAIR = "-20002"
    TEXT_TOO_LONG = "-20003"
    
    @staticmethod
    def get_error_message(error_code: str) -> str:
        """Get user-friendly error message for error code"""
        
        error_messages = {
            ErrorCodes.EMPTY_TEXT: "Please enter some text to translate.",
            ErrorCodes.MISSING_LANGUAGES: "Please select both source and target languages.",
            ErrorCodes.SAME_SOURCE_TARGET: "Source and target languages cannot be the same.",
            ErrorCodes.INVALID_RESPONSE: "Invalid response from translation service.",
            ErrorCodes.NETWORK_ERROR: "Network error. Please check your internet connection.",
            ErrorCodes.UNEXPECTED_ERROR: "An unexpected error occurred. Please try again.",
            ErrorCodes.CONCURRENCY_QUOTA_EXCEEDED: "Service is very busy. Please try again in a few minutes.",
            ErrorCodes.AUTHENTICATION_FAILED: "Authentication failed. Please check your API credentials.",
            ErrorCodes.INVALID_LANGUAGE_PAIR: "This language combination is not supported.",
            ErrorCodes.TEXT_TOO_LONG: "Text is too long. Please reduce the length and try again."
        }
        
        return error_messages.get(error_code, f"Error code: {error_code}")
    
    @staticmethod
    def is_error_code(response_text: str) -> bool:
        """Check if the response text is an error code (negative number)"""
        try:
            return int(response_text.strip()) < 0
        except ValueError:
            return False
    
    @staticmethod
    def is_success_code(response_text: str) -> bool:
        """Check if the response text is a success code (positive number)"""
        try:
            return int(response_text.strip()) > 0
        except ValueError:
            return False


def handle_api_response(response: str) -> tuple[str, bool]:
    """
    Handle API response and return (message, is_success)
    
    Args:
        response: Raw response text from API
        
    Returns:
        Tuple of (user_message, is_success_boolean)
    """
    response = response.strip()
    
    if ErrorCodes.is_success_code(response):
        return response, True
    elif ErrorCodes.is_error_code(response):
        message = ErrorCodes.get_error_message(response)
        return message, False
    else:
        return ErrorCodes.get_error_message(ErrorCodes.INVALID_RESPONSE), False
