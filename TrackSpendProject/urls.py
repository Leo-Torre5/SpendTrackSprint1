from django.contrib import admin
from django.urls import path, include, re_path
from expenses.views import ExpenseListCreateAPIView, BudgetRetrieveUpdateDestroyAPIView
from django.views.static import serve
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    RegisterAPIView,
    CustomTokenObtainPairView,
    UserProfileAPIView
)
from django.views.generic import RedirectView

urlpatterns = [
    # Authentication & Core
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='api-auth/login/')),  # Redirect root to DRF login
    path('register/', RegisterAPIView.as_view(), name='auth_register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/getUser/', UserProfileAPIView.as_view(), name='get_user'),
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout

    # Media & Static (for production)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    # Expenses
    path('api/expenses/', ExpenseListCreateAPIView.as_view(), name='expenses-list'),
    path('api/budgets/<int:pk>/', BudgetRetrieveUpdateDestroyAPIView.as_view(), name='budget-detail'),
]