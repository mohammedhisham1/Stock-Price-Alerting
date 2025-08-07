from django.core.management.base import BaseCommand
from alerts.tasks import evaluate_all_alerts


class Command(BaseCommand):
    help = 'Evaluate all active alerts'

    def handle(self, *args, **options):
        self.stdout.write('Evaluating alerts...')
        
        result = evaluate_all_alerts.delay()
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Evaluated {result["total_alerts"]} alerts, '
                    f'{result["triggered_count"]} triggered'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to evaluate alerts: {result["error"]}')
            )
