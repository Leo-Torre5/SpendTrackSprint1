from rest_framework import serializers
from .models import Expense, Budget, Category
from django.db.models import Sum
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_default']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'category_id', 'date', 'description', 'notes', 'created_at']
        read_only_fields = ['created_at']

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid category ID")
        return value

    def create(self, validated_data):
        """
        Handle creating an Expense while associating it with a category.
        """
        category_id = validated_data.pop('category_id')
        validated_data['category'] = Category.objects.get(id=category_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Handle updates for Expense objects.
        """
        category_id = validated_data.pop('category_id', None)
        if category_id:
            validated_data['category'] = Category.objects.get(id=category_id)
        return super().update(instance, validated_data)


class BudgetSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Make sure it's read_only
    current_spending = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'category_id', 'amount', 'period',
                  'start_date', 'end_date', 'current_spending']
        read_only_fields = ['user']  # Explicitly mark user as read-only


    def validate(self, data):
        if data['start_date'] > data.get('end_date', data['start_date']):
            raise serializers.ValidationError("End date must be after start date")
        return data

    def get_current_spending(self, obj):
        # Implement your spending calculation logic
        # Example: sum of expenses in this budget's period
        expenses = Expense.objects.filter(
            user=obj.user,
            category=obj.category,
            date__gte=obj.start_date,
            date__lte=obj.end_date if obj.end_date else timezone.now().date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        return float(expenses)

    def validate_category_id(self, value):
        """
        Ensure the provided category_id exists.
        """
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid category ID.")
        return value

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        validated_data['category'] = Category.objects.get(id=category_id)
        return super().create(validated_data)


    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            validated_data['category'] = Category.objects.get(id=category_id)
        return super().update(instance, validated_data)
