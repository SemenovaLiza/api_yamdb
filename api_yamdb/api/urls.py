from django.urls import include, path

from . import views
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet,
                    CustomUserViewSet,
                    ReviewViewSet)

v1_router = SimpleRouter()
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('users', CustomUserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', views.GetTokenView.as_view(), name='token'),
]
