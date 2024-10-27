from flask import render_template, session

from ORM.views.profile import Profile
from ORM.tables.friendship import Friendship
from ORM.tables.user import User
from ORM.tables.tag import UserTag, Tag
from ORM.tables.visit import Visit

def go_profile(profile_id: int):

    # TODO : opti cette merde
    user_id = session['user_id']
    if isinstance(user_id, tuple):
        user_id = session['user_id'][0]
    
    profile = Profile._find_by_id(profile_id)
    profile_image_data = User.get_profile_image(profile.id)
    user_tag_ids = UserTag.find_tags_by_user_id(profile.id)
    
    user_tags = []
    for tag in user_tag_ids:
        user_tags.append(Tag._find_by_id(tag.id))
    
    friendship = Friendship.get_friendship_by_user_ids([user_id, profile_id])
    state, connected, recevied_invitation, sent_invitation = False, False, False, False
    if friendship:
        state = friendship.state
        if state != 'connected':
            recevied_invitation = friendship.receiver_id == session['user_id']
            sent_invitation = friendship.sender_id == session['user_id']
        else:
            connected = True
    
    if not (Visit.find_visit(user_id, profile_id)):
        visit = Visit(None, user_id, profile_id)
        visit.create()

    # send a notif to profile_id
    
    return render_template('profile.html', profile=profile, state=state, connected=connected,
                           profile_image_data=profile_image_data, recevied_invitation=recevied_invitation,
                           sent_invitation=sent_invitation, user_tags=user_tags)