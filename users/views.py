import json

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
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
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import UpdateUserProfileSerializer
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

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
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() # Save the user instance

        # Generate token upon successful registration
        token_pair = CustomTokenObtainPairSerializer.get_token(user)
        refresh_token = str(token_pair)
        access_token = str(token_pair.access_token)

        response_data = {
            "refresh": refresh_token,
            "access": access_token,
            "user": UserSerializer(user).data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user_data = response.data.get('user')
            if user_data:
                # Include user data in the response
                response.data['user'] = user_data
        return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email
    })

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

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        custom_user = CustomUser.objects.get(id=user.id)
        profile = Profile.objects.get(user=custom_user)

        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
            'profile': {
                'id': profile.id,
                'phone_number': profile.phone_number,
                'street_address': profile.street_address,
                'city': profile.city,
                'zip_code': profile.zip_code,
                'state': profile.state,
                'profile_picture': request.build_absolute_uri(
                    profile.profile_picture.url) if profile.profile_picture else None
            }
        }

        return Response(user_data, status=status.HTTP_200_OK)

class UpdateUserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = UpdateUserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# E-Mail

@csrf_exempt
@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == "GET":
        return JsonResponse({
            "message": "Please send a POST request to this url."
        })
    try:
        data = json.loads(request.body)
        name = data.get('name', '')
        email = data.get('email', '')
        message = data.get('message', '')

        # Sending email
        send_mail(
            subject=f'Message from {name}',
            message=f'Message sent by {name} ({email}):\n\n{message}',
            from_email=email,
            recipient_list=['fscherer@unomaha.edu'],
            fail_silently=False,
        )

        return JsonResponse({'message': 'Message succesfully sent!'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)