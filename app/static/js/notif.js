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
    console.log('ah suuuuuuuuuuuuuuu', badgemsg);
    if (!badgemsg) {
        badgemsg = document.createElement('span');
        badgemsg.id = 'badge-msg-notifs';
        badgemsg.classList.add('position-absolute', 'top-0', 'start-100', 'translate-middle', 'badge', 'rounded-pill', 'bg-danger');
        badgemsg.textContent = '0';

        const iconElement = document.querySelector('#notif-icon');
        if (iconElement) {
            iconElement.parentNode.insertBefore(badgemsg, iconElement);
        }
    }

    let currentValue = parseInt(badgemsg.textContent, 10);
    if (isNaN(currentValue)) {
        currentValue = 0;
    }
    badgemsg.textContent = currentValue + 1;
    console.log('ah badgemsg.textContent', badgemsg.textContent);

}
