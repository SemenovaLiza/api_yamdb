from django.db import models
from django.contrib.auth.models import AbstractUser

from api_yamdb.settings import ADMIN, MODERATOR, USER, USERNAME_MAX_LENGTH


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='slug')
    description = models.TextField(
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
        null=False,
        blank=False,
        related_name='category',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Медиаконтент'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название жанра')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name

ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    role = models.CharField(
        choices=ROLES,
        default=USER,
        max_length=max(len(role[0]) for role in ROLES)
    )
    bio = models.TextField(blank=True, null=True)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    text = models.TextField()

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'],
                                    name='unique_reviews')]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
