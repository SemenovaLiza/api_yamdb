from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import permissions
from rest_framework import views, viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CustomUser
from .permissions import IsAdmin, IsAuthor
from .serializers import (AdminSerializer, CustomUserSerializer,
                          SignUpSerializer, TokenSerializer)


# данные пользователя
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdmin, IsAuthor)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(
        methods=['get', 'retrieve', 'patch'],
        detail=True, url_path='me'
    )
    def get_user_profile(request):
        if request.method == 'patch':
            if request.user.is_admin:
                serializer = AdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = CustomUserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_users_list(request):
        if request.method == 'get' and request.user.is_admin:
            users = CustomUser.objects.all()
            serializer = AdminSerializer(users, many=True)
            return Response(serializer.data)


class SignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = get_object_or_404(
            CustomUser, username=serializer.validated_data['username']
        )
        confirmation_code = default_token_generator.make_token(user)
        user_email = serializer.validated_data['email']
        send_mail(
            subject='YaMbd registration',
            message=f'Confirmation code for registration: {confirmation_code}',
            from_email=None,
            recipient_list=[user_email, ]
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetTokenView(views.APIView):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser, username=serializer.validate_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
