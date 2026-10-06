from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializers import (
    OfferSerializer,
    OfferDetailSerializer,
    OfferDetailsSerializer,
    OrderSerializer,
    ReviewSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = OfferSerializer


class OfferDetailView(generics.ModelViewSet):
     permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer


class OrdersDetailView(APIView):
    permission_classes = [IsAuthenticated]


class CompletedOrdersView(APIView):
    permission_classes = [IsAuthenticated]


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]
    
