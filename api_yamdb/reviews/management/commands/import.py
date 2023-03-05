"""Import CSV."""

import csv
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import (Category, Genre, Title, CustomUser,
                            Review, Comment, GenreTitle)

SOURCES = {
    CustomUser: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):
    """A subclass of Django's BaseCommand."""

    help = 'CSV Import'

    def handle(self, *args, **options):
        """Import CSVs when the command is entered."""
        for model, source in SOURCES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{source}',
                    encoding='utf-8') as f:
                '''Reading object as a dictionary.'''
                reader = csv.DictReader(f)
                model.objects.bulk_create(model(**data) for data in reader)
