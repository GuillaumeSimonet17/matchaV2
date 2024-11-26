from flask import render_template, session
from ORM.views.profile import Profile
from ORM.tables.notif import Notif

# EMIT

def delete_notif_by_id(notif_id):
    notif = Notif._find_by_id(notif_id)
    notif.delete()
    

def get_numbers_of_notifs():
    user_id = session['user_id']
    notifs = Notif.find_notifs_by_user(user_id)
    if notifs:
        return len([notif for notif in notifs if not notif.read and notif.state != 'message'])
    return 0

def get_numbers_of_notifs_msg():
    user_id = session['user_id']
    notifs = Notif.find_notifs_by_user(user_id)
    if notifs:
        return len([notif for notif in notifs if not notif.read and notif.state == 'message'])
    return 0

def go_notif():

    user_id = session['user_id']
    notifs = Notif.find_notifs_by_user(user_id)
    
    notifs_list = []
    if notifs:

        notifs = [notif for notif in notifs if notif.state != 'message']
        notifs = sorted(notifs, key=lambda x: x.created_at, reverse=True)
        # set all notifs as read where read=False
        Notif.mark_notifs_by_user_id_as_read(user_id)

        for notif in notifs:
            sender = Profile._find_by_id(notif.sender_id)
            notifs_list.append({
                'sender': sender,
                'state': notif.state,
                'date': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            })
 
    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    return render_template('notifs.html', user_id=user_id, notifs_list=notifs_list,
                    nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg)
