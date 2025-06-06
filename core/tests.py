from django.test import TestCase, Client
from django.urls import reverse
from core.models import Customer
import json

class CheckEligibilityViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('check_eligibility')
        cls.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            age=30,
            monthly_income=70000,
            approved_limit=100000
        )

    def test_post_valid_data(self):
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 50000.0,
            "interest_rate": 10.0,
            "tenure": 12
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()

        self.assertIn('approval', response_json)
        self.assertIsInstance(response_json['approval'], bool)
        self.assertIn('monthly_installment', response_json)
        self.assertGreaterEqual(response_json['monthly_installment'], 0)

    def test_post_invalid_loan_amount(self):
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": -1000,  # invalid negative loan amount
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Loan amount must be greater than 0.')

    def test_post_invalid_customer_id(self):
        # Using a non-existent integer customer_id (but valid integer type)
        data = {
            "customer_id": 999999,  # Assuming this ID doesn't exist
            "loan_amount": 50000.0,
            "interest_rate": 12.0,
            "tenure": 12
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)  # Expecting 404 because customer not found
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Customer not found')







# from django.test import TestCase, Client
# from django.urls import reverse
# from core.models import Customer

# class CheckEligibilityViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('check_eligibility')

#         # Create a customer to use in tests
#         self.customer = Customer.objects.create(
#             first_name="Test",
#             last_name="User",
#             phone_number="1234567890",
#             age=30,
#             monthly_income=70000,
#             approved_limit=100000
#         )

#     def test_post_valid_data(self):
#         data = {
#             "customer_id": self.customer.customer_id,
#             "loan_amount": 50000.0,
#             "interest_rate": 15.0,
#             "tenure": 12
#         }
#         response = self.client.post(self.url, data, content_type='application/json')
#         self.assertEqual(response.status_code, 200)

#         # Example: Check that the response contains the 'approval' key
#         self.assertIn('approval', response.json())

#     def test_post_invalid_data(self):
#         # Missing required fields or invalid values
#         data = {
#             "customer_id": self.customer.customer_id,
#             "loan_amount": -1000,  # invalid negative loan_amount
#             # interest_rate and tenure missing
#         }
#         response = self.client.post(self.url, data, content_type='application/json')
#         self.assertEqual(response.status_code, 400)


