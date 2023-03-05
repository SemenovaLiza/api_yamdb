from rest_framework import serializers
from reviews.models import Title, Category, Genre, CustomUser, Review, Comment
from api_yamdb.settings import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH)
from .validators import username_validation


class CategorySerializer(serializers.ModelSerializer):
    """A serializer for the Category model."""

    class Meta:
        """Defines metadata options for the 'Category' serializer."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """A serializer for the Genre model."""

    class Meta:
        """Defines metadata options for the 'Genre' serializer."""

        model = Genre
        fields = ('name', 'slug')


class TitleSerializerPost(serializers.ModelSerializer):
    """A serializer for the Title model."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        """Defines metadata options for
        the 'TitleSerializerPost' serializer."""

        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        slug_field = 'slug'


class TitleSerializerGet(serializers.ModelSerializer):
    """A serializer for the Title model that serializes selected fields.
    Includes nested representations of related fields."""

    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        """Defines metadata options for the 'TitleSerializerGet' serializer."""

        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """A serializer for the Review model that serializes selected fields."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        """Defines metadata options for the 'ReviewSerializer' serializer."""
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    """A serializer for the Comment model that serializes selected fields."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        """Defines metadata options for the 'CommentSerializer' serializer."""
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)


class CustomUserSerializer(serializers.ModelSerializer):
    """A serializer for the CustomUser model that serializes selected fields.
    Meant for non-admin access to the user list.
    """

    class Meta:
        """Defines metadata options for the 'CustomUserSerializer' serializer.
        """
        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        read_only_fields = ('role',)
        model = CustomUser


class AdminSerializer(serializers.ModelSerializer):
    """A serializer for the CustomUser model that serializes selected fields.
    Meant for the admin-only access to user roles.
    """

    class Meta:
        """Defines metadata options for the 'AdminSerializer' serializer."""
        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        model = CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    """A serializer for the CustomUser model that serializes selected fields.
    Specifically meant for creating signing up new user.
    """
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[username_validation],
        required=True
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True
    )

    def validate(self, data):
        """Uniqueness validation for creating new 'CustomUser' object."""
        name = data["username"]
        email = data["email"]
        if not CustomUser.objects.filter(username=name, email=email).exists():
            if CustomUser.objects.filter(username=name):
                raise serializers.ValidationError(
                    'A user with this username already exists.'
                )

            if CustomUser.objects.filter(email=email):
                raise serializers.ValidationError(
                    'A user with this email already exists.'
                )

        return data

    class Meta:
        """Defines metadata options for the 'SignUpSerializer' serializer."""
        fields = ('username', 'email')
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    """Serialize request data for getting your AuthToken."""
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField(max_length=300)
