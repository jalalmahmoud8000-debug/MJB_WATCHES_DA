
from django.core.management.base import BaseCommand
from accounts.tasks import send_email_task

class Command(BaseCommand):
    help = 'Sends a test email using the Celery task.'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient', 
            type=str, 
            help='The email address to send the test email to.'
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        subject = "Test Email from Celery"
        message = "This is a test email sent asynchronously using Celery and Redis."
        recipient_list = [recipient]

        self.stdout.write(self.style.NOTICE(
            f'Dispatching test email to {recipient}...'
        ))

        # Dispatch the task
        send_email_task.delay(subject, message, recipient_list)

        self.stdout.write(self.style.SUCCESS(
            'Successfully dispatched the email task. Check your Celery worker console for output.'
        ))
