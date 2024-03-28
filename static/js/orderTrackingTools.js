// Function to initialize Select2 and set up change listeners
const initializeSelect2AndListeners = () => {
    const selectElements = [
        {selector: '#order-status-select-multiple', paramName: 'order_status'},
        {selector: '#order-type-select-multiple', paramName: 'order_type'},
        {selector: '#client-select-multiple', paramName: 'client'}
        // Add more selectors and parameter names as needed
    ];

    selectElements.forEach(({selector, paramName}) => {
        const $select = $(selector).select2(); // Initialize Select2

        // Set initial value from URL parameters
        const params = new URLSearchParams(window.location.search);
        const values = params.getAll(paramName);
        if (values) {
            $select.val(values).trigger('change');
        }

        // Update URL on change
        $select.on('change', () => {
            const selectedValues = $select.val() || [];
            const newUrl = updateURLParameter(paramName, selectedValues);
            window.location.href = newUrl;
        });
    });
};

// Function to update URL parameters
const updateURLParameter = (paramName, newValues) => {
    // Clone 'params' to avoid modifying the global state
    const updatedParams = new URLSearchParams(window.location.search);
    updatedParams.delete(paramName)
    newValues.forEach(value => updatedParams.append(paramName, value));
    updatedParams.delete('page'); // Reset pagination
    return `${window.location.pathname}?${updatedParams.toString()}`;
};


// Document ready
$(document).ready(() => {
    initializeSelect2AndListeners();

    // paginate_by element selector
    const select = document.getElementById("orderPerPageSelector");

    // Add an event listener for the change event on the select element
    select.addEventListener("change", function() {
      const newUrl = updateURLParameter('paginate_by', [select.value]);
      window.location.href = newUrl;
    });
});