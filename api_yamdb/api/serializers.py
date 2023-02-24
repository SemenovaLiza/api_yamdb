from rest_framework import serializers
from reviews.models import CustomUser, Review
from api_yamdb.settings import USERNAME_MAX_LENGTH


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        read_only_fields = ('role',)
        model = CustomUser


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        model = CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=True
    )
    email = serializers.EmailField(required=True)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                '"me" - некорректное имя пользователя.')
        return data

    class Meta:
        fields = ('username', 'email')
        model = CustomUser


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField(max_length=300)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'author', 'pub_date',)
