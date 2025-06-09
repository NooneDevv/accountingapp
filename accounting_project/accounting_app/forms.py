from datetime import datetime
from django import forms
from .models import Transaction, Account
import datetime

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['debit_account', 'credit_account', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput( attrs={'type': 'date', 'class': 'form-control'}),
            'debit_account': forms.Select(attrs={'class': 'form-select'}),
            'credit_account': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BalanceSheetDateForm(forms.Form):
    end_date = forms.DateField(initial=datetime.date.today,
                               widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))