import {incrementBadgeNotif, add_notif} from './notif.js';

const currentUserIdElement = document.getElementById('current-user');
const currentUserId = currentUserIdElement ? currentUserIdElement.getAttribute('data-current-user-id') : null;

// ----------------------------------- EMIT -----------------------------------

const btnSendInvit = document.getElementById('btn-send-invit')
if (btnSendInvit) {
    btnSendInvit.onclick = function () {
        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_invitation', {
            receiver_id: receiver_id
        });

        this.remove();
        document.getElementById('alert-invitation-sent').classList.remove('d-none');

    };
}

const btnSendBlock = document.getElementById('btn-send-block')
if (btnSendBlock) {
    btnSendBlock.onclick = function () {

        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_block', {
            receiver_id: receiver_id
        });

        this.remove();
        const p_balise_block = `
            <p id="alert-block-sent" class="row alert alert-success">Vous venez de bloquer ce bateau</p>
            `
        document.getElementById('friendship-btn-container').insertAdjacentHTML('afterbegin', p_balise_block);

        const btnInvit = document.getElementById('btn-send-invit')
        if (btnInvit) {
            btnInvit.remove()
        }
    };
}

const btnSendConnect = document.getElementById('btn-send-connect')
if (btnSendConnect) {
    btnSendConnect.onclick = function () {

        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_connection', {
            receiver_id: receiver_id
        });

        this.remove();
        document.getElementById('alert-connection-sent').classList.remove('d-none');

    };
}

const btnSendUninvit = document.getElementById('btn-send-uninvit')
if (btnSendUninvit) {
    btnSendUninvit.onclick = function () {

        const receiver_id = this.getAttribute('data-profile-id');

        socket.emit('send_uninvitation', {
            receiver_id: receiver_id
        });

        this.remove();

    };
}

// ----------------------------------- ON -----------------------------------

function display_friendship_changes(data) {
    if (data.state === 'invitation') {
        document.getElementById('btn-send-invit').remove();

        const p_balise = `
            <p id="alert-invitation-received" class="row alert alert-success">Invitation reçu</p>
            `
        document.getElementById('friendship-btn-container').insertAdjacentHTML('afterbegin', p_balise);
    }
    if (data.state === 'uninvitation') {
        const newAlert = `
            <p id="now-alert" class="alert alert-success">You are unliked</p>
            `
        const btn = document.getElementById('btn-send-uninvit')
        if (btn) {
            btn.remove();
        }
        document.getElementById('friendship-btn-container').insertAdjacentHTML('afterbegin', newAlert);
    }
    if (data.state === 'connected') {
        const p_balise2 = `
            <p id="alert-connection-received" class="alert alert-success">You are connected and can now chat</p>
            `
        document.getElementById('friendship-btn-container').insertAdjacentHTML('afterbegin', p_balise2);
        const btn2 = document.getElementById('alert-invitation-received')
        if (btn2) {
            btn2.remove();
        }
    }
}

socket.on('receive_invitation', function (data) {

    fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {
                add_notif(data)

                socket.emit('mark_notifs_as_read', data);

            } else {
                incrementBadgeNotif()

                if (currentPage === 'profile' && data.sender_id === res.current_profile_id) {
                    display_friendship_changes(data)
                }
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

});

socket.on('receive_connection', function (data) {
    fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {
                add_notif(data)

                socket.emit('mark_notifs_as_read', data);

            } else {
                incrementBadgeNotif();
                if (currentPage === 'profile' && data.sender_id === res.current_profile_id) {
                    display_friendship_changes(data)
                }
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

});

socket.on('receive_uninvitation', function (data) {
    fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {
                add_notif(data)

                socket.emit('mark_notifs_as_read', data);

            } else {
                incrementBadgeNotif();
                if (currentPage === 'profile' && data.sender_id === res.current_profile_id) {
                    display_friendship_changes(data)
                }
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

});

socket.on('receive_view_profile', function (data) {
    fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {
                data['state'] = 'view'
                data['date'] = 'Now'

                add_notif(data)

                socket.emit('mark_notifs_as_read', data);
            } else {
                incrementBadgeNotif();
            }
        })
        .catch(error => console.error('Error fetching session data:', error));
})
