document.getElementById('add-note-button').addEventListener('click', function () {
    const content = document.getElementById('id_content').value;

    if (content.trim() !== '') {
        // Create a new FormData object
        const formData = new FormData();
        formData.append('content', content); // Append the note content to the form data

        // Send an AJAX request to add the note
        fetch(noteUpdateUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Note-Action": "create",
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Construct the new note element and add it to the list
                    const noteElement = document.createElement('li');
                    noteElement.innerHTML = `
                                    <div class="content">${content}</div>
                                    <div class="timestamp">${data.timestamp}</div>
                                    <button class="note-delete" 
                                            data-note-id="${data.note_id}" 
                                            data-delete-url="${noteDeleteUrl}">
                                            X
                                    </button>`;
                    const noteList = document.querySelector('.order-note-list');
                    noteList.appendChild(noteElement);

                    // Clear the note content input field
                    document.getElementById('id_content').value = '';

                    // Reload the page to reflect the note addition
                    location.reload();
                } else {
                    console.error("Error adding note:", data.error);
                }
            })
            .catch(error => {
                console.error("Error adding note:", error);
            });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Add an event listener for the "X" buttons
    document.querySelectorAll('.note_delete').forEach(function (button) {
        button.addEventListener('click', function (event) { // Add 'event' as a parameter
            event.preventDefault(); // Prevent the default form submission

            const noteId = button.getAttribute('data-note-id');
            const deleteUrl = button.getAttribute('data-delete-url');

            // Create a new FormData object
            const formData = new FormData();
            formData.append('note_id', noteId); // Append the note_id to the form data

            // Debugging: Log the URL and noteId to the console
            console.log('Delete URL:', deleteUrl);
            console.log('Note ID:', noteId);

            // Send an AJAX request to delete the note with the note_id
            fetch(deleteUrl, {
                method: "POST",
                body: formData, // Send the note_id in the request body
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error("Network response was not ok.");
                    }
                })
                .then(data => {
                    if (data.success) {
                        // Remove the deleted note element from the DOM
                        const noteElement = button.closest('li');
                        noteElement.remove();
                    } else {
                        console.error("Error deleting note:", data.error);
                    }
                })
                .catch(error => {
                    console.error("Error deleting note:", error);
                });
        });
    });
});

// Function to get the CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}