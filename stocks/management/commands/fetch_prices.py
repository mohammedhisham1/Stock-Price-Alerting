from django.core.management.base import BaseCommand
from stocks.tasks import fetch_all_stock_prices


class Command(BaseCommand):
    help = 'Fetch current stock prices for all monitored stocks'

    def handle(self, *args, **options):
        self.stdout.write('Fetching stock prices...')
        
        # Call the task directly instead of using .delay() for management command
        result = fetch_all_stock_prices()
        
        if result.get('success'):
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {result.get("successful", 0)} stocks '
                    f'with {result.get("errors", 0)} errors'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to fetch prices: {result.get("error", "Unknown error")}')
            )
