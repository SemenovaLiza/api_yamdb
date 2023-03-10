from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

from api_yamdb.settings import (ADMIN, MODERATOR, USER,
                                USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
                                FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH)
from api.v1.validators import username_validation


class Title(models.Model):
    """The Title model represents a media content title."""

    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год')
    description = models.TextField(
        max_length=1000, null=True, blank=True, verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        'Genre',
        through='GenreTitle',
        related_name='genre',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='category',
        verbose_name='Категория',
    )

    class Meta:

        verbose_name = 'Медиаконтент'
        verbose_name_plural = 'Медиаконтент'

    def __str__(self):
        """Represent a string of the Title instance."""
        return self.name


class Category(models.Model):
    """The Category model represents a media content category."""

    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='slug')

    class Meta:

        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Represent a string of the Category instance."""
        return self.name


class Genre(models.Model):
    """The Genre model represents a media content genre."""

    name = models.CharField(max_length=256, verbose_name='Название жанра')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')

    class Meta:

        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        """Represent a string of the Genre instance."""
        return self.name


class GenreTitle(models.Model):
    """The model represents the relationship between a Title and a Genre."""

    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)


class CustomUser(AbstractUser):
    """Customized user model with RBAC implemented."""
    ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        blank=False,
        validators=[username_validation],
        verbose_name='Никнейм пользователя'
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Почта пользователя'
    )
    role = models.CharField(
        choices=ROLES,
        default=USER,
        max_length=max(len(role[0]) for role in ROLES),
        blank=True,
        verbose_name='Роль пользователя'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='О пользователе'
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        blank=True,
        verbose_name='Фамилия пользователя'
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        """Represent a string of the CustomUser instance. Returns username."""
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Review(models.Model):
    """The Review model represents a user-created review on media title."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Медиаконтент'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )
    text = models.TextField(verbose_name='Текст')

    class Meta:
        verbose_name = 'Отзыв'
        constraints = [UniqueConstraint(
            fields=['title', 'author'], name='unique_reviews')]

    def __str__(self):
        """Represent a string of the Review instance. Returns review's text."""
        return self.text


class Comment(models.Model):
    """The Comment model represents a user comments on review objects."""
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации комментария')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments', verbose_name='Отзыв')

    class Meta:
        verbose_name = 'Комментарий'
