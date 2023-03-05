"""A list of URL patterns for the API endpoints."""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views


v1_router = SimpleRouter()
v1_router.register('titles', views.TitleViewSet, basename='titles')
v1_router.register('categories', views.CategoryViewSet, basename='categories')
v1_router.register('genres', views.GenreViewSet, basename='genres')
v1_router.register('users', views.CustomUserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews', views.ReviewViewSet,
                   basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', views.GetTokenView.as_view(), name='token'),
]
