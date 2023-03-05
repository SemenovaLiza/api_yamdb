from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import AbstractUser

from api_yamdb.settings import (ADMIN, MODERATOR, USER,
                                USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
                                FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH)
from api.validators import username_validation


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


ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
)


class CustomUser(AbstractUser):
    """Customized user model with RBAC implemented."""
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        blank=False,
        validators=[username_validation]
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        blank=False
    )
    role = models.CharField(
        choices=ROLES,
        default=USER,
        max_length=max(len(role[0]) for role in ROLES),
        blank=True
    )
    bio = models.TextField(blank=True, null=True)
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        blank=True
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


class Review(models.Model):
    """The Review model represents a user-created review on media title."""
    author = models.ForeignKey(
        CustomUser,
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

    class Meta:

        constraints = [UniqueConstraint(
            fields=['title', 'author'], name='unique_reviews')]

    def __str__(self):
        """Represent a string of the Review instance. Returns review's text."""
        return self.text


class Comment(models.Model):
    """The Comment model represents a user comments on review objects."""
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
