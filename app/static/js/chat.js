import {incrementBadgeMsg} from './notif.js';

const currentUserIdElement = document.getElementById('current-user');
const currentUserId = currentUserIdElement ? currentUserIdElement.getAttribute('data-current-user-id') : null;

const currentProfileIdElement = document.getElementById('current-profile');
let currentProfileId = currentProfileIdElement ? currentProfileIdElement.getAttribute('data-profile-id') : null;

document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.getElementById("chat-container");
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

const profiles = document.querySelectorAll('.user-profile')
if (profiles) {
    profiles.forEach(profile => {
        profile.addEventListener('click', function (event) {
            event.preventDefault();

            const username = this.getAttribute('data-username');
            currentProfileId = this.getAttribute('data-profile-id');

            let old_select = document.querySelector('.bg-secondary')
            if (old_select) {
                old_select.classList.remove('bg-secondary');
                old_select.querySelector('p').classList.remove('text-light');
                old_select.querySelector('p').classList.add('text-secondary');
            }
            this.classList.add('bg-secondary');
            this.querySelector('p').classList.remove('text-secondary');
            this.querySelector('p').classList.add('text-light');
            socket.emit('get_messages', {profile_id: currentProfileId});

        });
    });
}

const btnSend = document.querySelector('#btn-send')
if (btnSend) {

    btnSend.addEventListener('click', function (event) {

        let message = document.querySelector('#input-msg')
        if (message.value !== '') {
            socket.emit('send_message', {
                content: message.value,
                sender_id: currentUserId,
                receiver_id: currentProfileId
            });

            const chatContainer = document.querySelector('#chat-container');

            const msgElement = document.createElement('div');
            msgElement.classList.add('d-flex', 'flex-column', 'align-items-center', 'mt-2', 'px-3', 'w-100');
            msgElement.innerHTML = `
                    <p class="text-dark p-2 px-3 m-0 text-start text-break rounded me-auto my-msg">${message.value}</p>
                    <small class="text-muted text-start text-break me-auto">Now</small>
                `;
            chatContainer.appendChild(msgElement);

            message.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

        }
    })
}

socket.on('receive_message', function (data) {

    fetch(`/get_current_page`, {method: 'GET'})
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'chat' && data['sender_id'] === res.current_channel) {

                socket.emit('received_message', data);

            } else {
                incrementBadgeMsg();
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

})

socket.on('display_messages', function (data) {
    const chatContainer = document.querySelector('#chat-container');
    if (chatContainer) {
        chatContainer.innerHTML = '';
    }

    if (data.messages.length === 0) {
        const msgElement = document.createElement('div');
        msgElement.innerHTML = `<p>No messages</p>`;
        chatContainer.appendChild(msgElement);
    }

    data.messages.forEach(msg => {
        const msgElement = document.createElement('div');

        msgElement.classList.add('d-flex', 'flex-column', 'align-items-center', 'rounded', 'mt-2', 'px-3', 'w-100');
        if (msg.sender_id == currentUserId)
            msgElement.innerHTML = `
                <p class="text-dark p-2 px-3 m-0 text-start text-break rounded me-auto my-msg">${msg.content}</p>
                <small class="text-muted text-start text-break me-auto">${msg.created_at}</small>
            `;
        else
            msgElement.innerHTML = `
                <p class="text-dark p-2 px-3 m-0 text-start text-break rounded ms-auto border">${msg.content}</p>
                <small class="text-muted text-start text-break ms-auto">${msg.created_at}</small>
            `;

        chatContainer.appendChild(msgElement);

    });
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

});
