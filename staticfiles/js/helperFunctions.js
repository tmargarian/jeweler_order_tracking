// Function to update URL parameters
export const updateURLParameter = (paramName, newValues) => {
    // Clone 'params' to avoid modifying the global state
    const updatedParams = new URLSearchParams(window.location.search);
    updatedParams.delete(paramName)
    newValues.forEach(value => updatedParams.append(paramName, value));
    updatedParams.delete('page'); // Reset pagination
    return `${window.location.pathname}?${updatedParams.toString()}`;
};


// Function to initialize Select2 and set up change listeners
export const initializeSelect2AndListeners = (selectElements) => {
    // selectElements must be an array of objects with 'selector' class and 'paramName' Get attributes
    // Example:
    // const selectElements = [
    //     {selector: '#order-status-select-multiple', paramName: 'order_status'},
    //     {selector: '#order-type-select-multiple', paramName: 'order_type'},
    //     {selector: '#client-select-multiple', paramName: 'client'}
    // ];
    selectElements.forEach(({selector, paramName}) => {
        const $select = $(selector).select2({theme: "bootstrap-5"}); // Initialize Select2

        // Set initial value from URL parameters
        const params = new URLSearchParams(window.location.search);
        const values = params.getAll(paramName);
        if (values) {
            $select.val(values).trigger('change');
        }

        // Update URL on change
        $select.on('change', () => {
            const selectedValues = $select.val() || [];
            window.location.href = updateURLParameter(paramName, selectedValues);
        });
    });
};