from flask import render_template, session
from ORM.views.profile import Profile
from ORM.tables.notif import Notif

# EMIT
# delete notif by notif_id

def go_notif():
    
    # set all notifs as read where read=False : mark_notifs_by_user_id_as_read
    # reinitaliser le badge
    
    user_id = session['user_id']
    notifs = Notif.find_notifs_by_user(user_id)
    notifs_list = []
    if notifs:
        for notif in notifs:
            sender = Profile._find_by_id(notif.sender_id)
            notifs_list.append({
                'sender': sender,
                'state': notif.state,
                'date': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            })
    return render_template('notifs.html', notifs_list=notifs_list)