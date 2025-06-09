from datetime import datetime
from django import forms
from .models import Transaction, Account
import datetime

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first_account = Account.objects.first()
        if first_account:
            self.fields['debit_account'].initial = first_account.pk
            self.fields['credit_account'].initial = first_account.pk

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Transaction
        fields = ['debit_account', 'credit_account', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'debit_account': forms.Select(),
            'credit_account': forms.Select(),
            'amount': forms.NumberInput(),
            'description': forms.TextInput(),
        }

class BalanceSheetDateForm(forms.Form):
    end_date = forms.DateField(initial=datetime.date.today,
                               widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))