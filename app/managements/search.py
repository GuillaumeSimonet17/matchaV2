from flask import render_template, session, jsonify
from ORM.views.profile import Profile
from ORM.tables.block import Block
from managements.notif import get_numbers_of_notifs, get_numbers_of_notifs_msg


def go_search():
    filtered_profiles = False
    all_profiles = Profile._all()

    user_id = session['user_id']

    # filtrer ceux que j'ai block et qui m'ont block
    blocked_ids = []

    blocked = Block.find_blocks_by_user_id(user_id)
    if blocked:
        for block in blocked:
            if block.receiver_id == user_id:
                blocked_ids.append(block.sender_id)
            else:
                blocked_ids.append(block.receiver_id)
            

    if all_profiles:
        filtered_profiles = []
        for profile in all_profiles:
            if blocked:
                if profile.id in blocked_ids:
                    continue

            if profile.id != user_id:
                image_data = Profile.get_profile_image(profile.id)
                filtered_profiles.append({
                    'id': profile.id,
                    'username': profile.username,
                    'profile_image': image_data
                })

    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    return render_template('search.html', filtered_profiles=filtered_profiles, user_id=user_id,
                           nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg)
