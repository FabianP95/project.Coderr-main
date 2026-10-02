from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    ReviewSerializer,
    OfferSerializer,
    OrderSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = OfferSerializer


class OfferDetailView(generics.ListAPIView):
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
    
