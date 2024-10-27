from flask import render_template, session
from ORM.views.profile import Profile
from ORM.tables.visit import Visit


def go_historic():
    user_id = session['user_id']
    if isinstance(user_id, tuple):
        user_id = session['user_id'][0]
    visits = Visit.find_visits_by_user(user_id)
    visits_list = []
    if visits:
        for visit in visits:
            receiver = Profile._find_by_id(visit.receiver_id)
            visits_list.append({
                'receiver': receiver,
                'date': visit.created_at.strftime('%Y-%m-%d %H:%M'),
            })
    
    return render_template('historic.html', visits_list=visits_list)