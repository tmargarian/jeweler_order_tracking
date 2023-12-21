function addressUpdate(url) {
    const zipCode = document
        .getElementById('id_1-zip_code')
        .value;

    fetch(url, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "zipCode": zipCode
        }
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_1-city').value = data.city;
            document.getElementById('id_1-state').value = data.state;
        });
}