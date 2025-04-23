from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    AdminUserSerializer,
    AdminCategorySerializer,
    AdminBudgetSerializer
)
from .models import CustomUser, Profile
from expenses.models import Category, Budget

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email
    })

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = CustomUser.objects.get(username=request.data['username'])
            response.data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'user_type': user.user_type
            }
        return response


class UserProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
            profile_data = {
                'phone_number': profile.phone_number,
                'street_address': profile.street_address,
                'zip_code': profile.zip_code,
                'state': profile.state,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None
            }
        except Profile.DoesNotExist:
            profile_data = None

        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'user_type': user.user_type,
            'profile': profile_data
        }
        return Response(data)

# Admin Views
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.user_type == 2

class AdminUserListCreateAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all().select_related('profile')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        # Add additional context if needed
        serializer.save()


class AdminUserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_update(self, serializer):
        user = serializer.save()
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()

class AdminCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminBudgetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Budget.objects.all()
    serializer_class = AdminBudgetSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminBudgetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = [JSONParser]
    queryset = Budget.objects.all()
    serializer_class = AdminBudgetSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]