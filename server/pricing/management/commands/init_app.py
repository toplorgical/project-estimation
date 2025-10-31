from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = (
        "Initialize application: run migrations, ensure superuser, and populate sample data once."
    )

    def handle(self, *args, **options):
        self.stdout.write("Running database migrations...")
        call_command("migrate", interactive=False)
        self.stdout.write(self.style.SUCCESS("✓ Migrations complete"))

        self.stdout.write("Ensuring superuser exists...")
        call_command("ensure_superuser")
        self.stdout.write(self.style.SUCCESS("✓ Superuser ensured"))

        self.stdout.write("Populating sample data if database is empty...")
        call_command("populate_sample_data", if_empty=True)
        self.stdout.write(self.style.SUCCESS("✓ Sample data ensured"))
