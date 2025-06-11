from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from .models import Account, Transaction

class AccountingLogicTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cash_account = Account.objects.get(name='Środki pieniężne w kasie')
        cls.equipment_account = Account.objects.get(name='Urządzenia techniczne i maszyny')
        cls.amortyzacja_expense_account = Account.objects.get(name='Amortyzacja')
        cls.umorzenie_equipment_account = Account.objects.get(name='Umorzenie urządzeń technicznych i maszyn')
        cls.accounts_payable = Account.objects.get(name='Zobowiązania z tytułu dostaw i usług wobec pozostałych jednostek do 12 m-cy')

    def test_asset_purchase_on_credit(self):
        Transaction.objects.create(
            debit_account=self.equipment_account,
            credit_account=self.accounts_payable,
            amount=Decimal('5000.00'),
            date=timezone.now(),
            description='Zakup urządzeń na kredyt'
        )
        self.assertEqual(self.equipment_account.get_balance(), Decimal('5000.00'))
        self.assertEqual(self.accounts_payable.get_balance(), Decimal('5000.00'))

    def test_amortization_transaction(self):
        Transaction.objects.create(
            debit_account=self.amortyzacja_expense_account,
            credit_account=self.umorzenie_equipment_account,
            amount=Decimal('1000.00'),
            date=timezone.now(),
            description='Amortyzacja urządzeń'
        )
        self.assertEqual(self.amortyzacja_expense_account.get_balance(), Decimal('1000.00'))
        self.assertEqual(self.umorzenie_equipment_account.get_balance(), Decimal('1000.00'))

    def test_cash_payment_for_liability(self):
        Transaction.objects.create(
            debit_account=self.accounts_payable,
            credit_account=self.cash_account,
            amount=Decimal('2000.00'),
            date=timezone.now(),
            description='Spłata zobowiązania gotówką'
        )
        self.assertEqual(self.accounts_payable.get_balance(), Decimal('-2000.00'))
        self.assertEqual(self.cash_account.get_balance(), Decimal('-2000.00'))

    def test_multiple_transactions_balance_check(self):
        Transaction.objects.create(debit_account=self.equipment_account, credit_account=self.accounts_payable, amount=Decimal('300.00'), date=timezone.now(), description='T1')
        Transaction.objects.create(debit_account=self.amortyzacja_expense_account, credit_account=self.umorzenie_equipment_account, amount=Decimal('50.00'), date=timezone.now(), description='T2')
        Transaction.objects.create(debit_account=self.accounts_payable, credit_account=self.cash_account, amount=Decimal('100.00'), date=timezone.now(), description='T3')

        self.assertEqual(self.equipment_account.get_balance(), Decimal('300.00'))
        self.assertEqual(self.accounts_payable.get_balance(), Decimal('200.00')) # 300 Credit - 100 Debit
        self.assertEqual(self.amortyzacja_expense_account.get_balance(), Decimal('50.00'))
        self.assertEqual(self.umorzenie_equipment_account.get_balance(), Decimal('50.00'))
        self.assertEqual(self.cash_account.get_balance(), Decimal('-100.00'))
