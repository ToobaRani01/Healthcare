// signup.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    
    if (!form) return;

    form.addEventListener('submit', function(event) {
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!username || !email || !password) {
            alert('Please fill in username, email, and password.');
            event.preventDefault();
            return;
        }
    });
});

