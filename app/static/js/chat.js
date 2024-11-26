import {incrementBadgeMsg} from './notif.js';

const currentUserIdElement = document.getElementById('current-user');
const currentUserId = currentUserIdElement ? currentUserIdElement.getAttribute('data-current-user-id') : null;

const currentProfileIdElement = document.getElementById('current-profile');
let currentProfileId = currentProfileIdElement ? currentProfileIdElement.getAttribute('data-profile-id') : null;

document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
});

const profiles = document.querySelectorAll('.user-profile')
if (profiles) {
    profiles.forEach(profile => {
        profile.addEventListener('click', function (event) {
            event.preventDefault();

            const username = this.getAttribute('data-username');
            currentProfileId = this.getAttribute('data-profile-id');

            let old_select = document.querySelector('.bg-primary')
            if (old_select) {
                old_select.classList.remove('bg-primary');
            }
            this.classList.add('bg-primary');

            socket.emit('get_messages', {profile_id: currentProfileId});

        });
    });
}

const btnSend = document.querySelector('#btn-send')
if (btnSend) {

    // const profileId = btnSend.getAttribute('data-profile-id');

    btnSend.addEventListener('click', function (event) {

        let message = document.querySelector('#input-msg')
        if (message.value !== '') {
            socket.emit('send_message', {content: message.value, sender_id: currentUserId, receiver_id: currentProfileId});

            const chatContainer = document.querySelector('#chat-container');

            const msgElement = document.createElement('div');
            msgElement.classList.add('d-flex', 'flex-column', 'align-items-center', 'rounded', 'mt-1', 'px-2', 'me-auto', 'my-msg');
            msgElement.innerHTML = `
                    <p class="text-dark p-2 px-3 m-0 text-end text-break"><strong class="text-dark">
                        You:</strong> ${message.value}</p>
                    <small class="text-dark">${new Date().toLocaleString()}</small>
                `;
            chatContainer.appendChild(msgElement);

            message.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

        }
    })
}

socket.on('receive_message', function (data) {
    incrementBadgeMsg();

    socket.emit('received_message', data);
})

socket.on('display_messages', function (data) {
    const chatContainer = document.querySelector('#chat-container');
    chatContainer.innerHTML = '';

    if (data.messages.length === 0) {
        const msgElement = document.createElement('div');
        msgElement.innerHTML = `<p>No messages</p>`;
        chatContainer.appendChild(msgElement);
    }

    data.messages.forEach(msg => {
        const msgElement = document.createElement('div');

        if (msg.sender_id == currentUserId)
            msgElement.classList.add('d-flex', 'flex-column', 'align-items-center', 'rounded', 'mt-1', 'px-2', 'me-auto', 'my-msg');
        else
            msgElement.classList.add('d-flex', 'flex-column', 'align-items-center', 'rounded', 'mt-1', 'px-2', 'ms-auto', 'border');
        msgElement.innerHTML = `
                <p class="text-dark p-2 px-3 m-0 text-end text-break"><strong class="text-dark">${msg.sender_id == currentUserId ?
                    'You' : data.profile_username}:</strong> ${msg.content}</p>
                <small class="text-dark">${msg.created_at}</small>
            `;

        chatContainer.appendChild(msgElement);

    });
    chatContainer.scrollTop = chatContainer.scrollHeight;

});
