from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.http import HttpResponse
from django.db.models import Sum
from django.utils.timezone import now
from core.models import Customer, Loan
from core.serializers import (
    CustomerSerializer,
    LoanSerializer,
    EligibilityInputSerializer,
    LoanDetailSerializer
)
from .tasks import process_credit_application
import math

# Home page view
from django.shortcuts import render
def home(request):
    return render(request, 'core/home.html')


class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data.copy()

        monthly_income = data.get('monthly_income')
        if monthly_income is None:
            return Response({"error": "Monthly income is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            monthly_income = float(monthly_income)
        except ValueError:
            return Response({"error": "Monthly income must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        if 'approved_limit' not in data:
            approved_limit = round((36 * monthly_income) / 100000) * 100000
            data['approved_limit'] = approved_limit

        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            try:
                customer = serializer.save()
                return Response({
                    "message": "Customer registered successfully.",
                    "customer_id": customer.customer_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Error saving customer: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CheckEligibilityView(APIView):
    def post(self, request):
        input_serializer = EligibilityInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = input_serializer.validated_data
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        # Validations
        if loan_amount <= 0 or interest_rate <= 0 or tenure <= 0:
            return Response({
                "error": "Loan amount, interest rate, and tenure must all be greater than zero."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Past loans and credit score calculation
        past_loans = Loan.objects.filter(customer=customer)

        on_time_ratio = 1
        if past_loans.exists():
            paid_on_time = past_loans.filter(emis_paid_on_time=True).count()
            on_time_ratio = paid_on_time / past_loans.count()

        num_loans = past_loans.count()
        current_year_loans = past_loans.filter(start_date__year=now().year).count()
        total_loan_volume = past_loans.aggregate(total=Sum('loan_amount'))['total'] or 0
        current_loans_amount = past_loans.filter(end_date__gte=now()).aggregate(total=Sum('loan_amount'))['total'] or 0

        credit_score = 0
        reason = ""

        if current_loans_amount > customer.approved_limit:
            credit_score = 0
            reason = "Current loans exceed approved limit."
        else:
            credit_score = min(100, int(
                on_time_ratio * 50 +
                (1 / (num_loans + 1)) * 30 +
                (10 if current_year_loans > 0 else 0) +
                (10 if customer.approved_limit > total_loan_volume else 0)
            ))

        total_emis = past_loans.filter(end_date__gte=now()).aggregate(total=Sum('monthly_installment'))['total'] or 0
        if total_emis > 0.5 * customer.monthly_income:
            credit_score = 0
            reason = "Total EMIs exceed 50% of income."

        # Loan approval rules
        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval = True
            else:
                corrected_interest_rate = 16
                reason = "Credit score low; interest rate adjusted to 16%."
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval = True
            else:
                corrected_interest_rate = 20
                reason = "Credit score very low; interest rate adjusted to 20%."
        else:
            approval = False
            if not reason:
                reason = "Credit score too low for approval."

        # EMI calculation
        try:
            P = float(loan_amount)
            r = float(corrected_interest_rate) / (12 * 100)
            n = int(tenure)

            emi = (P * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1) if r > 0 else P / n
            emi = round(emi, 2)
        except Exception as e:
            return Response({'error': f"Error calculating EMI: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        if emi > 0.5 * customer.monthly_income:
            return Response({
                'approval': False,
                'reason': "EMI exceeds 50% of income.",
                'monthly_installment': emi
            }, status=status.HTTP_200_OK)

        return Response({
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': emi,
            'credit_score': credit_score,
            'reason': reason,
        }, status=status.HTTP_200_OK)


class CreateLoanView(APIView):
    def post(self, request):
        required_fields = [
            'customer_id', 'loan_amount', 'interest_rate', 'tenure',
            'monthly_installment', 'emis_paid_on_time', 'start_date', 'end_date'
        ]

        missing_fields = [f for f in required_fields if f not in request.data]
        if missing_fields:
            return Response({
                'error': f"Missing fields: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(customer_id=request.data['customer_id'])
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            loan = Loan(
                customer=customer,
                loan_amount=request.data['loan_amount'],
                interest_rate=request.data['interest_rate'],
                tenure=request.data['tenure'],
                monthly_installment=request.data['monthly_installment'],
                emis_paid_on_time=request.data['emis_paid_on_time'],
                start_date=request.data['start_date'],
                end_date=request.data['end_date'],
            )
            loan.full_clean()  # model-level validations
            loan.save()
            return Response({'message': 'Loan created successfully.', 'loan_id': loan.loan_id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f"Error creating loan: {e}"}, status=status.HTTP_400_BAD_REQUEST)


class LoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanDetailSerializer
    lookup_field = 'loan_id'
    lookup_url_kwarg = 'loan_id'

    def get(self, request, *args, **kwargs):
        try:
            loan = self.get_object()
            serializer = self.get_serializer(loan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({"detail": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)


class CustomerLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def trigger_task(request):
    application_id = 123  # Example hardcoded ID
    process_credit_application.delay(application_id)
    return HttpResponse("Task triggered! Check Celery worker logs.")
