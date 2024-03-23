// Get the select element
let select = document.getElementById("orderPerPageSelector");

// Get the form element
let form = document.getElementById("orderListPaginatorForm");

// Add an event listener for the change event on the select element
select.addEventListener("change", function() {
  // Submit the form when the select value changes
  form.submit();
});