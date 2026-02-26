from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Make manager@gms.com a superuser with admin privileges'

    def handle(self, *args, **kwargs):
        email = 'manager@gms.com'
        
        try:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully made {email} a superuser!')
            )
            self.stdout.write(
                self.style.SUCCESS('  - is_superuser: True')
            )
            self.stdout.write(
                self.style.SUCCESS('  - is_staff: True')
            )
            self.stdout.write(
                self.style.WARNING('\nNow only this admin can approve/reject leave requests.')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User {email} does not exist!')
            )
            self.stdout.write(
                self.style.WARNING('Run setup_staff.py first to create the manager account.')
            )
