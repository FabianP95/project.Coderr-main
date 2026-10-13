from django.urls import include, path
from rest_framework import routers

from .views import OfferDetailView, OfferViewSet

router = routers.SimpleRouter()
router.register(r"offers", OfferViewSet, basename="offers")

urlpatterns = [
    path("", include(router.urls)),
    path("offerdetails/<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
]
