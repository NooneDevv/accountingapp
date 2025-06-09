from django.db import models

from django.db.models import Sum, Q
from django.utils import timezone

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('ASSET', 'Aktywa'),
        ('LIABILITY', 'Pasywa - Zobowiązania i rezerwy na zobowiązania'),
        ('EQUITY', 'Pasywa - Kapitał własny'),
    ]


    ACCOUNT_NAMES = [
        # Aktywa Trwałe (A)
        ('Wartości niematerialne i prawne', 'ASSET'),
        ('Rzeczowe aktywa trwałe', 'ASSET'),
        ('Należności długoterminowe', 'ASSET'),
        ('Inwestycje długoterminowe', 'ASSET'),
        ('Długoterminowe rozliczenia międzyokresowe', 'ASSET'),
        # Aktywa Obrotowe (B) todo
        ('Zapasy', 'ASSET'),
        ('Należności krótkoterminowe', 'ASSET'),
        ('Inwestycje krótkoterminowe', 'ASSET'),
        ('Krótkoterminowe rozliczenia międzyokresowe', 'ASSET'),
        # Kapitał własny (A)
        ('Kapitał (fundusz) podstawowy', 'EQUITY'),
        ('Kapitał (fundusz) zapasowy', 'EQUITY'),
        
        ('Kapitał (fundusz) z aktualizacji wyceny', 'EQUITY'),
        ('Pozostałe kapitały (fundusze) rezerwowe', 'EQUITY'),
        ('Zysk (strata) z lat ubiegłych', 'EQUITY'),
        ('Zysk (strata) netto', 'EQUITY'),
        ('Odpisy z zysku netto w ciągu roku obrotowego', 'EQUITY'),
        # Zobowiązania i rezerwy na zobowiązania (B)
        ('Rezerwy na zobowiązania', 'LIABILITY'),
        ('Zobowiązania długoterminowe', 'LIABILITY'),
        ('Zobowiązania krótkoterminowe', 'LIABILITY'),
        ('Rozliczenia międzyokresowe', 'LIABILITY'),
    ]
        #assignment
        
         # ('Urządzenia techniczne i maszyny', 'ASSET'),
        # ('Umorzenie urządzeń technicznych i maszyn', 'ASSET'),
            # ('Środki transportu', 'ASSET'),
        # ('Umorzenie środków transportu', 'ASSET'), 
        # ('Należności z tytułu dostaw i usług od pozostałych jednostek do 12 m-cy', 'ASSET'),
        # ('Środki pieniężne w kasie', 'ASSET'),
        # ('Środki pieniężne na r-kach bankowych', 'ASSET'),
        
        # ('Kapitał podstawowy', 'EQUITY'),
        # ('Zysk (strata) netto', 'EQUITY'),
        # ('Zobowiązania z tytułu dostaw i usług wobec pozostałych jednostek do 12 m-cy', 'LIABILITY'),
        # ('Kredyty bankowe krótkoterminowe', 'LIABILITY'),
        # ('Zobowiązania z tytułu wynagrodzeń', 'LIABILITY'),
        # ('Zobowiązania z tytułu publicznoprawnych', 'LIABILITY')

    account_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)

    def __str__(self):
        return self.name

    def get_balance(self, end_date=None):
        """
        Balance = (Sum of Debits) - (Sum Credits) for ASSET
        Balance = (Sum Credits) - (Sum Debits) for LIABILITY and EQUITY
        """
        debits = self.debit_transactions.filter(date__lte=end_date) if end_date else self.debit_transactions.all()
        credits = self.credit_transactions.filter(date__lte=end_date) if end_date else self.credit_transactions.all()

        debit_total = float(debits.aggregate(Sum('amount'))['amount__sum'] or 0.00)
        credit_total = float(credits.aggregate(Sum('amount'))['amount__sum'] or 0.00)

        if self.account_type == 'ASSET':
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