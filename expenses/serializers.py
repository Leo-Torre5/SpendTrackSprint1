from rest_framework import serializers
from .models import Expense, Budget, Category
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_default']


class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'amount', 'category', 'category_id',
            'date', 'description', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid category ID")
        return value


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'amount', 'period', 'start_date', 'end_date']
        read_only_fields = ['user']

    def validate(self, data):
        if data['start_date'] > data.get('end_date', data['start_date']):
            raise serializers.ValidationError("End date must be after start date")
        return data