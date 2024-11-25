from flask import render_template, session
from ORM.views.profile import Profile
from managements.notif import get_numbers_of_notifs


def go_search():
    filtered_profiles = False
    all_profiles = Profile._all()

    # filtrer ceux que j'ai block et qui m'ont block

    if all_profiles:
        filtered_profiles = []
        for profile in all_profiles:
            user_id = session['user_id']
            if profile.id != user_id:
                image_data = Profile.get_profile_image(profile.id)
                filtered_profiles.append({
                    'id': profile.id,
                    'username': profile.username,
                    'profile_image': image_data
                })
                
    nb_notifs = get_numbers_of_notifs()
    return render_template('search.html', filtered_profiles=filtered_profiles, user_id=user_id,
                           nb_notifs=nb_notifs)