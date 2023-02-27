from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import (
    filters, viewsets, views, viewsets, status, permissions, mixins)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


from reviews.models import (Category, Genre, Title,
                            CustomUser, Review, Comment)
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdmin,
                          IsAuthor, AuthorOrStaffOrReadOnly)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializerGet, TitleSerializerPost,
                          AdminSerializer, CustomUserSerializer,
                          SignUpSerializer, TokenSerializer,
                          ReviewSerializer, CommentSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializerGet
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleSerializerPost
        return TitleSerializerGet


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('name')
    ordering_fields = ('name', 'year')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('name')
    ordering_fields = ('name', 'year')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class CustomUserViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = CustomUser.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (IsAdmin, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=True, url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_user_profile(self, request):
        if request.method == 'patch':
            if self.request.user.is_admin:
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
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=False)
    def get_users_list(request):
        users = CustomUser.objects.all()
        serializer = AdminSerializer(users, many=True)
        return Response(serializer.data)


class SignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        user = get_object_or_404(
            CustomUser, username=username
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='YaMbd registration',
            message=('Confirmation code for registration:'
                     f'{str(confirmation_code)}'),
            from_email=None,
            recipient_list=[email]
        )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser, username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
