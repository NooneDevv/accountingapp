from datetime import datetime
from django import forms
from .models import Transaction, Account
import datetime

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial value for debit and credit accounts to the first available account
        first_account = Account.objects.first()
        if first_account:
            self.fields['debit_account'].initial = first_account.pk
            self.fields['credit_account'].initial = first_account.pk

        # Ensure all fields have the form-control or form-select class for Bootstrap styling
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
        # Widgets are now largely handled in __init__ for consistency, 
        # but specific ones like type='date' can be defined here or in __init__.
        # For this iteration, __init__ handles adding 'form-control' / 'form-select'.
        # The initial widget definitions from the original code are kept for reference 
        # but the __init__ loop will override/ensure the classes.
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}), # 'form-control' added by __init__
            'debit_account': forms.Select(), # 'form-select' added by __init__
            'credit_account': forms.Select(), # 'form-select' added by __init__
            'amount': forms.NumberInput(), # 'form-control' added by __init__
            'description': forms.TextInput(), # 'form-control' added by __init__
        }

class BalanceSheetDateForm(forms.Form):
    end_date = forms.DateField(initial=datetime.date.today,
                               widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))