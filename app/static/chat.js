function sendMessage() {
    const messageInput = document.getElementById('chat-message');
    const message = messageInput.value.trim();

    if (message) {
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: message=${encodeURIComponent(message)}
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                messageInput.value = '';
                loadMessages();
            }
        });
    }
}

function loadMessages() {
    fetch('/chat')
        .then(response => response.json())
        .then(data => {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = '';
            data.messages.forEach(msg => {
                const p = document.createElement('p');
                p.textContent = ${msg.username}: ${msg.message};
                chatBox.appendChild(p);
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        });
}

// Загрузка сообщений при открытии страницы
document.addEventListener('DOMContentLoaded', loadMessages);