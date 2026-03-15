# apps/payments/serializers.py
from rest_framework import serializers
from django.db import transaction as db_transaction
from django.utils import timezone
import uuid
from decimal import Decimal
from .models import Transaction, AirtimePurchase, WalletFunding
from apps.accounts.models import Wallet

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'reference', 
                 'status', 'description', 'metadata', 'created_at']
        read_only_fields = ['reference', 'status', 'created_at']

class AirtimePurchaseSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    network = serializers.ChoiceField(choices=AirtimePurchase.NETWORK_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, 
                                     min_value=Decimal('50.00'))
    is_pin_based = serializers.BooleanField(default=False)

    def validate_amount(self, value):
        if value < 50:
            raise serializers.ValidationError("Minimum airtime amount is 50")
        if value > 50000:
            raise serializers.ValidationError("Maximum airtime amount is 50000")
        return value

    def validate_phone_number(self, value):
        # Basic phone number validation
        if not value.startswith('0') or len(value) != 11:
            raise serializers.ValidationError("Invalid phone number format")
        return value

class WalletFundingSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2,
                                     min_value=Decimal('100.00'))
    funding_method = serializers.ChoiceField(choices=WalletFunding.FUNDING_METHODS)
    provider_reference = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value > 1000000:
            raise serializers.ValidationError("Maximum funding amount is 1,000,000")
        return value