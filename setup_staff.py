#!/usr/bin/env python
"""
Quick setup script for Staff Module
Run this after migrations to create initial data
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GMS.settings')
django.setup()

from django.contrib.auth import get_user_model
from staff.models import Staff, StaffRole

User = get_user_model()

def create_roles():
    """Create initial staff roles"""
    print("Creating staff roles...")
    
    roles_data = [
        {
            'name': 'Manager',
            'description': 'Full access to manage staff, customers, schedules, and view reports',
            'can_manage_staff': True,
            'can_manage_customers': True,
            'can_manage_schedules': True,
            'can_view_reports': True,
        },
        {
            'name': 'Trainer',
            'description': 'Can manage customers and view schedules',
            'can_manage_staff': False,
            'can_manage_customers': True,
            'can_manage_schedules': False,
            'can_view_reports': False,
        },
        {
            'name': 'Receptionist',
            'description': 'Can manage customers and view schedules',
            'can_manage_staff': False,
            'can_manage_customers': True,
            'can_manage_schedules': False,
            'can_view_reports': False,
        },
        {
            'name': 'Maintenance',
            'description': 'Basic access to view schedules',
            'can_manage_staff': False,
            'can_manage_customers': False,
            'can_manage_schedules': False,
            'can_view_reports': False,
        },
    ]

    for role_data in roles_data:
        role, created = StaffRole.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        if created:
            print(f"✓ Created role: {role.name}")
        else:
            print(f"- Role already exists: {role.name}")


def create_sample_manager():
    """Create a sample manager account"""
    print("\nCreating sample manager account...")
    
    email = 'manager@gms.com'
    
    if User.objects.filter(email=email).exists():
        print(f"- Manager account already exists: {email}")
        return
    
    # Create user
    user = User.objects.create_user(
        email=email,
        name='System Manager',
        password='manager123',  # Change this in production!
        role='Mechanic',
        phone='1234567890',
        address='GMS Office',
        is_active=True,
        is_verified=True
    )
    
    # Get Manager role
    manager_role = StaffRole.objects.get(name='Manager')
    
    # Create staff profile
    staff = Staff.objects.create(
        user=user,
        employee_id='MGR001',
        role=manager_role,
        hire_date='2024-01-01',
        department='Management',
        salary=50000.00,
        status='Active'
    )
    
    print(f"✓ Manager created successfully!")
    print(f"  Email: {email}")
    print(f"  Password: manager123")
    print(f"  Employee ID: {staff.employee_id}")
    print(f"\n  Login at: http://localhost:8000/staff/login/")


def main():
    print("=" * 60)
    print("Staff Module Setup")
    print("=" * 60)
    
    try:
        create_roles()
        create_sample_manager()
        
        print("\n" + "=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://localhost:8000/staff/login/")
        print("3. Login with: manager@gms.com / manager123")
        print("\n⚠️  Remember to change the default password!")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        print("Make sure you've run migrations first:")
        print("  python manage.py makemigrations")
        print("  python manage.py migrate")


if __name__ == '__main__':
    main()
