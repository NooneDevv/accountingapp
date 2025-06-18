from django.db import models
from django.db.models import Sum
from django.utils import timezone

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('ASSET', 'Aktywa'),
        ('LIABILITY', 'Pasywa - Zobowiązania i rezerwy na zobowiązania'),
        ('EQUITY', 'Pasywa - Kapitał własny'),
        ('EXPENSE', 'Koszty'),
        ('REVENUE', 'Przychody'),
    ]


    NORMAL_BALANCE_CHOICES = [
        ('DEBIT', 'Debet'),
        ('CREDIT', 'Kredyt'),
    ]

    account_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    normal_balance = models.CharField(max_length=6, choices=NORMAL_BALANCE_CHOICES, default='DEBIT')

    def __str__(self):
        return self.name

    def get_balance(self, end_date=None):
        debits_qs = self.debit_transactions
        credits_qs = self.credit_transactions

        if end_date:
            debits_qs = debits_qs.filter(date__lte=end_date)
            credits_qs = credits_qs.filter(date__lte=end_date)

        debit_total = debits_qs.aggregate(total=Sum('amount'))['total'] or 0.00
        credit_total = credits_qs.aggregate(total=Sum('amount'))['total'] or 0.00
        
        debit_total = float(debit_total)
        credit_total = float(credit_total)

        if self.normal_balance == 'DEBIT':
            return debit_total - credit_total
        else: 
            return credit_total - debit_total

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    debit_account = models.ForeignKey(
        Account, related_name='debit_transactions', on_delete=models.CASCADE
    )
    credit_account = models.ForeignKey(
        Account, related_name='credit_transactions', on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount}"