import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Ensure a Django superuser exists; create it if missing (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            dest="email",
            help="Superuser email (overrides DJANGO_SUPERUSER_EMAIL)",
        )
        parser.add_argument(
            "--password",
            dest="password",
            help="Superuser password (overrides DJANGO_SUPERUSER_PASSWORD)",
        )
        parser.add_argument("--username", dest="username", help="Username (optional)")
        parser.add_argument("--first-name", dest="first_name", help="First name (optional)")
        parser.add_argument("--last-name", dest="last_name", help="Last name (optional)")

    def handle(self, *args, **options):
        User = get_user_model()

        email = options.get("email") or os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@local")
        password = options.get("password") or os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")
        username = options.get("username") or os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        first_name = options.get("first_name") or os.getenv("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
        last_name = options.get("last_name") or os.getenv("DJANGO_SUPERUSER_LAST_NAME", "User")

        # Idempotent: if exists, just report and exit
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"✓ Superuser already exists: {email}"))
            return

        # Create the superuser
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        except TypeError:
            # Fallback in case custom manager has different signature
            user = User(email=email, username=username, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()

        self.stdout.write(self.style.SUCCESS(f"✓ Superuser created: {email}"))
