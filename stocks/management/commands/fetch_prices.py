from django.core.management.base import BaseCommand
from stocks.tasks import fetch_all_stock_prices


class Command(BaseCommand):
    help = 'Fetch current stock prices for all monitored stocks'

    def handle(self, *args, **options):
        self.stdout.write('Fetching stock prices...')
        
        result = fetch_all_stock_prices.delay().get()
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {result["updated_count"]}/{result["total_count"]} stocks'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to fetch prices: {result["error"]}')
            )
