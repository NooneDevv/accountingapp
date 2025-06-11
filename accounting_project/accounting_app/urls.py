from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounts_view, name='accounts'),
    path('transactions/', views.transaction_history_view, name='transaction_history'),
    path('balance_sheet/', views.balance_sheet_view, name='balance_sheet'),
    path('add_transaction/', views.add_transaction_view, name='add_transaction'),
    path('clear_transactions/', views.clear_all_transactions_view, name='clear_all_transactions'),
]