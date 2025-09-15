
from django.urls import path
from .views import (
    RegisterCustomerView,
    CheckEligibilityView,
    CreateLoanView,
    LoanDetailView,
    CustomerLoansView,
    trigger_task,
    home
)

urlpatterns = [
    path('', home, name='home'),
    path('register-customer/', RegisterCustomerView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('loan/<int:loan_id>/', LoanDetailView.as_view(), name='loan-detail'),
    path('customer-loans/<int:customer_id>/', CustomerLoansView.as_view(), name='customer-loans'),
    path('trigger-task/', trigger_task, name='trigger-task'),
]
