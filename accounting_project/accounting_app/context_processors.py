from .forms import TransactionForm
from .models import Transaction

def global_context(request):
    return {
        'transaction_form': TransactionForm(),
        'recent_transactions': Transaction.objects.order_by('-date')[:20]
    }