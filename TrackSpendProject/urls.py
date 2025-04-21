from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from expenses.views import ExpenseListCreateAPIView, ExpenseRetrieveUpdateDestroyAPIView, CategoryListAPIView, \
    CategoryRetrieveAPIView, BudgetListCreateAPIView, BudgetRetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    RegisterAPIView,
    CustomTokenObtainPairView,
    UserProfileAPIView
)
from django.views.generic import RedirectView
router = DefaultRouter()

# Si vous utilisez des ViewSets, vous pouvez les enregistrer ici :
# router.register('expenses', ExpenseViewSet, basename='expenses')
# router.register('categories', CategoryViewSet, basename='categories')
# router.register('budgets', BudgetViewSet, basename='budgets')


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # DRF Root Home
    path('', include(router.urls)),  # DRF default home

    # Authentication & API Endpoints
    path('register/', RegisterAPIView.as_view(), name='auth_register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/getUser/', UserProfileAPIView.as_view(), name='get_user'),
    path('api-auth/', include('rest_framework.urls')),  # Login/logout for DRF

    # Include other endpoints directly
    path('api/expenses/', ExpenseListCreateAPIView.as_view(), name='expense-list'),
    path('api/expenses/<int:pk>/', ExpenseRetrieveUpdateDestroyAPIView.as_view(), name='expense-detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', CategoryRetrieveAPIView.as_view(), name='category-detail'),
    path('api/budgets/', BudgetListCreateAPIView.as_view(), name='budget-list'),
    path('api/budgets/<int:pk>/', BudgetRetrieveUpdateDestroyAPIView.as_view(), name='budget-detail'),
]
