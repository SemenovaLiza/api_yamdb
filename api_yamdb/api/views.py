from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import (
    filters, views, viewsets, status, permissions)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import (Category, Genre, Title,
                            CustomUser, Review)
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdmin,
                          AuthorOrStaffOrReadOnly)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializerGet, TitleSerializerPost,
                          AdminSerializer, CustomUserSerializer,
                          SignUpSerializer, TokenSerializer,
                          ReviewSerializer, CommentSerializer)


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


class ListMixin:
    """Correspond to the list."""

    queryset = None
    serializer_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name', 'year')
    lookup_field = 'slug'
    http_method_names = ('get', 'post', 'delete')


class DestroyMixin:
    """Correspond to delete."""

    def destroy(self, request, *args, **kwargs):
        """Delete an existing instance of the view model associated."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotAllowedMixin:
    """Correspond to retreat."""

    def http_method_not_allowed(self, request, *args, **kwargs):
        """Return a 405 response with no content."""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        """Return a response with a status of 405."""
        return self.http_method_not_allowed(request, *args, **kwargs)


class GenreListMixin(ListMixin):
    """Inherit from ListMixin with settings."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreViewSet(GenreListMixin, DestroyMixin,
                   NotAllowedMixin, viewsets.ModelViewSet):
    """A ViewSet for CRUD operations on the Genre model."""

    pass


class CategoryListMixin(ListMixin):
    """Inherit from ListMixin with settings."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryViewSet(CategoryListMixin, DestroyMixin,
                      NotAllowedMixin, viewsets.ModelViewSet):
    """A ViewSet for CRUD operations on the Category model."""

    pass


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
        queryset = Review.objects.filter(
            title=self.get_title(), author=self.request.user)
        if queryset.exists():
            raise ValidationError('Only one review per author is allowed')
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
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

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
    serializer_class = AdminSerializer
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
        serializer = CustomUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpView(views.APIView):
    """A view for creating new CustomUser model."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Create CustomUser with 200 and send confirmation email."""
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
            from_email=None,
            recipient_list=[email]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(views.APIView):
    """A view for getting AuthToken with email confirmation code."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Get AuthToken with 200. Response 400 with incorrect data."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser, username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
        ):
            token = default_token_generator.get_token_for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
