from flask import render_template, session
from ORM.views.profile import Profile
from ORM.tables.visit import Visit
from managements.notif import get_numbers_of_notifs, get_numbers_of_notifs_msg


def go_historic():
    user_id = session['user_id']
    visits = Visit.find_visits_by_user(user_id)
    visits_list = []
    if visits:
        for visit in visits:
            receiver = Profile._find_by_id(visit.receiver_id)
            visits_list.append({
                'receiver': receiver,
                'date': visit.created_at.strftime('%Y-%m-%d %H:%M'),
            })

    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    return render_template('historic.html', user_id=user_id, visits_list=visits_list,
                        nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg)