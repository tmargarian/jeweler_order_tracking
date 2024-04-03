

        // Function to toggle the disabled attribute on fields
        function toggleFieldsDisabled() {
            // Get the checkbox and the fields to be disabled
            let clientExistsSelector = document.querySelector('#id_client_already_exists');
            let clientSelector = document.querySelector('#id_client');

            let clientFields = [
                document.querySelector('#id_first_name'),
                document.querySelector('#id_last_name'),
                document.querySelector('#id_email'),
                document.querySelector('#id_phone_number'),
            ];


            let isClientExists = clientExistsSelector.value === 'True';

            // {# Disabling/Enabling Client Fields (Name/Phone/Email) #}
            clientFields.forEach(field => {field.disabled = isClientExists;});
            // {# Enabling/Disabling the Client Selector #}
            clientSelector.disabled = !isClientExists;

            // {# If we set Existing Client? to No -> Set the Client Selector and Data to nothing #}
            if (!isClientExists) {
                clientSelector.value = '';
                clientFields.forEach(field => {
                    field.value = '';
                });
            }
            console.log("toggled fields disabled");

        }

        function populateClientFields(url) {
            let clientSelector = document.querySelector('#id_client');

            let clientFields = [
                document.querySelector('#id_first_name'),
                document.querySelector('#id_last_name'),
                document.querySelector('#id_email'),
                document.querySelector('#id_phone_number'),
            ];

            if (clientSelector.value === '') {
                // {# If we set to empty client - clean the fields #}
                clientFields.forEach(field => {field.value = '';});
            } else {
                // {# If we set to existing client - fill out the fields #}
                fetch(url, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "clientId": clientSelector.value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        document.querySelector('#id_first_name').value = data.first_name;
                        document.querySelector('#id_last_name').value = data.last_name;
                        document.querySelector('#id_phone_number').value = data.phone_number;
                        document.querySelector('#id_email').value = data.email;
                    })
            }
        }


        document.addEventListener('DOMContentLoaded', function() {
            // Initially set the field states and add an event listener
            toggleFieldsDisabled();
            let clientExistsSelector = document.querySelector('#id_client_already_exists');
            clientExistsSelector.addEventListener('change', toggleFieldsDisabled);

            let clientSelector = document.querySelector('#id_client');
            clientSelector.addEventListener('change', () => populateClientFields(createOrderUrl));
        })