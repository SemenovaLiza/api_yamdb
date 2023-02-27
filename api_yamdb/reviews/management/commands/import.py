import csv
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import (Category, Genre, Title,
                            User, Comment, Review,
                            GenreTitle)

SOURCES = {
    Genre: 'genre.csv',
    Category: 'category.csv',
    Title: 'titles.csv',
    User: 'users.csv',
    Comment: 'comments.csv',
    Review: 'review.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):
    help = 'CSV Import'

    def handle(self, *args, **options):
        for model, source in SOURCES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{source}',
                    encoding='utf-8') as f:
                '''Read as dict'''
                reader = csv.DictReader(f)
                model.objects.bulk_create(
                    model(**content) for content in reader
                )

        self.stdout.write(self.style.SUCCESS('Загрузка успешна'))
