"""Data validation helpers."""


def is_plain_string(value):
    """
    Check if a value is a plain string (not dict, list, or other type).
    Used to guard against NoSQL injection attacks.
    
    Args:
        value: The value to check
        
    Returns:
        bool: True if value is a string, False otherwise
    """
    return isinstance(value, str)


def validate_password_length(password):
    """
    Validate password meets minimum length requirement.
    
    Args:
        password: The password to validate
        
    Returns:
        bool: True if password is at least 8 characters, False otherwise
    """
    return isinstance(password, str) and len(password) >= 8
