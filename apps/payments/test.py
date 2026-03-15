# apps/payments/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from apps.accounts.models import Wallet
from apps.payments.models import Transaction

User = get_user_model()

class AirtimePurchaseTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone_number='08012345678',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('1000.00'))
        self.client.force_authenticate(user=self.user)

    def test_airtime_purchase_success(self):
        response = self.client.post('/api/payments/airtime/purchase/', {
            'phone_number': '08012345678',
            'network': 'MTN',
            'amount': '500.00'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.count(), 1)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('500.00'))

    def test_airtime_purchase_insufficient_balance(self):
        response = self.client.post('/api/payments/airtime/purchase/', {
            'phone_number': '08012345678',
            'network': 'MTN',
            'amount': '2000.00'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1000.00'))