from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.TransactionHistoryView.as_view(), name='transaction-history'),
    path('wallet/balance/', views.WalletBalanceView.as_view(), name='wallet-balance'),
    path('airtime/purchase/', views.AirtimePurchaseView.as_view(), name='airtime-purchase'),
    path('wallet/fund/', views.WalletFundingView.as_view(), name='wallet-fund'),
]