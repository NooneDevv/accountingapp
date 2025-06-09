document.addEventListener('DOMContentLoaded', function() {
    const transactionRows = document.querySelectorAll('.transaction-row');

    transactionRows.forEach(row => {
        row.addEventListener('mouseover', function() {
            const transactionId = this.dataset.transactionId;
            if (transactionId) {
                highlightTransaction(transactionId, true);
            }
        });

        row.addEventListener('mouseout', function() {
            const transactionId = this.dataset.transactionId;
            if (transactionId) {
                highlightTransaction(transactionId, false);
            }
        });
    });

    function highlightTransaction(transactionId, add) {
        const matchingRows = document.querySelectorAll(`[data-transaction-id="${transactionId}"]`);

        matchingRows.forEach(match => {
            if (add) {
                match.classList.add('highlight');
                // match.style.backgroundColor = 'grey'; // Light blue background
                // match.backgroundColor = '#f0f8ff'; // Light blue background
            } else {
                match.classList.remove('highlight');
            }
        });
    }

    // New functionality for Add Transaction Modal
    const addTransactionModal = document.getElementById('addTransactionModal');
    if (addTransactionModal) {
        const debitAccountSelect = addTransactionModal.querySelector('#id_debit_account'); // Django default ID
        const debitAccountFundsDiv = addTransactionModal.querySelector('#debitAccountFunds');
        const balanceUrl = addTransactionModal.dataset.balanceUrl; // Get URL from data attribute

        function fetchAndDisplayBalance(accountId) {
            if (!accountId || !balanceUrl) { // Also check if balanceUrl is available
                debitAccountFundsDiv.innerHTML = '';
                return;
            }
            
            fetch(`${balanceUrl}?account_id=${accountId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        debitAccountFundsDiv.innerHTML = `<span class="text-danger">Error: ${data.error}</span>`;
                    } else {
                        debitAccountFundsDiv.innerHTML = `Available funds: <strong class="${data.balance < 0 ? 'text-danger' : 'text-success'}">${parseFloat(data.balance).toFixed(2)} PLN</strong>`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching account balance:', error);
                    debitAccountFundsDiv.innerHTML = '<span class="text-danger">Could not fetch balance.</span>';
                });
        }

        if (debitAccountSelect && debitAccountFundsDiv) {
            // Event listener for when the debit account selection changes
            debitAccountSelect.addEventListener('change', function() {
                fetchAndDisplayBalance(this.value);
            });

            // Event listener for when the modal is shown, to load initial balance
            addTransactionModal.addEventListener('shown.bs.modal', function () {
                fetchAndDisplayBalance(debitAccountSelect.value);
            });
        }
    }
});