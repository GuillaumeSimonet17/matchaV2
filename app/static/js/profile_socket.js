import {incrementBadgeNotif} from './notif.js';

const currentUserIdElement = document.getElementById('current-user');
const currentUserId = currentUserIdElement ? currentUserIdElement.getAttribute('data-current-user-id') : null;

// ----------------------------------- EMIT -----------------------------------

const btnSendInvit = document.getElementById('btn-send-invit')
if (btnSendInvit) {
    btnSendInvit.onclick = function () {

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
    btnSendConnect.onclick = function () {

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
    btnSendUninvit.onclick = function () {

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
}

function display_friendship_changes(data) {
    console.log('data.state = ', data.state)
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
            } else {
                incrementBadgeNotif(data)

                if (currentPage === 'profile' && data.sender_id === res.current_profile_id) {
                    display_friendship_changes(data)
                }
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

    console.log('Invitation reçue:');
});

socket.on('receive_connection', function (data) {
    fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {
                add_notif(data)
            } else {
                incrementBadgeNotif();
                console.log('data.profile_id=  ', data.sender_id)
                console.log('res.current_profile_id =  ', res.current_profile_id)
                if (currentPage === 'profile' && data.sender_id === res.current_profile_id) {
                    display_friendship_changes(data)
                }
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

    console.log('Invitation reçue:');
    // change 'Invitation envoyée' by You are connected and can now chat
    console.log('Connection reçue:');
});

socket.on('receive_uninvitation', function (data) {
    fetch('/get_current_page')
        .then(response => response.json())
        .then(res => {
            const currentPage = res.current_page;

            if (currentPage === 'notifs') {
                add_notif(data)
            } else {
                incrementBadgeNotif();
                console.log('data.profile_id=  ', data.sender_id)
                console.log('res.current_profile_id  ', res.current_profile_id)
                if (currentPage === 'profile' && data.sender_id === res.current_profile_id) {
                    console.log('coucou toi')
                    display_friendship_changes(data)
                }
            }
        })
        .catch(error => console.error('Error fetching session data:', error));

    //  remove 'You are connected and can now chat'
    console.log('Uninvitation reçue:');
});