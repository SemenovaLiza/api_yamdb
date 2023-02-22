from rest_framework import serializers

from reviews.models import CustomUser
from api_yamdb.settings import USERNAME_MAX_LENGTH


# сериалиатор для обычного пользователя
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'username', 'email',
            'role', 'bio',
            'first_name', 'last_name'
        )
        read_only_fields = ('role',)
        model = CustomUser


# сериализатор для назначения ролей пользователям
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
