#!/usr/bin/env python
"""
Verification script to check admin setup
"""

import os
import sys
import django

# Add GMS directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'GMS'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GMS.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("Admin Setup Verification")
print("=" * 60)

email = 'manager@gms.com'

try:
    user = User.objects.get(email=email)
    
    print(f"\n✓ User found: {email}")
    print(f"  Name: {user.name}")
    print(f"  is_superuser: {user.is_superuser}")
    print(f"  is_staff: {user.is_staff}")
    print(f"  is_active: {user.is_active}")
    
    if hasattr(user, 'staff_profile'):
        staff = user.staff_profile
        print(f"\n✓ Staff profile exists")
        print(f"  Employee ID: {staff.employee_id}")
        print(f"  Role: {staff.role.name if staff.role else 'None'}")
        print(f"  Status: {staff.status}")
    
    print("\n" + "=" * 60)
    if user.is_superuser:
        print("✓ ADMIN SETUP COMPLETE!")
        print("=" * 60)
        print("\nThis user can now:")
        print("  • Approve leave requests")
        print("  • Reject leave requests")
        print("  • View all leave requests")
        print("  • Manage all staff operations")
        print("\nRegular staff members CANNOT approve/reject leave requests.")
    else:
        print("⚠️  WARNING: User is not a superuser!")
        print("=" * 60)
        print("\nRun this command to fix:")
        print("  python manage.py make_manager_superuser")
    
except User.DoesNotExist:
    print(f"\n❌ User {email} not found!")
    print("\nRun setup_staff.py first to create the manager account.")

print()
