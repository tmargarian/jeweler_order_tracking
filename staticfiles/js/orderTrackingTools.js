import { updateURLParameter, initializeSelect2AndListeners } from './helperFunctions.js';

const selectElements = [
    {selector: '#order-status-select-multiple', paramName: 'order_status'},
    {selector: '#order-type-select-multiple', paramName: 'order_type'},
    {selector: '#client-select-multiple', paramName: 'client'}
];

// Document ready
$(document).ready(() => {
    initializeSelect2AndListeners(selectElements);

    // paginate_by element selector
    const select = document.getElementById("orderPerPageSelector");

    // Add an event listener for the change event on the select element
    select.addEventListener("change", function() {
        window.location.href = updateURLParameter('paginate_by', [select.value]);
    });
});