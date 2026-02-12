    // static/js/login.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            // Client-side validation for demonstration
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {
                alert('Please fill in all fields.');
                event.preventDefault(); // Stop form submission
                return;
            }

            // You can add AJAX submission here if needed, 
            // but for now, we rely on Flask's POST handling.
            
            console.log('Login form submitted successfully (client-side check passed).');
        });
    }
});