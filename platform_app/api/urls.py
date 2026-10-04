from django.urls import include, path
from rest_framework import routers

from .views import (
    BaseInfoView,
    CompletedOrdersView,
    OfferDetailView,
    OfferViewSet,
    OrdersDetailView,
    OrderViewSet,
    ReviewViewSet,
)

router = routers.SimpleRouter()
router.register(r"offers", OfferViewSet, basename="offers")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("", include(router.urls)),
    path("offerdetails/<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
    path("order-count/<int:pk>/", OrdersDetailView.as_view(), name="order-count"),
    path(
        "completed-order-count/<int:pk>/",
        CompletedOrdersView.as_view(),
        name="completed-order-count",
    ),
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
