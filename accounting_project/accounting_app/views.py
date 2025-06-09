from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Account, Transaction
from .forms import TransactionForm, BalanceSheetDateForm
from datetime import date
from django.utils import timezone
from django.http import JsonResponse

def accounts_view(request):
    accounts = Account.objects.all().order_by('name')
    account_types = Account.ACCOUNT_TYPES

    grouped_accounts = {
        key: {'verbose_name': verbose, 'accounts': []} for key, verbose in account_types
    }

    for account in accounts:
        debit_total = account.debit_transactions.aggregate(total=Sum('amount'))['total'] or 0
        credit_total = account.credit_transactions.aggregate(total=Sum('amount'))['total'] or 0
        
        account.debit_total = debit_total
        account.credit_total = credit_total
        account.balance = account.get_balance()
        
        if account.account_type in grouped_accounts:
            grouped_accounts[account.account_type]['accounts'].append(account)

    context = {
        'grouped_accounts': grouped_accounts
    }
    return render(request, 'accounting_app/accounts.html', context)

def transaction_history_view(request):
    transactions = Transaction.objects.all().order_by('-date')
    context = {
        'transactions': transactions
    }
    return render(request, 'accounting_app/transaction_history.html', context)

def balance_sheet_view(request):
    form = BalanceSheetDateForm()
    context = {'form': form}

    if request.method == 'POST':
        form = BalanceSheetDateForm(request.POST)
        if form.is_valid():
            end_date = form.cleaned_data['end_date']
            
            def get_bal(name):
                try:
                    return Account.objects.get(name=name).get_balance(end_date)
                except Account.DoesNotExist:
                    print(name)
                    return 0

            aktywa_trwale_I = get_bal('Urządzenia techniczne i maszyny')
            aktywa_trwale_II = get_bal('Środki transportu')
            aktywa_trwale_III = get_bal('Umorzenie urządzeń technicznych i maszyn')
            aktywa_trwale_IV = get_bal('Umorzenie środków transportu')
            aktywa_trwale_total = sum([aktywa_trwale_I, aktywa_trwale_II, aktywa_trwale_III, aktywa_trwale_IV])
            
            aktywa_obrotowe_I = get_bal('Należności z tytułu dostaw i usług od pozostałych jednostek do 12 m-cy')
            aktywa_obrotowe_II = get_bal('Środki pieniężne w kasie')
            aktywa_obrotowe_III = get_bal('Środki pieniężne na r-kach bankowych')
            aktywa_obrotowe_total = sum([aktywa_obrotowe_I, aktywa_obrotowe_II, aktywa_obrotowe_III])

            total_assets = aktywa_trwale_total + aktywa_obrotowe_total

            kapital_wlasny_I = get_bal('Kapitał (fundusz) podstawowy')
            kapital_wlasny_II = get_bal('Zysk (strata) netto')
            
            kapital_wlasny_total = kapital_wlasny_I + kapital_wlasny_II

            zobowiazania_I = get_bal('Zobowiązania z tytułu dostaw i usług wobec pozostałych jednostek do 12 m-cy')
            zobowiazania_II = get_bal('Kredyty bankowe krótkoterminowe')
            zobowiazania_III = get_bal('Zobowiązania z tytułu publicznoprawnych')
            zobowiazania_IV = get_bal('Zobowiązania z tytułu wynagrodzeń')
            
            zobowiazania_total = sum([zobowiazania_I, zobowiazania_II, zobowiazania_III, zobowiazania_IV])
            
            total_liabilities_and_equity = kapital_wlasny_total + zobowiazania_total
            print(total_liabilities_and_equity)
            context['end_date_str'] = end_date.strftime('%Y-%m-%d')
            context['balance_sheet_data'] = {
                'A': { 'total': aktywa_trwale_total, 'I': aktywa_trwale_I, 'II': aktywa_trwale_II, 'III': aktywa_trwale_III, 'IV': aktywa_trwale_IV },
                'B': { 'total': aktywa_obrotowe_total, 'I': aktywa_obrotowe_I, 'II': aktywa_obrotowe_II, 'III': aktywa_obrotowe_III},
                'total_assets': total_assets,
                'P_A': { 'total': kapital_wlasny_total, 'I': kapital_wlasny_I, 'II': kapital_wlasny_II },
                'P_B': { 'total': zobowiazania_total, 'I': zobowiazania_I, 'II': zobowiazania_II, 'III': zobowiazania_III, 'IV': zobowiazania_IV },
                'total_liabilities_and_equity': total_liabilities_and_equity,
            }

    return render(request, 'accounting_app/balance_sheet.html', context)

def add_transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('accounts')

def get_account_balance_view(request):
    account_id = request.GET.get('account_id')
    if not account_id:
        return JsonResponse({'error': 'Account ID not provided'}, status=400)
    try:
        account = get_object_or_404(Account, pk=account_id)
        balance = account.get_balance()
        return JsonResponse({'balance': balance})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)