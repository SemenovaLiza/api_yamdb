from django.db import models


class Title(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год')
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.CharField(
        max_length=1000, null=True, blank=True, verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        'Genre',
        related_name='genre',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Медиаконтент'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название жанра')
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name
