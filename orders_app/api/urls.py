from django.urls import include, path
from rest_framework import routers

from .views import CompletedOrdersView, OrdersDetailView, OrderViewSet

router = routers.SimpleRouter()
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
    path("order-count/<int:pk>/", OrdersDetailView.as_view(), name="order-count"),
    path(
        "completed-order-count/<int:pk>/",
        CompletedOrdersView.as_view(),
        name="completed-order-count",
    ),
]
