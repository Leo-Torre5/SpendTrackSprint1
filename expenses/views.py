from rest_framework import generics, permissions
from .models import Expense, Budget, Category
from .serializers import ExpenseSerializer, BudgetSerializer, CategorySerializer


class IsOwnerPermission(permissions.BasePermission):
    """
    Custom permission to check if the requesting user owns the resource.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to retrieve a list of expenses or create a new expense.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific expense.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.all()

class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.all()


class BudgetListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to retrieve a list of budgets or create a new budget.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific budget.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
