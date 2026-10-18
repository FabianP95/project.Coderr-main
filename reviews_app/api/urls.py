from django.urls import include, path
from rest_framework import routers

from .views import ReviewViewSet

router = routers.SimpleRouter()
router.register(r"reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("", include(router.urls)),
]
