document.querySelectorAll('.order-status-table-cell')
    .forEach(orderStatusDiv => {
        const orderStatus = orderStatusDiv.textContent;
        if (orderStatus === 'In Progress') {
            orderStatusDiv.style.backgroundColor = 'darkgoldenrod';
        } else if (orderStatus === 'Completed') {
            orderStatusDiv.style.backgroundColor = 'darkgreen';
        } else if (orderStatus === 'Cancelled') {
            orderStatusDiv.style.backgroundColor = 'darkred';
        }
    });