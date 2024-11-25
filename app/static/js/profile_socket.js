import { incrementBadgeNotif } from './notif.js';

const currentUserIdElement = document.getElementById('current-user');
const currentUserId = currentUserIdElement ? currentUserIdElement.getAttribute('data-current-user-id') : null;

// ----------------------------------- EMIT -----------------------------------

const btnSendInvit = document.getElementById('btn-send-invit')
if (btnSendInvit) {
    btnSendInvit.onclick = function() {

        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_invitation', {
            sender_id: currentUserId,
            receiver_id: receiver_id
        });

        this.remove();
        document.getElementById('alert-invitation-sent').classList.remove('d-none');

    };
}

const btnSendConnect = document.getElementById('btn-send-connect')
if (btnSendConnect) {
    btnSendConnect.onclick = function() {

        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_connection', {
            sender_id: currentUserId,
            receiver_id: receiver_id
        });

        this.remove();
        document.getElementById('alert-connection-sent').classList.remove('d-none');

    };
}

const btnSendUninvit = document.getElementById('btn-send-uninvit')
if (btnSendUninvit) {
    btnSendUninvit.onclick = function() {

        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_uninvitation', {
            sender_id: currentUserId,
            receiver_id: receiver_id
        });

        this.remove();

    };
}

// ----------------------------------- ON -----------------------------------

socket.on('receive_invitation', function(data) {
    // add notif
    incrementBadgeNotif()

    // add 'Invitation reçue'
    console.log('Invitation reçue:', data.message);
});

socket.on('receive_connection', function(data) {
    // add notif
    incrementBadgeNotif()

    // change 'Invitation envoyée' by You are connected and can now chat
    console.log('Connection reçue:', data.message);
});

socket.on('receive_uninvitation', function(data) {
    // add notif
    incrementBadgeNotif()

    //  remove 'You are connected and can now chat'
    console.log('Uninvitation reçue:', data.message);
});