from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounts_view, name='accounts'),
    path('transactions/', views.transaction_history_view, name='transaction_history'),
    path('balance-sheet/', views.balance_sheet_view, name='balance_sheet'),
    path('add-transaction/', views.add_transaction_view, name='add_transaction'),
]