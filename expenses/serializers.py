from rest_framework import serializers
from .models import Expense, Budget, Category


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
        fields = ['id', 'amount', 'category', 'category_id', 'date', 'description', 'created_at']
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
    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_id', 'amount', 'period', 'start_date', 'end_date']
        read_only_fields = ['user']  #

    def validate(self, data):
        if data['start_date'] > data.get('end_date', data['start_date']):
            raise serializers.ValidationError("End date must be after start date")
        return data

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
