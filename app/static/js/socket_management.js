const socket = io();

const currentUserIdElement = document.getElementById('current-user');
const currentUserId = currentUserIdElement ? currentUserIdElement.getAttribute('data-current-user-id') : null;  // Utiliser l'attribut 'data-id'

// Émettre un événement de jointure
if (currentUserId) {
    socket.emit('join', { user_id: currentUserId });
}

// Écouter l'événement 'current_user'
socket.on('current_user', function(data) {
    console.log('current_user => ', data);
});
// ----------------------------------- ON -------------------------------------

socket.on('current_user', function(data) {
    console.log('current_user => ', data);
});

export default socket;