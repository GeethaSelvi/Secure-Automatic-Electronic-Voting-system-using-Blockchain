# adminapp/management/commands/sync_votes.py
from django.core.management.base import BaseCommand
from adminapp.models import Candidate

class Command(BaseCommand):
    help = 'Sync votes from blockchain to database'
    
    def handle(self, *args, **options):
        for candidate in Candidate.objects.all():
            if candidate.blockchain_id:
                candidate.update_votes()
        self.stdout.write('Votes synced successfully')