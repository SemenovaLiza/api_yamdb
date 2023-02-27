import re
from rest_framework import serializers

from reviews.models import Title, Category, Genre, CustomUser, Review, Comment
from api_yamdb.settings import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
                                FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH)


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
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
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
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=True)
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH, required=True)
    first_name = serializers.CharField(
        max_length=FIRST_NAME_MAX_LENGTH, required=False)
    last_name = serializers.CharField(
        max_length=LAST_NAME_MAX_LENGTH, required=False)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                '"me" is invalid username.')
        if not re.match(r'^[\w.@+-]+\Z', data['username']):
            raise serializers.ValidationError(
                'The username must consist of letters, digits'
                'and @/./+/-/_ only.')
        return data

    class Meta:
        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        read_only_fields = ('role',)
        model = CustomUser


class AdminSerializer(serializers.ModelSerializer):
    role = serializers.CharField(max_length=13, required=False)
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=True)
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH, required=True)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                '"me" is invalid username.')
        if not re.match(r'^[\w.@+-]+\Z', data['username']):
            raise serializers.ValidationError(
                'The username must consist of letters, digits'
                'and @/./+/-/_ only.')
        return data

    class Meta:
        fields = (
            'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        model = CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=True
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH, required=True)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                '"me" is invalid username.')
        if re.match(r'^[\w.@+-]+\Z', data['username']) is None:
            raise serializers.ValidationError(
                'The username must consist of letters, digits'
                'and @/./+/-/_ only.')
        return data

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    class Meta:
        fields = ('username', 'email')
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField(max_length=300)
