from django.core.management.base import BaseCommand
from django.db import transaction

from hunt.special_puzzles.events.fencing import FencingTeamData

@transaction.atomic
def fencing(upload):
    registered = list(FencingTeamData.objects
        .filter(registered=True)
        .order_by('registered_time')
        .select_related('team'))
    if not upload:
        return '\n'.join('%s,%s,%s' % (data.team.id, data.team.name,
            data.registered_time) for data in registered)
    urls = dict(line.split(',')[:2] for line in open(upload))
    for data in registered:
        data.url = urls.get(str(data.team_id), '')
        data.save()
    return 'Updated %s teams with %s urls' % (len(registered), len(urls))

class Command(BaseCommand):
    help = """Export and import data for the Fencing event."""

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, upload=None, **options):
        return fencing(upload)
