document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const submitButton = document.getElementById('submit-button');

    form.addEventListener('submit', function () {
        submitButton.setAttribute('disabled', 'disabled');
        submitButton.value = 'Processing...'; // Optional: Change button text
    });
});