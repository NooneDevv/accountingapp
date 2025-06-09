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
});