from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction, models
from django.utils import timezone
import uuid
from decimal import Decimal
from .models import Transaction, AirtimePurchase, WalletFunding
from .serializers import (
    TransactionSerializer, 
    AirtimePurchaseSerializer,
    WalletFundingSerializer
)
from apps.accounts.models import Wallet

class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class AirtimePurchaseView(generics.GenericAPIView):
    serializer_class = AirtimePurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = request.user
        amount = data['amount']
        
        # Get wallet with select_for_update for concurrency control
        try:
            wallet = Wallet.objects.select_for_update().get(user=user)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check sufficient balance
        if wallet.balance < amount:
            return Response(
                {"error": "Insufficient balance"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique reference
        reference = f"AIRTIME-{uuid.uuid4().hex[:12].upper()}"
        
        # Create transaction record
        transaction_record = Transaction.objects.create(
            user=user,
            transaction_type='AIRTIME',
            amount=amount,
            reference=reference,
            status='PENDING',
            description=f"Airtime purchase for {data['phone_number']}",
            metadata={
                'phone_number': data['phone_number'],
                'network': data['network'],
                'is_pin_based': data['is_pin_based']
            }
        )
        
        # Debit wallet
        wallet.balance -= amount
        wallet.save()
        
        # Simulate airtime purchase (in real app, call external API)
        # For demo, we'll assume success
        try:
            # Simulate API call to telecom provider
            airtime_purchase = AirtimePurchase.objects.create(
                user=user,
                transaction=transaction_record,
                phone_number=data['phone_number'],
                network=data['network'],
                amount=amount,
                is_pin_based=data['is_pin_based'],
                pin="1234" if data['is_pin_based'] else ""  # Demo PIN
            )
            
            # Update transaction status
            transaction_record.status = 'SUCCESS'
            transaction_record.save()
            
            return Response({
                "status": "success",
                "message": "Airtime purchased successfully",
                "data": {
                    "reference": reference,
                    "amount": str(amount),
                    "phone_number": data['phone_number'],
                    "network": data['network'],
                    "new_balance": str(wallet.balance),
                    "pin": airtime_purchase.pin if data['is_pin_based'] else None
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # If airtime purchase fails, reverse the transaction
            transaction_record.status = 'FAILED'
            transaction_record.save()
            
            # Reverse the debit
            wallet.balance += amount
            wallet.save()
            
            return Response(
                {"error": f"Airtime purchase failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WalletFundingView(generics.GenericAPIView):
    serializer_class = WalletFundingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = request.user
        amount = data['amount']
        
        # Get wallet with select_for_update
        try:
            wallet = Wallet.objects.select_for_update().get(user=user)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate unique reference
        reference = f"FUND-{uuid.uuid4().hex[:12].upper()}"
        
        # Create transaction record
        transaction_record = Transaction.objects.create(
            user=user,
            transaction_type='DEPOSIT',
            amount=amount,
            reference=reference,
            status='PENDING',
            description=f"Wallet funding via {data['funding_method']}",
            metadata={
                'funding_method': data['funding_method'],
                'provider_reference': data.get('provider_reference', '')
            }
        )
        
        # Create wallet funding record
        wallet_funding = WalletFunding.objects.create(
            user=user,
            transaction=transaction_record,
            amount=amount,
            funding_method=data['funding_method'],
            provider_reference=data.get('provider_reference', '')
        )
        
        # In a real app, initiate payment with payment gateway
        # For demo, we'll simulate successful payment
        wallet.balance += amount
        wallet.save()
        
        # Update records
        transaction_record.status = 'SUCCESS'
        transaction_record.save()
        
        wallet_funding.is_verified = True
        wallet_funding.verified_at = timezone.now()
        wallet_funding.save()
        
        return Response({
            "status": "success",
            "message": "Wallet funded successfully",
            "data": {
                "reference": reference,
                "amount": str(amount),
                "funding_method": data['funding_method'],
                "new_balance": str(wallet.balance)
            }
        }, status=status.HTTP_200_OK)

class WalletBalanceView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = request.user.wallet
        return Response({
            "balance": str(wallet.balance),
            "currency": wallet.currency,
            "last_updated": wallet.updated_at
        })