from flask import render_template, session, request
from flask_socketio import emit

from ORM.tables.friendship import Friendship
from ORM.views.profile import Profile
from ORM.tables.channel import Channel
from ORM.tables.message import Message
from ORM.tables.notif import Notif

from managements.profile import is_blocked
from managements.notif import get_numbers_of_notifs, get_numbers_of_notifs_msg


def go_chat():
    user_id = session['user_id']
    profiles = []
    profile_id = None
    profile_selected = None
    messages_data = []
    
    connections = Friendship.get_friendship_connections(user_id)
    
    if connections:
        other_user_ids = [
            conn.sender_id if conn.receiver_id == user_id else conn.receiver_id
            for conn in connections
        ]
        
        profiles = []
        for id in other_user_ids:
            profile = Profile._find_by_id(id)
            if (is_blocked(user_id, id)):
                continue
            if profile:
                image_data = Profile.get_profile_image(profile.id)
                profiles.append({'id': profile.id, 'username': profile.username, 'image_data': image_data})
        
        last_message = Message.find_last_channel_id(user_id)

        if last_message:
            channel_id = last_message['channel_id']
            profile_id = last_message['profile_id']
            
            profile_selected = Profile._find_by_id(profile_id)

            # Récupérer les messages entre user_id et profile_id
            messages = Message.find_messages_by_channel_id(channel_id)
            if messages:
                messages_data = [{"receiver_id": msg.receiver_id, "sender_id": msg.sender_id, "content": msg.content,
                                  "created_at": msg.created_at.strftime('%Y-%m-%d %H:%M')} for msg in messages]
        else:
            channel = Channel.find_last_channel_by_user_id(user_id)
            if channel.user_a == user_id:
                profile_id = channel.user_b
            else:
                profile_id = channel.user_a
            profile_selected = Profile._find_by_id(profile_id)
        
        session['current_channel'] = profile_selected.id
    
    session['current_page'] = 'chat'

    Notif.delete_notifs_msg_by_user_id(user_id)
    
    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    return render_template('chat.html', profiles=profiles, user_id=user_id, profile_selected=profile_selected,
                           profile_id=profile_id, messages_data=messages_data, nb_notifs=nb_notifs,
                           nb_notifs_msg=nb_notifs_msg)

def handle_get_messages(data):
    user_id = session.get('user_id')
    profile_id = data.get('profile_id')
    
    profile_selected = Profile._find_by_id(int(profile_id))
    
    channel = Channel.find_channel_by_user_ids(int(user_id), int(profile_id))
    
    messages_data = []
    messages = Message.find_messages_by_channel_id(channel.id)
    
    if messages:
        messages_data = [{"receiver_id": msg.receiver_id, "sender_id": msg.sender_id, "content": msg.content,
                          "created_at": msg.created_at.strftime('%Y-%m-%d %H:%M')} for msg in messages]
    
    session['current_channel'] = profile_selected.id
    emit('display_messages', {'messages': messages_data, 'profile_username': profile_selected.username},
         room=request.sid)

def handle_send_message(data):
    print( data.get('receiver_id'))

    if data.get('receiver_id') is None or data.get('sender_id') is None:
        print('\nc coment\n')
        return
    
    sender_id = int(data['sender_id'])
    receiver_id = int(data['receiver_id'])
    content = data['content']
    
    if is_blocked(sender_id, receiver_id):
        return
    print('rece === ', receiver_id)
    if receiver_id != 0:
        channel = Channel.find_channel_by_user_ids(sender_id, receiver_id)
        msg = Message(None, channel.id, sender_id, receiver_id, content, False)
        msg.create()
    
    have_to_notif = False
    notifs_exist = Notif.find_notif('message', sender_id, receiver_id)
    if not notifs_exist:
        have_to_notif = True
    else:
        for notif_exist in notifs_exist:
            if notif_exist.read:
                have_to_notif = True
    
    if have_to_notif:
        notif = Notif(None, 'message', sender_id, receiver_id, False)
        notif.create()
    
    print('ici ', f'user_{receiver_id}')
    emit('receive_message', {'sender_id': sender_id}, room=f'user_{receiver_id}')
