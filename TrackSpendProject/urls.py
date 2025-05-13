# TrackSpendProject/urls
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from expenses.views import ExpenseListCreateAPIView, ExpenseRetrieveUpdateDestroyAPIView, CategoryListAPIView, \
    CategoryRetrieveAPIView, BudgetListCreateAPIView, BudgetRetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.static import serve
from django.conf import settings
from users.views import (
    RegisterAPIView,
    CustomTokenObtainPairView,
    UserProfileAPIView,
    AdminUserListCreateAPIView,
    AdminUserRetrieveUpdateDestroyAPIView,
    AdminCategoryListCreateAPIView,
    AdminCategoryRetrieveUpdateDestroyAPIView,
    AdminBudgetListCreateAPIView,
    AdminBudgetRetrieveUpdateDestroyAPIView,
    UpdateUserProfileAPIView,
    contact_view
)

router = DefaultRouter()

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # DRF Root Home
    path('', include(router.urls)),  # DRF default home

    # Authentication & API Endpoints
    path('register/', RegisterAPIView.as_view(), name='auth_register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),  # Login/logout for DRF

    # Expenses
    path('api/expenses/', ExpenseListCreateAPIView.as_view(), name='expense-list'),
    path('api/expenses/<int:pk>/', ExpenseRetrieveUpdateDestroyAPIView.as_view(), name='expense-detail'),

    # Categories
    path('api/categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', CategoryRetrieveAPIView.as_view(), name='category-detail'),

    # Budgets
    path('api/budgets/', BudgetListCreateAPIView.as_view(), name='budget-list'),
    path('api/budgets/<int:pk>/', BudgetRetrieveUpdateDestroyAPIView.as_view(), name='budget-detail'),

    # Admin Endpoints
    path('api/admin/users/', AdminUserListCreateAPIView.as_view(), name='admin-users-list'),
    path('api/admin/users/<int:pk>/', AdminUserRetrieveUpdateDestroyAPIView.as_view(), name='admin-user-detail'),
    path('api/admin/categories/', AdminCategoryListCreateAPIView.as_view(), name='admin-categories-list'),
    path('api/admin/categories/<int:pk>/', AdminCategoryRetrieveUpdateDestroyAPIView.as_view(),
         name='admin-category-detail'),
    path('api/admin/budgets/', AdminBudgetListCreateAPIView.as_view(), name='admin-budgets-list'),
    path('api/admin/budgets/<int:pk>/', AdminBudgetRetrieveUpdateDestroyAPIView.as_view(), name='admin-budget-detail'),

    # Profile
    path('api/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('api/profile/update/', UpdateUserProfileAPIView.as_view(), name='update-profile'),

    # Static files
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root':
                                                 settings.MEDIA_ROOT}),  # serve media files when deployed
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root':
                                                  settings.STATIC_ROOT}),  # serve static files when deployed

    #Email
    path('contact/', contact_view, name='contact'),
]