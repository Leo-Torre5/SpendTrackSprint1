from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    is_default = models.BooleanField(default=False)  # For pre-defined categories

    class Meta:
        verbose_name_plural = "Categories"

class Expense(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses')
    date = models.DateField()
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)  # Added notes field
    created_at = models.DateTimeField(auto_now_add=True)
    indexes = [
        models.Index(fields=['date']),
        models.Index(fields=['user', 'category']),
    ]


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('six_month', 'Six Month'),
        ('yearly', 'Yearly'),
        ('five_year', 'Five Year'),
        ('ten_year', 'Ten Year'),
    ]
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='budget_amount_non_negative'
            )
        ]


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    REPORT_TYPE_CHOICES = [
        ('spending_trend', 'Spending Trend'),
        ('budget_vs_actual', 'Budget vs Actual'),
        ('category_breakdown', 'Category Breakdown'),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField()  # Stores filters/date ranges
    data = models.JSONField()  # Pre-computed report data