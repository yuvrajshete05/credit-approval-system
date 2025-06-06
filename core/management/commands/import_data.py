from django.core.management.base import BaseCommand
import pandas as pd
from core.models import Customer, Loan

class Command(BaseCommand):
    help = 'Import customer and loan data from Excel files'

    def handle(self, *args, **kwargs):
        customer_file = r"C:\Users\yuvraj\Desktop\credit-approval-system\credit_approval_system\credit_approval_system\customer_data.xlsx"
        loan_file = r"C:\Users\yuvraj\Desktop\credit-approval-system\credit_approval_system\credit_approval_system\loan_data.xlsx"

        customer_df = pd.read_excel(customer_file)
        customer_df.columns = customer_df.columns.str.strip()

        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['Customer ID'],
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'phone_number': row['Phone Number'],
                    'age': row['Age'],
                    'monthly_income': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                    'current_debt': row.get('Current Debt', 0),
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported customers'))

        loan_df = pd.read_excel(loan_file)
        loan_df.columns = loan_df.columns.str.strip()

        for _, row in loan_df.iterrows():
            Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer_id': row['Customer ID'],
                    'loan_amount': row['Loan Amount'],
                    'tenure': row['Tenure'],
                    'interest_rate': row['Interest Rate'],
                    'monthly_installment': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'start_date': row['Date of Approval'],
                    'end_date': row['End Date'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported loans'))
