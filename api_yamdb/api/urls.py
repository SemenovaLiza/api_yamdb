from django.urls import path, include
from rest_framework import routers

from .views import ReviewViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')

urlpatterns = [
    path('v1/', include(router_v1.urls))
]
