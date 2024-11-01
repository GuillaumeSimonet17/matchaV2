import {socket, currentUserId} from './socket_management.js';

// ----------------------------------- EMIT -----------------------------------

document.getElementById('btn-send-invit').onclick = function() {

    const receiver_id = this.getAttribute('data-profile-id');

    console.log('sender_id => ', currentUserId);
    console.log('receiver_id => ', receiver_id);

    socket.emit('send_invitation', {
        sender_id: currentUserId,
        receiver_id: receiver_id
    });
    this.remove();
    document.getElementById('alert-invitation-sent').classList.remove('d-none');

};


// ----------------------------------- ON -----------------------------------

socket.on('receive_invitation', function(data) {
    console.log('Invitation reçue:', data.message);
});
