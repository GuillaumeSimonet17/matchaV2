from flask import render_template, session, redirect, url_for

from ORM.tables.user import User
from ORM.views.profile import Profile
from ORM.tables.friendship import Friendship
from ORM.tables.tag import UserTag, Tag
from ORM.tables.visit import Visit
from ORM.tables.block import Block
from ORM.tables.notif import Notif

from managements.notif import get_numbers_of_notifs, get_numbers_of_notifs_msg

def go_profile(profile_id: int):
    user_id = session['user_id']
    session['profile_id'] = profile_id

    profile = Profile._find_by_id(profile_id)
    if not profile:
        return render_template('404.html'), 404

    if is_blocked(user_id, profile_id):
        return redirect(url_for('main.home'))

    online = profile.connected
    profile_image_data = Profile.get_profile_image(profile.id)
    user_tag_ids = UserTag.find_tags_by_user_id(profile.id)

    user_tags = []
    if user_tag_ids:
        for tag_id in user_tag_ids:
            tag = Tag._find_by_id(tag_id.tag_id)
            if tag:
                user_tags.append(tag)

    friendship = Friendship.get_friendship_by_user_ids([user_id, profile_id])
    state, connected, received_invitation, sent_invitation = False, False, False, False
    if friendship:
        state = friendship.state

        if state != 'connected':
            received_invitation = friendship.receiver_id == session['user_id']
            sent_invitation = friendship.sender_id == session['user_id']
        else:
            connected = True

    if not (Visit.find_visit(user_id, profile_id)):
        visit = Visit(None, user_id, profile_id)
        visit.create()

    notif = Notif(None, 'view', user_id, profile_id, False)
    notif.create()

    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    
    

    return render_template('profile.html', profile=profile, state=state, connected=connected,
                           profile_image_data=profile_image_data, received_invitation=received_invitation,
                           sent_invitation=sent_invitation, user_tags=user_tags, user_id=user_id,
                           nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg, online=online)

def is_blocked(user_id, profile_id):
    block = False

    are_blocked = Block.find_block(user_id, profile_id)
    if are_blocked:
        block = True
    else:
        are_blocked = Block.find_block(profile_id, user_id)
        if are_blocked:
            block = True
    return block

def fame_rate_calcul(user_id):
    
    nb_connections = 0
    connections = Friendship.get_friendship_connections(user_id)
    if connections:
        nb_connections = len(connections)
        
    nb_invitations = 0
    invitations = Friendship.get_invitations_received(user_id)
    if invitations:
        nb_invitations = len(invitations)
    
    nb_uninvitations = 0
    uninvitations = Friendship.get_uninvitations_received(user_id)
    if uninvitations:
        nb_uninvitations = len(uninvitations)
    
    nb_blocks = 0
    blocks = Block.find_blocks_by_receiver_id(user_id)
    if blocks:
        nb_blocks = len(blocks)

    coef_connections = 2
    coef_invitations = 1.5
    coef_uninvitations = -1
    coef_block = -1

    fame_rate = (
        (nb_connections * coef_connections) +
        (nb_invitations * coef_invitations) +
        (nb_blocks * coef_block) +
        (nb_uninvitations * coef_uninvitations)
    )
    print('fame_rate = ', fame_rate)
    user = User._find_by_id(user_id)
    user.update({'fame_rate': fame_rate})
