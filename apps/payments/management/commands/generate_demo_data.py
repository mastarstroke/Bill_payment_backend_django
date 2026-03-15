from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Wallet
from apps.payments.models import Transaction, AirtimePurchase
import random
import uuid
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate demo data for testing'

    def handle(self, *args, **kwargs):
        # Create demo user if not exists
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={
                'username': 'demo_user',
                'phone_number': '08012345678',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            
            # Create wallet
            Wallet.objects.create(user=demo_user, balance=Decimal('10000.00'))
            
            # Create some transactions
            for i in range(5):
                amount = Decimal(random.randint(100, 5000))
                Transaction.objects.create(
                    user=demo_user,
                    transaction_type='AIRTIME',
                    amount=amount,
                    reference=f"AIRTIME-{uuid.uuid4().hex[:12].upper()}",
                    status='SUCCESS',
                    description=f"Airtime purchase for 080{random.randint(11111111, 99999999)}"
                )
            
            self.stdout.write(self.style.SUCCESS('Demo data created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Demo user already exists'))