#!/usr/bin/env python3
"""
Script to create a test user for login testing
Usage: python3 create_test_user.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.user import User
from app.utils.auth import hash_password, verify_password

def create_test_user():
    app = create_app()
    with app.app_context():
        email = "a@a.com"
        password = "123456789"
        
        # Check if user exists
        existing_user = User.objects(email=email).first()
        if existing_user:
            print(f"User {email} already exists!")
            print(f"Testing password verification...")
            is_valid = verify_password(password, existing_user.hashed_password)
            if is_valid:
                print(f"✓ Password is correct!")
                print(f"User details:")
                print(f"  - ID: {existing_user.id}")
                print(f"  - Name: {existing_user.name}")
                print(f"  - Role: {existing_user.role}")
                print(f"  - Email: {existing_user.email}")
            else:
                print(f"✗ Password verification failed!")
                print(f"Updating password...")
                existing_user.hashed_password = hash_password(password)
                existing_user.save()
                print(f"✓ Password updated successfully!")
            return
        
        # Create new user
        print(f"Creating new user: {email}")
        try:
            user = User(
                email=email,
                hashed_password=hash_password(password),
                name="Test User",
                phone="1234567890",
                role="supplier",
                company_name="Test Company",
                country="IN"
            )
            user.save()
            print(f"✓ User created successfully!")
            print(f"User details:")
            print(f"  - ID: {user.id}")
            print(f"  - Email: {user.email}")
            print(f"  - Role: {user.role}")
            print(f"  - Password: {password}")
            
            # Verify password
            print(f"\nVerifying password...")
            is_valid = verify_password(password, user.hashed_password)
            if is_valid:
                print(f"✓ Password verification successful!")
            else:
                print(f"✗ Password verification failed!")
        except Exception as e:
            print(f"✗ Error creating user: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_test_user()

