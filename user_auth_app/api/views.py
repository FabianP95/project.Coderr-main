from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user_auth_app.models import User

from .permissions import IsProfileCreator
from .serializers import (
    BusinessUserSerializer,
    CustomerUserSerializer,
    RegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
)


class CustomLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _created = Token.objects.get_or_create(user=user)
            data = {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, _created = Token.objects.get_or_create(user=saved_account)
            data = {
                "token": token.key,
                "username": saved_account.username,
                "email": saved_account.email,
                "user_id": saved_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsProfileCreator]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BusinessProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessUserSerializer
    queryset = User.objects.filter(type=User.Type.BUSINESS)


class CustomerProfileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerUserSerializer
    queryset = User.objects.filter(type=User.Type.CUSTOMER)
