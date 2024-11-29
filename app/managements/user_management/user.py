from flask import render_template, session, request
from ORM.tables.user import User
from ORM.tables.tag import UserTag, Tag
from managements.user_management.update_user import update_user_infos
from managements.notif import get_numbers_of_notifs, get_numbers_of_notifs_msg


def go_user():
    user = User._find_by_username(session['username'])
    profile_image_data = User.get_profile_image(user.id)
    user_tags = UserTag.find_tags_by_user_id(user.id)
    tags = Tag._all()
    user_tag_ids = []
    if user_tags:
        user_tag_ids = [tag.tag_id for tag in user_tags]
    if request.method == 'POST':
        return update_user_infos(request, user=user, profile_image_data=profile_image_data, user_tag_ids=user_tag_ids,
                                 tags=tags)

    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()

    return render_template('user.html', user=user, user_id=user.id, profile_image_data=profile_image_data,
                           user_tag_ids=user_tag_ids, tags=tags, nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg)
