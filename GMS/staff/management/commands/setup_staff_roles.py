from django.core.management.base import BaseCommand
from staff.models import StaffRole


class Command(BaseCommand):
    help = 'Create initial staff roles with permissions'

    def handle(self, *args, **kwargs):
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
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.name}')
                )

        self.stdout.write(self.style.SUCCESS('\nStaff roles setup complete!'))
