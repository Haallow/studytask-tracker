#!/usr/bin/env python
"""Verify authentication module functionality."""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.models import is_plain_string, validate_password_length

def test_models():
    """Test validation helpers."""
    print("Testing validation helpers...")
    
    # Test is_plain_string
    assert is_plain_string("test") == True, "String should be valid"
    assert is_plain_string({"key": "value"}) == False, "Dict should be invalid"
    assert is_plain_string(["list"]) == False, "List should be invalid"
    assert is_plain_string(123) == False, "Number should be invalid"
    print("✓ is_plain_string works correctly")
    
    # Test validate_password_length
    assert validate_password_length("12345678") == True, "8 char password should be valid"
    assert validate_password_length("1234567") == False, "7 char password should be invalid"
    assert validate_password_length("verylongpassword") == True, "Long password should be valid"
    assert validate_password_length(12345678) == False, "Non-string should be invalid"
    print("✓ validate_password_length works correctly")

def test_routes():
    """Test that routes are registered."""
    print("\nTesting routes registration...")
    
    from app import create_app
    app = create_app()
    
    # Get list of routes
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': str(rule)
            })
    
    print(f"\nRegistered routes:")
    for route in sorted(routes, key=lambda x: x['path']):
        print(f"  {route['methods']} {route['path']} -> {route['endpoint']}")
    
    # Verify expected routes exist
    expected_routes = [
        ('/health', ['GET']),
        ('/register', ['POST']),
        ('/login', ['POST']),
        ('/logout', ['POST']),
        ('/me', ['GET'])
    ]
    
    for path, methods in expected_routes:
        route = next((r for r in routes if r['path'] == path), None)
        assert route is not None, f"Route {path} not found"
        for method in methods:
            assert method in route['methods'], f"Method {method} not found for {path}"
        print(f"✓ {path} with {methods} registered")

def test_password_hashing():
    """Test password hashing functionality."""
    print("\nTesting password hashing...")
    
    from werkzeug.security import generate_password_hash, check_password_hash
    
    password = "testpassword123"
    hashed = generate_password_hash(password)
    
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed[:50]}...")
    
    assert hashed != password, "Hash should not equal password"
    assert check_password_hash(hashed, password), "Valid password should verify"
    assert not check_password_hash(hashed, "wrongpassword"), "Invalid password should not verify"
    
    print("✓ Password hashing works correctly")

def main():
    """Run all verifications."""
    print("="*50)
    print("Authentication Module Verification")
    print("="*50)
    
    try:
        test_models()
        test_routes()
        test_password_hashing()
        
        print("\n" + "="*50)
        print("✓ All verifications passed!")
        print("="*50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
