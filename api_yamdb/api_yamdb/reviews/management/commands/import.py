import csv
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import (Category, Genre, Title)

SOURCES = {
    # User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    # Review: 'review.csv',
    # Comment: 'comments.csv',
    # GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):
    help = 'CSV Import'

    def handle(self, *args, **kwargs):
        for model, source in SOURCES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{source}',
                    'r', encoding='utf-8') as f:
                '''Объект чтения в качестве словаря'''
                reader = csv.DictReader(f)
                model.objects.bulk_create(model(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS('Загрузка успешна'))
