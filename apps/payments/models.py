from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.accounts.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('AIRTIME', 'Airtime Purchase'),
        ('BILL_PAYMENT', 'Bill Payment'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['reference']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.reference}"

class AirtimePurchase(models.Model):
    NETWORK_CHOICES = [
        ('MTN', 'MTN Nigeria'),
        ('GLO', 'Globacom'),
        ('AIRTEL', 'Airtel Nigeria'),
        ('9MOBILE', '9mobile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='airtime_purchases')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='airtime_purchase')
    phone_number = models.CharField(max_length=15)
    network = models.CharField(max_length=10, choices=NETWORK_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pin = models.CharField(max_length=4, blank=True)
    is_pin_based = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.network} - {self.phone_number} - {self.amount}"

class WalletFunding(models.Model):
    FUNDING_METHODS = [
        ('CARD', 'Card Payment'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('USSD', 'USSD'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_fundings')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='wallet_funding')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    funding_method = models.CharField(max_length=20, choices=FUNDING_METHODS)
    provider_reference = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funding_method} - {self.amount}"