from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db import transaction

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.email

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='NGN')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s wallet - Balance: {self.balance}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    @classmethod
    def get_wallet_for_update(cls, user_id):
        """Get wallet with select_for_update for concurrency control"""
        return cls.objects.select_for_update().get(user_id=user_id)

    def debit(self, amount):
        """Debit wallet amount with concurrency control"""
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()
        return self.balance

    def credit(self, amount):
        """Credit wallet amount"""
        self.balance += amount
        self.save()
        return self.balance