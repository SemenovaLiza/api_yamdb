from rest_framework import serializers
from reviews.models import Title, Category, Genre, CustomUser, Review, Comment
from api_yamdb.settings import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH)
from .validators import username_validation


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializerPost(serializers.ModelSerializer):
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
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        read_only_fields = ('role',)
        model = CustomUser


class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        model = CustomUser


class SignUpSerializer(serializers.ModelSerializer):
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
        fields = ('username', 'email')
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField(max_length=300)
