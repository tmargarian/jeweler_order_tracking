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
                    // Handling the Note timestamp
                    noteElement.innerHTML = `
                                    <div class="note-content">${content}</div>
                                    <div class="note-timestamp">${localizeTimestamp(data.timestamp)}</div>
                                    <button class="note-delete" 
                                            data-note-id="${data.note_id}" 
                                            data-delete-url="/app/note_delete/${data.note_id}/">
                                            X
                                    </button>`;
                    const noteList = document.querySelector('.order-note-list');
                    noteList.appendChild(noteElement);

                    // Clear the note content input field
                    document.getElementById('id_content').value = '';

                    // Reload the page to reflect the note addition
                    // location.reload();
                } else {
                    console.error("Error adding note:", data.error);
                }
            })
            .catch(error => {
                console.error("Error adding note:", error);
            });
    }
});

function localizeTimestamp(timestamp) {
    utcTimestamp = new Date(timestamp);
    // Separate date and time options for independent formatting
    const dateOptions = {
      month: 'long', // Full month name
      day: 'numeric', // Day of the month
      year: 'numeric', // 4 digit year
    };
    const timeOptions = {
      hour: 'numeric', // Numeric hour, automatically adjusts to AM/PM formatting
      minute: '2-digit', // Two-digit minute
      hour12: true, // Use 12-hour time
    };
    const formattedDate = new Intl.DateTimeFormat('en-US', dateOptions).format(utcTimestamp);
    const formattedTime = new Intl.DateTimeFormat('en-US', timeOptions).format(utcTimestamp);

    return `${formattedDate}, ${formattedTime}`;
}

function handleNotDeleteRequest(deleteUrl, formData) {
    return fetch(deleteUrl, {
        method: "POST",
        body: formData,
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
            return true;
        } else {
            console.error("Error deleting note:", data.error);
            return false;
        }
    })
    .catch(error => {
        console.error("Error deleting note:", error);
        return false;
    });
}

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

document.addEventListener('DOMContentLoaded', function () {
    // Assuming '.order-note-list' is the parent container of your note items
    const noteList = document.querySelector('.order-note-list');

    if (noteList) {
        // Convert the timezones of the timestampts
        timestampDivs = document.querySelectorAll('.note-timestamp');
        timestampDivs.forEach((timestampDiv) => {
            let normalizedTimestampString = timestampDiv.innerText
                .replace('a.m.', 'AM')
                .replace('p.m','PM')
                .concat(', UTC');

            timestampDiv.innerText = localizeTimestamp(normalizedTimestampString);
        })


        // Event delegation for handling note deletion
        noteList.addEventListener('click', function (event) {
            // Check if the clicked element is a delete button
            if (event.target.classList.contains('note-delete')) {
                event.preventDefault(); // Prevent the default form submission if it's a form button

                const button = event.target; // The clicked button
                const noteId = button.getAttribute('data-note-id');
                const deleteUrl = button.getAttribute('data-delete-url');

                // Create a new FormData object
                const formData = new FormData();
                formData.append('note_id', noteId); // Append the note_id to the form data

                // Send an AJAX request to delete the note with the note_id
                handleNotDeleteRequest(deleteUrl, formData)
                    .then(success => {
                        if (success) {
                            const noteElement = button.closest('li');
                            noteElement.remove(); // Remove the note element from the DOM
                        }
                    });
            }
        });
    }


});

