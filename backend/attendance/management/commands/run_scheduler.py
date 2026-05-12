from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run APScheduler to manage periodic tasks (forgotten_checkout at 19:00)"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler()

        scheduler.add_job(
            lambda: call_command('forgotten_checkout'),
            'cron',
            hour=19,
            minute=0,
            id='forgotten_checkout',
            name='Send checkout reminders at 19:00',
            replace_existing=True,
        )

        self.stdout.write(self.style.SUCCESS(
            'Scheduler started. Press Ctrl+C to stop.\n'
            '  - forgotten_checkout runs daily at 19:00'
        ))
        try:
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write('Scheduler stopped.')
