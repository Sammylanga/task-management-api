import logging
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer

# Initialize logger
logger = logging.getLogger("users")

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"New user registered: {request.data.get('username')}")
            return response
        except Exception as e:
            logger.error(f"Error during user registration: {e}")
            return Response({"error": f"User registration failed {e}"}, status=500)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"User {request.data.get('username')} logged in successfully")
            return response
        except Exception as e:
            logger.error(f"Login error for user {request.data.get('username')}: {e}")
            return Response({"error": "Authentication failed"}, status=401)

class AdminOnlyView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            logger.warning(f"Unauthorized access attempt to AdminOnlyView by {request.user.username}")
            return Response({"error": "Forbidden"}, status=403)

        logger.info(f"Admin user {request.user.username} accessed AdminOnlyView")
        return super().get(request, *args, **kwargs)
