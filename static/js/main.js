// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    const queryInput = document.getElementById('queryInput');
    const imageUpload = document.getElementById('imageUpload');
    const filePreview = document.getElementById('filePreview');
    const imageThumbnail = document.getElementById('imageThumbnail');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const chatForm = document.getElementById('chatForm');
    const addFileBtn = document.getElementById('addFileBtn');
    const chatHistory = document.getElementById('chatHistory');
    // Using the new float button ID if it exists, otherwise use the old one.
    const newChatBtn = document.getElementById('newChatFloatBtn') || document.getElementById('newChatBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const username = document.body.getAttribute('data-username') || 'Y'; // Get username from body attribute

    // NEW MODAL ELEMENTS
    const imageModal = document.getElementById('imageModal');
    const fullImage = document.getElementById('fullImage');
    const modalClose = document.querySelector('.modal-close');

    if (typeof marked === 'undefined') {
        console.error("Marked.js library is not loaded. Markdown formatting will not work for new messages.");
    }

    // Function to scroll chat history to the bottom
    function scrollToBottom() {
        // Use a timeout to ensure all DOM manipulation is complete before scrolling
        setTimeout(() => {
            // Find the last element (which should be the anchor or the last message/indicator)
            const lastElement = chatHistory.lastElementChild;
            if (lastElement) {
                lastElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
        }, 100);
    }

    // Function to handle image enlargement
    function setupImageEnlargement(imgElement) {
        imgElement.addEventListener('click', function () {
            const fullSrc = this.getAttribute('data-full-src') || this.src;
            fullImage.src = fullSrc;
            imageModal.style.display = "flex";
        });
    }

    // Close modal event
    if (modalClose) {
        modalClose.addEventListener('click', function () {
            imageModal.style.display = "none";
            fullImage.src = ""; // Clear image source
        });
    }

    // Close modal when clicking outside the image
    if (imageModal) {
        imageModal.addEventListener('click', function (event) {
            if (event.target === imageModal) {
                imageModal.style.display = "none";
                fullImage.src = ""; // Clear image source
            }
        });
    }

    // Function to handle copying message content
    function handleCopyButtonClick(event) {
        const button = event.currentTarget;
        const content = button.getAttribute('data-raw-content');
        if (content) {
            navigator.clipboard.writeText(content).then(() => {
                const originalTitle = button.title;
                button.title = 'Copied!';
                setTimeout(() => {
                    button.title = originalTitle;
                }, 2000);
            }).catch(err => {
                console.error('Could not copy text: ', err);
            });
        }
    }

    // Event listener for image file selection
    if (imageUpload) {
        imageUpload.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                fileNameDisplay.textContent = file.name;
                filePreview.style.display = 'flex';

                // For image files, display a thumbnail
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        imageThumbnail.src = e.target.result;
                        imageThumbnail.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                } else {
                    imageThumbnail.style.display = 'none';
                }

                // Auto-resize query input since file is attached
                if (queryInput) {
                    autoResizeTextarea(queryInput);
                }
            } else {
                filePreview.style.display = 'none';
                imageThumbnail.src = '';
                fileNameDisplay.textContent = '';
            }
        });
    }

    // Event listener to trigger file input click
    if (addFileBtn) {
        addFileBtn.addEventListener('click', function () {
            imageUpload.click();
        });
    }

    // Event listener to remove file
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', function () {
            imageUpload.value = null; // Clear the file input
            filePreview.style.display = 'none';
            imageThumbnail.src = '';
            fileNameDisplay.textContent = '';

            // Re-check textarea size after file removal
            if (queryInput) {
                autoResizeTextarea(queryInput);
            }
        });
    }

    // Function to automatically resize the textarea
    function autoResizeTextarea(textarea) {
        textarea.style.height = 'auto'; // Reset height
        let newHeight = textarea.scrollHeight;

        // Check if there is a file attached. If yes, the max height is shorter.
        const isFileAttached = imageUpload && imageUpload.files.length > 0;
        const maxHeight = isFileAttached ? 100 : 200; // Example max heights

        if (newHeight > maxHeight) {
            textarea.style.height = maxHeight + 'px';
            textarea.style.overflowY = 'scroll';
        } else {
            textarea.style.height = newHeight + 'px';
            textarea.style.overflowY = 'hidden';
        }
    }

    /**
             * Applies specialized medical formatting to diagnostic labels in the AI response.
             * Works on already-rendered HTML to support persistence across refreshes.
             */
    function applyMedicalFormatting(container) {
        let html = container.innerHTML;

        // 1. Primary Diagnosis with Confidence
        // Require it to look like a header (bold or at start of tag content)
        html = html.replace(/(?:\*\*|<strong>)?Primary Diagnosis:?(?:\*\*|<\/strong>)?\s*([^<(\n]+)(?:\s*\((\d+%)\))?/gi, (match, name, prob) => {
            const probText = prob ? ` <span class="diagnosis-probability">${prob} Confidence</span>` : "";
            return `<span class="diagnosis-section-title">Primary Diagnosis:</span> <span class="diagnosis-name">${name.trim()}</span>${probText}`;
        });

        // 2. Severity Level with Badge
        // Consumes the standard "severe condition" warning sentence if it follows, to prevent duplication
        // Also strips leading color words like "Green ", "Yellow ", "Red " etc.
        html = html.replace(/(?:\*\*|<strong>)?Severity Level:?(?:\*\*|<\/strong>)?\s*(?:Green\s+|Yellow\s+|Red\s+)?(Mild|Moderate|Severe|Risk)(?:\.?\s*This is a severe condition and should be treated\/referred rather than managed at home\.?)?/gi, (match, level) => {
            let lcLevel = level.toLowerCase();
            if (lcLevel === 'severe') lcLevel = 'risk'; // Map severe to risk class
            let advice = "";
            if (lcLevel === 'risk') advice = '<div class="severe-warning">⚠️ This is a severe condition and should be treated/referred rather than managed at home.</div>';
            return `<span class="diagnosis-section-title">Severity Level:</span> <span class="severity-badge severity-${lcLevel}">${level}</span>${advice}`;
        });

        // 3. Other Generic Labels - Use word boundaries and require a colon to signify it's a header
        const labels = [
            { pattern: /\bMedication:/i, replacement: "Recommended Medication:" },
            { pattern: /\bOther Probable Diagnoses:/i, replacement: "Other Probable Diagnoses:" },
            { pattern: /\bTreatment:/i, replacement: "General Treatment:" },
            { pattern: /\bCase Description:/i, replacement: "Case Description:" },
            { pattern: /\bDisclaimer:/i, replacement: "Medical Disclaimer:" }
        ];

        labels.forEach(label => {
            // Match the label when it's bolded or just followed by a colon at a word boundary
            const regex = new RegExp(`(?:\\*\\*|<strong>)?${label.pattern.source}(?:\\*\\*|<\\/strong>)?`, 'gi');
            html = html.replace(regex, `<span class="diagnosis-section-title">${label.replacement}</span>`);
        });

        container.innerHTML = html;
    }

    // Function to dynamically append a new message to the chat history
    function appendMessage(role, content, imageUrl) {
        // --- START: Avatar and Message Structure Setup ---
        const roleClass = role === 'user' ? 'user' : 'ai';
        // AI Avatar set to the robot emoji 🤖
        const avatarChar = role === 'user' ? (username ? username[0].toUpperCase() : 'Y') : '🤖';
        const messageElement = document.createElement('div');
        messageElement.className = `message ${roleClass}-message`;

        let messageContentHTML = '';

        if (role === 'user') {
            // User message *with* the message-bubble
            messageContentHTML = `
                <div class="message-content-wrapper">
                    <div class="message-bubble">
                        ${imageUrl ? `
                            <div class="image-bubble-wrapper">
                                <img src="${imageUrl}" class="uploaded-img-preview-bubble" alt="User uploaded image" data-full-src="${imageUrl}">
                            </div>` : ''}
                        <div class="text-content">
                            ${content ? marked.parse(content) : ''}
                        </div>
                    </div>
                </div>`;

            messageElement.innerHTML = `
                <div class="avatar ${roleClass}-avatar">${avatarChar}</div>
                ${messageContentHTML}`;
        }

        if (role === 'ai') {
            // Processing logic extracted to applyMedicalFormatting
            messageContentHTML = `
                <div class="message-content-wrapper">
                    ${imageUrl ? `
                        <div class="image-bubble-wrapper">
                            <img src="${imageUrl}" class="uploaded-img-preview-bubble" alt="User uploaded image" data-full-src="${imageUrl}">
                        </div>` : ''}
                    <div class="diagnosis-card">
                        <div class="text-content">
                            ${marked.parse(content)}
                        </div>
                    </div>
                    <button class="icon-btn copy-message-btn" title="Copy Message" data-raw-content="${content}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    </button>
                </div>`;

            messageElement.innerHTML = `
                <div class="avatar ${roleClass}-avatar">${avatarChar}</div>
                ${messageContentHTML}`;

            // Apply visual formatting to labels
            const textContent = messageElement.querySelector('.text-content');
            if (textContent) applyMedicalFormatting(textContent);
        }

        // --- END: Avatar and Message Structure Setup ---

        // 🚨 CRITICAL FIX: Insert message *before* the typing indicator
        // If the typing indicator is visible, insert the new message before it.
        if (typingIndicator && typingIndicator.style.display !== 'none') {
            chatHistory.insertBefore(messageElement, typingIndicator);
            // If this is an AI message, hide the indicator immediately after insertion
            if (role === 'ai') {
                typingIndicator.style.display = 'none';
            }
        } else {
            // Otherwise, append the message to the end of the history
            chatHistory.appendChild(messageElement);
        }

        // Apply listeners to the newly added elements
        if (role === 'ai') {
            const copyButton = messageElement.querySelector('.copy-message-btn');
            if (copyButton) {
                copyButton.addEventListener('click', handleCopyButtonClick);
            }
        }

        const imageElement = messageElement.querySelector('.uploaded-img-preview-bubble');
        if (imageElement) {
            setupImageEnlargement(imageElement);
        }

        scrollToBottom();
    }

    // Add the appendMessage to global scope for use in the fetch block
    window.appendMessage = appendMessage;


    // --- Chat Form Submission Logic ---
    if (chatForm) {
        chatForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const query = queryInput.value.trim();
            const file = imageUpload.files[0];
            const hasFile = !!file;

            if (!query && !hasFile) {
                alert('Please enter a query or upload an image.');
                return;
            }

            // 1. SHOW USER MESSAGE
            const userMessageContent = query || (file ? `*Uploaded image: ${file.name}*` : '');
            // Create a temporary URL for the local image preview
            const tempImageUrl = hasFile ? URL.createObjectURL(file) : null;

            // Insert the user message (it will be inserted right before the indicator if visible)
            appendMessage('user', userMessageContent, tempImageUrl);

            // 2. SHOW TYPING INDICATOR (Move to end if it's not already the last element)
            if (typingIndicator) {
                typingIndicator.style.display = 'flex';
                // CRITICAL: Ensure indicator is moved to the very bottom, after the user message
                chatHistory.appendChild(typingIndicator);
            }
            scrollToBottom();

            // 3. PREPARE & SEND REQUEST
            const formData = new FormData(this);
            // formData already contains 'query' and 'image' from the form fields

            // Clear input fields immediately after sending
            queryInput.value = '';
            imageUpload.value = null;
            if (filePreview) filePreview.style.display = 'none';
            if (imageThumbnail) imageThumbnail.src = '';
            if (fileNameDisplay) fileNameDisplay.textContent = '';
            autoResizeTextarea(queryInput);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    body: formData // Sends the form data including file
                });

                // HIDE TYPING INDICATOR BEFORE PROCESSING RESPONSE (If not handled by appendMessage)
                if (typingIndicator) {
                    typingIndicator.style.display = 'none';
                }

                if (response.ok) {
                    const data = await response.json();

                    if (data.role === 'error' || data.role === 'error_internal') {
                        // For API/Internal errors, display a more prominent error message
                        appendMessage('ai', `**AI Response Error:**\n\n${data.content}`, null);
                    } else if (data.content) {
                        // Success case
                        appendMessage('ai', data.content, null);
                    } else {
                        // Empty response case
                        appendMessage('ai', "I received an empty response. Please try again.", null);
                    }

                } else {
                    // HTTP error (e.g., 404, 500)
                    let errorMessage = `Server responded with status ${response.status} (${response.statusText}).`;

                    try {
                        const errorData = await response.json();
                        errorMessage += `\nDetails: \`${errorData.content || errorData.message || 'No further details available.'}\``;
                    } catch (e) {
                        // Could not parse JSON error response
                        errorMessage += '\nCould not parse server error details.';
                    }

                    appendMessage('ai', `**Request Failed:**\n\n${errorMessage}`, null);
                }
            } catch (error) {
                // HIDE TYPING INDICATOR AFTER NETWORK CATCH
                if (typingIndicator) {
                    typingIndicator.style.display = 'none';
                }

                // CRITICAL FIX: Network or client-side connection error
                console.error('Fetch error:', error);
                appendMessage('ai', `**Network Error:** Could not connect to the server. Please check your network connection or server status.`, null);
            }

            scrollToBottom();
            queryInput.focus();
        });
    }

    // --- New Chat Button Logic ---
    if (newChatBtn) {
        newChatBtn.addEventListener('click', async function () {
            if (!confirm('Start a new chat? This will clear the current conversation and create a new thread.')) {
                return;
            }

            try {
                const response = await fetch('/new_chat', {
                    method: 'POST'
                });

                if (response.ok) {
                    // Force a full reload to fetch new thread history
                    window.location.href = '/main_activity';
                } else {
                    const errorData = await response.json();
                    alert(`Failed to start new chat: ${errorData.message}`);
                }
            } catch (error) {
                console.error('New chat error:', error);
                alert('A server error occurred while trying to start a new chat.');
            }
        });
    }

    // --- Thread Delete Buttons ---
    document.querySelectorAll('.thread-delete-btn').forEach(btn => {
        btn.addEventListener('click', async (event) => {
            event.preventDefault();
            event.stopPropagation();
            const threadId = btn.getAttribute('data-thread-id');
            if (!threadId) return;
            if (!confirm('Delete this thread and all its messages?')) {
                return;
            }
            try {
                const response = await fetch(`/threads/${threadId}/delete`, { method: 'POST' });
                const data = await response.json();
                if (response.ok) {
                    const nextId = data.next_thread_id;
                    if (nextId) {
                        window.location.href = `/main_activity?thread_id=${nextId}`;
                    } else {
                        window.location.href = '/main_activity';
                    }
                } else {
                    alert(data.message || 'Failed to delete thread.');
                }
            } catch (err) {
                console.error('Delete thread error:', err);
                alert('Server error deleting thread.');
            }
        });
    });

    // Event listener for textarea resizing
    if (queryInput) {
        queryInput.addEventListener('input', () => autoResizeTextarea(queryInput));

        // Handle Enter key to send message
        queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // --- Initial Setup ---

    // Apply copy button listener to existing AI messages (for pre-rendered history)
    document.querySelectorAll('.ai-message .copy-message-btn').forEach(button => {
        button.addEventListener('click', handleCopyButtonClick);
    });

    // Apply image enlargement listener to all existing image bubbles (for pre-rendered history)
    document.querySelectorAll('.uploaded-img-preview-bubble').forEach(setupImageEnlargement);

    // PERSISTENCE FIX: Apply medical formatting to all historical AI messages already in the page
    document.querySelectorAll('.ai-message .diagnosis-card .text-content').forEach(applyMedicalFormatting);

    // Initial scroll to bottom and focus
    scrollToBottom();
    if (queryInput) {
        autoResizeTextarea(queryInput); // Initial size check
        queryInput.focus();
    }
});