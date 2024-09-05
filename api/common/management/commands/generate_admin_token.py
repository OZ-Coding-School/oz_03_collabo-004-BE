from django.core.management.base import BaseCommand, CommandError
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class Command(BaseCommand):
    help = "Generate JWT tokens for the admin user"

    def handle(self, *args, **options):
        email = input("Enter the email of the user: ")
        password = input("Enter the password of the user: ")
        try:
            user = User.objects.get(email=email.strip())
            if not user.check_password(password.strip()):
                raise CommandError("Password is incorrect")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            self.stdout.write(self.style.SUCCESS(f"Access Token: {access_token}"))
            self.stdout.write(self.style.SUCCESS(f"Refresh Token: {refresh_token}"))
        except User.DoesNotExist:
            raise CommandError("Admin user with the specified email does not exist")
