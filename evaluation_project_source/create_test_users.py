"""
Script to create test users with different roles
Run this script with: python create_test_users.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EvaluationProject.settings')
django.setup()

from django.contrib.auth.models import User
from evaluation_app.models import UserProfile


def create_test_users():
    """Create test users for each role"""
    
    test_users = [
        {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'phone': '1234567890'
        },
        {
            'username': 'regular_user',
            'email': 'user@example.com',
            'password': 'user123',
            'first_name': 'Regular',
            'last_name': 'User',
            'role': 'user',
            'phone': '0987654321'
        },
        {
            'username': 'guest_user',
            'email': 'guest@example.com',
            'password': 'guest123',
            'first_name': 'Guest',
            'last_name': 'User',
            'role': 'guest',
            'phone': '5555555555'
        }
    ]
    
    print("\n" + "="*60)
    print("Creating Test Users for Evaluation System")
    print("="*60 + "\n")
    
    for user_data in test_users:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists. Skipping...")
            continue
        
        try:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Update profile
            user.profile.role = user_data['role']
            user.profile.phone = user_data['phone']
            user.profile.save()
            
            print(f"✅ Created {user_data['role'].upper()} user:")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating user '{username}': {str(e)}\n")
    
    print("="*60)
    print("Test Users Creation Complete!")
    print("="*60)
    print("\nYou can now login with any of the above credentials.")
    print("Navigate to: http://localhost:8000/login/\n")


if __name__ == '__main__':
    create_test_users()
