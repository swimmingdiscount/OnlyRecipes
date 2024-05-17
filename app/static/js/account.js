document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('security-link').addEventListener('click', function(event) {
        event.preventDefault();
        fetch('/account/security')
            .then(response => response.text())
            .then(data => {
                document.getElementById('account-content').innerHTML = data;
                // Update active class for the sidebar
                document.querySelectorAll('.list-group-item').forEach(item => item.classList.remove('active'));
                document.getElementById('security-link').classList.add('active');
                // Re-attach the form submission handler after updating the content
                attachFormHandler();
            });
    });

    // Function to handle form submission
    function attachFormHandler() {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(form);
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                })
                .then(response => response.text())
                .then(data => {
                    document.getElementById('account-content').innerHTML = data;
                });
            });
        }
    }

    // Attach the form handler on initial load
    attachFormHandler();
});
