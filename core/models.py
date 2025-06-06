# models.py
from django.db import models
from django.core.exceptions import ValidationError

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    age = models.IntegerField()
    monthly_income = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if self.age < 18:
            raise ValidationError({'age': 'Customer ki age kam se kam 18 honi chahiye.'})
        if self.monthly_income <= 0:
            raise ValidationError({'monthly_income': 'Monthly income 0 se zyada honi chahiye.'})

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField()
    tenure = models.IntegerField()
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer}"

    def clean(self):
        if self.loan_amount <= 0:
            raise ValidationError({'loan_amount': 'Loan amount positive number hona chahiye.'})
        if self.tenure <= 0:
            raise ValidationError({'tenure': 'Tenure kam se kam 1 month hona chahiye.'})
        if self.interest_rate <= 0:
            raise ValidationError({'interest_rate': 'Interest rate positive hona chahiye.'})
