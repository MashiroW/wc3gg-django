from django.core.management.base import BaseCommand
from myapp.models import Player

class Command(BaseCommand):
    help = 'Delete all Player records'

    def handle(self, *args, **kwargs):
        Player.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all Player records.'))
