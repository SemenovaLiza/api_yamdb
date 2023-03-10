from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import (
    filters, viewsets, status, permissions, mixins)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import (Category, Genre, Title,
                            CustomUser, Review)
from api_yamdb import settings
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdmin,
                          AuthorOrStaffOrReadOnly)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializerGet, TitleSerializerPost,
                          EditUserProfileSerializer, CustomUserSerializer,
                          SignUpSerializer, TokenSerializer,
                          ReviewSerializer, CommentSerializer)


@api_view(['post'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """A view for creating a new user by sending
    a confirmation code to the email.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    user, created = CustomUser.objects.get_or_create(
        username=username, email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='YaMbd registration',
        message=('Confirmation code for registration:'
                 f'{str(confirmation_code)}'),
        from_email=settings.FROM_EMAIL,
        recipient_list=[email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['post'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """A view for getting AuthToken with email confirmation code."""
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


class TitleViewSet(viewsets.ModelViewSet):
    """A ViewSet for CRUD operations on the Title model."""

    queryset = Title.objects.annotate(rating=Round(Avg('reviews__score')))
    serializer_class = TitleSerializerPost
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Request Serializer to use."""
        if self.action in ('create', 'update', 'partial_update'):
            return TitleSerializerPost
        return TitleSerializerGet


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet
                   ):
    """A ViewSet for CRUD operations on the Genre model."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name', 'year')
    lookup_field = 'slug'


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """A ViewSet for CRUD operations on the Category model."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name', 'year')
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    """A ViewSet for CRUD operations on the Review model."""
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_title(self):
        """Instrumental method for accessing Title object from request."""
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def perform_create(self, serializer):
        """Custom creation method for Review objects.
        Provides user and title info to the object after uniqueness check."""
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        """Overrided reviews query for getting title-related objects."""
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    """A ViewSet for CRUD operations on the Comment model."""
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_review(self):
        """Instrumental method for accessing Review object from the request."""
        return get_object_or_404(Review, pk=self.kwargs['review_id'],
                                 title__id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        """Custom creation method for Comment objects.
        Provides review and user relation to the object."""
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        """Overrided comments query for getting review-related comments."""
        return self.get_review().comments.all()


class CustomUserViewSet(viewsets.ModelViewSet):
    """A ViewSet for CRUD operations on the CustomUser model."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdmin, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    http_method_names = ("get", "post", "delete", "patch")

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_user_profile(self, request):
        """Get user profile info with 200."""
        serializer = EditUserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
