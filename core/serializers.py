from rest_framework import serializers
from core.models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("Customer ki age kam se kam 18 honi chahiye.")
        return value

    def validate_monthly_income(self, value):
        if value <= 0:
            raise serializers.ValidationError("Monthly income positive value honi chahiye.")
        return value

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class EligibilityInputSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(
        error_messages={
            'required': 'Customer ID dena zaroori hai.',
            'invalid': 'Customer ID valid integer hona chahiye.'
        }
    )
    loan_amount = serializers.FloatField(
        min_value=0.01,
        error_messages={
            'required': 'Loan amount dena zaroori hai.',
            'invalid': 'Loan amount valid number hona chahiye.',
            'min_value': 'Loan amount zero ya usse zyada hona chahiye.'
        }
    )
    interest_rate = serializers.FloatField(
        min_value=0.01,
        error_messages={
            'required': 'Interest rate dena zaroori hai.',
            'invalid': 'Interest rate valid number hona chahiye.',
            'min_value': 'Interest rate zero ya usse zyada hona chahiye.'
        }
    )
    tenure = serializers.IntegerField(
        min_value=1,
        error_messages={
            'required': 'Tenure dena zaroori hai.',
            'invalid': 'Tenure valid integer hona chahiye.',
            'min_value': 'Tenure kam se kam 1 mahina hona chahiye.'
        }
    )

class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']

class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerInfoSerializer(read_only=True)  # nested serializer

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("Customer ki age kam se kam 18 honi chahiye.")
        return value

    def validate_monthly_income(self, value):
        if value <= 0:
            raise serializers.ValidationError("Monthly income positive value honi chahiye.")
        return value
