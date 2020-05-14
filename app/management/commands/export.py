from django.core import serializers
from django.core.management.base import BaseCommand
from app.models import Result


class Command(BaseCommand):
    help = 'Exports results in JSON through stdout'

    def handle(self, *args, **options):
        rs = Result.objects.all()
        print(
            serializers.serialize('json', rs)
        )
