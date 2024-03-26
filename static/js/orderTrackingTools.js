/* Enable Select2 Boxes */
function updateURLParameter(paramName, newValues) {
    // Remove the parameter if it exists
    params.delete(paramName);

    // Add new values for the parameter
    newValues.forEach(value => params.append(paramName, value));

    // Reset pagination
    params.delete('page');

    // Construct the new URL
    return `${window.location.pathname}?${params.toString()}`;
}

$(document).ready(function() {
        $('#order-status-select-multiple').select2();
        $('#order-type-select-multiple').select2();
    });

// Get all order statuses and types from GET
const params = new URLSearchParams(window.location.search);
const orderStatuses = params.getAll('order_status');
const orderTypes = params.getAll('order_type');

// If there are order statuses or types in GET -> update elements
if (orderStatuses) {
    $('#order-status-select-multiple').val(orderStatuses).trigger('change');
}

if (orderTypes) {
    $('#order-type-select-multiple').val(orderTypes).trigger('change');
}

// On change of the element - update URL parameter instead of form submission
$('#order-status-select-multiple').on('change', function() {
    const selectedStatuses = $(this).val() || [];
    const newUrl = updateURLParameter('order_status', selectedStatuses);
    window.location.href = newUrl; // Navigate to the new URL
});

$('#order-type-select-multiple').on('change', function() {
    const selectedTypes = $(this).val() || [];
    const newUrl = updateURLParameter('order_type', selectedTypes);
    window.location.href = newUrl; // Navigate to the new URL
});

// paginate_by element selector
const select = document.getElementById("orderPerPageSelector");

// Add an event listener for the change event on the select element
select.addEventListener("change", function() {
  const newUrl = updateURLParameter('paginate_by', [select.value]);
  window.location.href = newUrl;
});