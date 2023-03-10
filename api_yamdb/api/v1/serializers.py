from rest_framework import serializers
from rest_framework.validators import ValidationError

from api_yamdb.settings import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH)
from reviews.models import Title, Category, Genre, CustomUser, Review, Comment
from .validators import username_validation


class CategorySerializer(serializers.ModelSerializer):
    """A serializer for the Category model."""

    class Meta:

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """A serializer for the Genre model."""

    class Meta:

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

        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """A serializer for the Review model that serializes selected fields."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                    author=self.context.get('request').user,
                    title__id=self.context.get('view').kwargs.get('title_id')
            ).exists():
                raise ValidationError('Only one review per title!')
        return super().validate(data)


class CommentSerializer(serializers.ModelSerializer):
    """A serializer for the Comment model that serializes selected fields."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:

        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)


class CustomUserSerializer(serializers.ModelSerializer):
    """A serializer for the CustomUser model that serializes selected fields.
    """

    class Meta:

        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        model = CustomUser


class EditUserProfileSerializer(CustomUserSerializer):
    """Serializer for changing data in the user's profile,
    except for the user's role.
    """
    role = serializers.CharField(read_only=True)


class SignUpSerializer(serializers.Serializer):
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


class TokenSerializer(serializers.Serializer):
    """Serialize request data for getting your AuthToken."""
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField(max_length=300)
