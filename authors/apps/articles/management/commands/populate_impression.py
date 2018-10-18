from django.core.management.base import (
    BaseCommand,
    CommandError
)

from authors.apps.articles.models import Impression


class Command(BaseCommand):
    help = "Populate the impressions table."

    def handle(self, *args, **options):
        impressions = [
            {'Like': 'Person finds the article appeasing'},
            {'Dislike': 'Person does not find the article to their liking'},
            {'Favourite': "Person has found that they resonate with an article's words"}
        ]
        try:
            Impression.objects.get(name='Like')
            message = 'No need to populate Impression table.'
        except Impression.DoesNotExist:
            for impression in impressions:
                for key, value in impression.items():
                    Impression.objects.create(
                        name=key,
                        description=value
                    ).save()
            message = 'Impression Table has been populated'

        self.stdout.write(self.style.SUCCESS(message))
