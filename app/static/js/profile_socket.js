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

function add_notif(data) {
     fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {

                const notifHtml = `
                    <div class="ms-3 mb-4 border-0 border-bottom col-10 justify-content-between d-flex align-items-center">
                        <button id="delete-notif" class="btn btn-outline-primary col-2 col-md-2" type="button">
                            <i class="bi bi-x-lg"></i>
                        </button>
                        <div class="ms-5 col-10 col-md-6">
                            <p class="mb-1"><a href="/profile/${data.sender_id}">${data.sender_username}</a> sent you a ${data.state}</p>
                            <p class="m-0 text-muted">${data.date}</p>
                        </div>
                    </div>
                `;

                document.getElementById('notifs-container').insertAdjacentHTML('afterbegin', notifHtml);
            } else {
                incrementBadgeNotif();
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

}

socket.on('receive_invitation', function(data) {
    add_notif(data)

    // Si la page actuelle est 'profile' et que profile_id correspond à data.sender_id
    // Ajouter 'Invitation reçue' à cet endroit
    // (Ajoute la logique conditionnelle ici selon le cas)
    console.log('Invitation reçue:', data.message);
});

socket.on('receive_connection', function (data) {
    add_notif(data)

    // change 'Invitation envoyée' by You are connected and can now chat
    console.log('Connection reçue:', data.message);
});

socket.on('receive_uninvitation', function (data) {
    add_notif(data)

    //  remove 'You are connected and can now chat'
    console.log('Uninvitation reçue:', data.message);
});