export function add_notif(data) {
    const notifHtml = `
        <div class="ms-3 mb-4 border-0 border-bottom col-10 justify-content-between d-flex align-items-center">
            <div class="ms-5 col-10 col-md-6">
                <p class="mb-1"><a href="/profile/${data.sender_id}">${data.sender_username}</a> sent you a ${data.state}</p>
                <p class="m-0 text-muted">${data.date}</p>
            </div>
        </div>
    `;

    document.getElementById('notifs-container').insertAdjacentHTML('afterbegin', notifHtml);
}

export function incrementBadgeNotif() {
    let badge = document.getElementById('badge-notifs');
    if (!badge) {
        badge = document.createElement('span');
        badge.id = 'badge-notifs';
        badge.classList.add('position-absolute', 'top-0', 'start-100', 'translate-middle', 'badge', 'rounded-pill', 'bg-danger');
        badge.textContent = '0';

        const iconElement = document.querySelector('#notif-icon');
        if (iconElement) {
            iconElement.parentNode.insertBefore(badge, iconElement);
        }

    }

    let currentValue = parseInt(badge.textContent, 10);
    if (isNaN(currentValue)) {
        currentValue = 0;
    }
    badge.textContent = currentValue + 1;
}

export function incrementBadgeMsg() {
    let badgemsg = document.getElementById('badge-msg-notifs');

    if (!badgemsg) {
        badgemsg = document.createElement('span');
        badgemsg.id = 'badge-msg-notifs';
        badgemsg.classList.add('position-absolute', 'top-0', 'start-100', 'translate-middle', 'badge', 'rounded-pill', 'bg-danger');

        const iconElement = document.querySelector('#chat-icon');
        if (iconElement) {
            iconElement.parentNode.insertBefore(badgemsg, iconElement);
        }
    }

    const icon_bell = document.querySelector('.bi-bell-fill');

    if (!icon_bell) {
        const bellIcon = document.createElement("i");
        bellIcon.className = "bi bi-bell-fill text-light";
        badgemsg.appendChild(bellIcon);
    }


}
