from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Account, Transaction
from .forms import TransactionForm, BalanceSheetDateForm
from datetime import date
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Helper function to remove Polish diacritics
def normalize_polish_chars(text):
    if not isinstance(text, str):
        return text
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def accounts_view(request):
    accounts = Account.objects.all().order_by('name')
    account_types = Account.ACCOUNT_TYPES

    grouped_accounts = {
        key: {'verbose_name': verbose, 'accounts': []} for key, verbose in account_types
    }

    for account in accounts:
        debit_total = account.debit_transactions.aggregate(total=Sum('amount'))['total'] or 0
        credit_total = account.credit_transactions.aggregate(total=Sum('amount'))['total'] or 0
        
        # Attach calculated values directly to the account object for the template
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
    # formatted_date = now.strftime("%d. %b %y")
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
                # Normalize account name before querying if necessary,
                # or ensure account names in DB do not use Polish chars if that's the strategy.
                # For now, assuming account names in DB are as expected by get_bal.
                try:
                    return Account.objects.get(name=name).get_balance(end_date)
                except Account.DoesNotExist:
                    print(normalize_polish_chars(name)) # Normalize for print if needed
                    return 0

            # Normalize static Polish strings when fetching balances
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
            
            total_liabilities_and_equity = kapital_wlasny_total + zobowiazania_total # Ensure this line is present and correct

            balance_sheet_data = {
                'A': { 'total': aktywa_trwale_total, 'I': aktywa_trwale_I, 'II': aktywa_trwale_II, 'III': aktywa_trwale_III, 'IV': aktywa_trwale_IV },
                'B': { 'total': aktywa_obrotowe_total, 'I': aktywa_obrotowe_I, 'II': aktywa_obrotowe_II, 'III': aktywa_obrotowe_III},
                'total_assets': total_assets,
                'P_A': { 'total': kapital_wlasny_total, 'I': kapital_wlasny_I, 'II': kapital_wlasny_II },
                'P_B': { 'total': zobowiazania_total, 'I': zobowiazania_I, 'II': zobowiazania_II, 'III': zobowiazania_III, 'IV': zobowiazania_IV },
                'total_liabilities_and_equity': total_liabilities_and_equity,
            }
            context['end_date_str'] = end_date.strftime('%Y-%m-%d')
            # Normalize data for HTML context if it also needs to be without Polish chars
            # For now, focusing on PDF as requested.
            # context['balance_sheet_data_normalized'] = { ... } # if needed for HTML too

            context['balance_sheet_data'] = balance_sheet_data


            if 'download_pdf' in request.POST:
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="balance_sheet_{end_date.strftime("%Y-%m-%d")}.pdf"'

                doc = SimpleDocTemplate(response, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Normalize PDF title and headers
                story.append(Paragraph(normalize_polish_chars(f"Bilans na dzien: {end_date.strftime('%Y-%m-%d')}"), styles['h1']))
                story.append(Spacer(1, 12))

                story.append(Paragraph(normalize_polish_chars("AKTYWA"), styles['h2']))
                data_aktywa = [
                    [normalize_polish_chars("A"), normalize_polish_chars("Aktywa trwale"), f"{balance_sheet_data['A']['total']:.2f}"],
                    [normalize_polish_chars("I"), normalize_polish_chars("Urzadzenia techniczne i maszyny"), f"{balance_sheet_data['A']['I']:.2f}"],
                    [normalize_polish_chars("II"), normalize_polish_chars("Srodki transportu"), f"{balance_sheet_data['A']['II']:.2f}"],
                    [normalize_polish_chars("III"), normalize_polish_chars("Umorzenie urzadzen technicznych i maszyn"), f"{balance_sheet_data['A']['III']:.2f}"],
                    [normalize_polish_chars("IV"), normalize_polish_chars("Umorzenie srodkow transportu"), f"{balance_sheet_data['A']['IV']:.2f}"],
                    [normalize_polish_chars("B"), normalize_polish_chars("Aktywa obrotowe"), f"{balance_sheet_data['B']['total']:.2f}"],
                    [normalize_polish_chars("I"), normalize_polish_chars("Naleznosci z tytulu dostaw i uslug od pozostalych jednostek do 12 m-cy"), f"{balance_sheet_data['B']['I']:.2f}"],
                    [normalize_polish_chars("II"), normalize_polish_chars("Srodki pieniezne w kasie"), f"{balance_sheet_data['B']['II']:.2f}"],
                    [normalize_polish_chars("III"), normalize_polish_chars("Srodki pieniezne na r-kach bankowych"), f"{balance_sheet_data['B']['III']:.2f}"],
                    ["", normalize_polish_chars("AKTYWA RAZEM"), f"{balance_sheet_data['total_assets']:.2f}"]
                ]
                table_aktywa = Table(data_aktywa, colWidths=[30, 300, 100])
                table_aktywa.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('ALIGN', (2,0), (2,-1), 'RIGHT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Using Helvetica which supports most characters
                    ('BOTTOMPADDING', (0,0), (-1,0), 12),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), 
                ]))
                story.append(table_aktywa)
                story.append(Spacer(1, 12))

                story.append(Paragraph(normalize_polish_chars("PASYWA"), styles['h2']))
                data_pasywa = [
                    [normalize_polish_chars("A"), normalize_polish_chars("Kapital wlasny"), f"{balance_sheet_data['P_A']['total']:.2f}"],
                    [normalize_polish_chars("I"), normalize_polish_chars("Kapital (fundusz) podstawowy"), f"{balance_sheet_data['P_A']['I']:.2f}"],
                    [normalize_polish_chars("II"), normalize_polish_chars("Zysk (strata) netto"), f"{balance_sheet_data['P_A']['II']:.2f}"],
                    [normalize_polish_chars("B"), normalize_polish_chars("Zobowiazania i rezerwy na zobowiazania"), f"{balance_sheet_data['P_B']['total']:.2f}"],
                    [normalize_polish_chars("I"), normalize_polish_chars("Zobowiazania z tytulu dostaw i uslug wobec pozostalych jednostek do 12 m-cy"), f"{balance_sheet_data['P_B']['I']:.2f}"],
                    [normalize_polish_chars("II"), normalize_polish_chars("Kredyty bankowe krotkoterminowe"), f"{balance_sheet_data['P_B']['II']:.2f}"],
                    [normalize_polish_chars("III"), normalize_polish_chars("Zobowiazania z tytulu publicznoprawnych"), f"{balance_sheet_data['P_B']['III']:.2f}"],
                    [normalize_polish_chars("IV"), normalize_polish_chars("Zobowiazania z tytulu wynagrodzen"), f"{balance_sheet_data['P_B']['IV']:.2f}"],
                    ["", normalize_polish_chars("PASYWA RAZEM"), f"{balance_sheet_data['total_liabilities_and_equity']:.2f}"]
                ]
                table_pasywa = Table(data_pasywa, colWidths=[30, 300, 100])
                table_pasywa.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('ALIGN', (2,0), (2,-1), 'RIGHT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 12),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ]))
                story.append(table_pasywa)
                doc.build(story)
                return response

    return render(request, 'accounting_app/balance_sheet.html', context)

def add_transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('accounts') # Redirect back to the accounts page