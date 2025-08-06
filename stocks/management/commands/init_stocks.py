from django.core.management.base import BaseCommand
from stocks.services import initialize_monitored_stocks


class Command(BaseCommand):
    help = 'Initialize monitored stocks in the database'

    def handle(self, *args, **options):
        self.stdout.write('Initializing monitored stocks...')
        
        created_count = initialize_monitored_stocks()
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} new stocks')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No new stocks created (already exist)')
            )
