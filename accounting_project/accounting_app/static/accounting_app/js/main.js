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

                setTimeout(() => { highlightTransaction(transactionId, false); }, 500);
                // setTimeout(function(){
                    
                // },2000);
            }
        });
    });

    function highlightTransaction(transactionId, add) {
        const matchingRows = document.querySelectorAll(`[data-transaction-id="${transactionId}"]`);

        matchingRows.forEach(match => {
            if (add) {
                match.classList.add('highlight');
            } else {
                setTimeout(2000);
                match.classList.remove('highlight');
            }
        });
    }
});