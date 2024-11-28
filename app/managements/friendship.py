from flask_socketio import emit

from ORM.tables.friendship import Friendship
from ORM.views.profile import Profile
from ORM.tables.notif import Notif
from ORM.tables.block import Block
from ORM.tables.channel import Channel

from managements.profile import is_blocked, fame_rate_calcul


def handle_invitation(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    
    if (is_blocked(sender_id, receiver_id)):
        return
    
    # check if friendship exist
    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])
    if friendship:
        if friendship.state == 'invitation':
            handle_connection(data)
        return
    friendship = Friendship(None, 'invitation', sender_id, receiver_id)
    friendship.create()

    notif = Notif(None, 'invitation', sender_id, receiver_id, False)
    notif.create()
    
    sender = Profile._find_by_id(sender_id)
    
    fame_rate_calcul(receiver_id)
    
    emit('receive_invitation',
         {'sender_username': sender.username, 'sender_id': sender.id, 'date': 'Now', 'state': 'invitation'},
         room=f'user_{receiver_id}')

def handle_block(data):
    if (is_blocked(data['sender_id'], data['receiver_id'])):
        return
 
    block = Block(None, data['sender_id'], data['receiver_id'])
    block.create()
 
    friendship = Friendship.get_friendship_by_user_ids([data['sender_id'], data['receiver_id']])
    if friendship:
        friendship.delete()

    channel = Channel.find_channel_by_user_ids(data['sender_id'], data['receiver_id'])
    if channel:
        channel.delete()
        
    fame_rate_calcul(data['receiver_id'])
        
def handle_connection(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    
    if (is_blocked(sender_id, receiver_id)):
        return
    
    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])
    
    # get friendship and check if state is invitation and receiver_id = sender_id
    if friendship.state != 'invitation' and friendship.sender_id != int(receiver_id):
        return
    
    # update state
    friendship.update({'state': 'connected'})
    
    # create channel between users
    channel = Channel(None, sender_id, receiver_id)
    channel.create()
    
    notif = Notif(None, 'connection', sender_id, receiver_id, False)
    notif.create()
    
    sender = Profile._find_by_id(sender_id)
    
    fame_rate_calcul(receiver_id)
    fame_rate_calcul(sender_id)

    emit('receive_connection',
         {'sender_username': sender.username, 'sender_id': sender.id, 'date': 'Now', 'state': 'connected'},
         room=f'user_{receiver_id}')

def handle_uninvitation(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    
    if (is_blocked(sender_id, receiver_id)):
        return
    
    channel = Channel.find_channel_by_user_ids(data['sender_id'], data['receiver_id'])
    if channel:
        channel.delete()
    
    # get friendship and check if state is connected
    friendship = Friendship.get_friendship_by_user_ids([sender_id, receiver_id])
    
    if friendship.state != 'connected':
        return
    
    # update state
    friendship.update({'state': 'uninvitation', 'sender_id': sender_id, 'receiver_id': receiver_id})
    
    notif = Notif(None, 'uninvitation', sender_id, receiver_id, False)
    notif.create()
    
    sender = Profile._find_by_id(sender_id)
    
    fame_rate_calcul(receiver_id)
    
    emit('receive_uninvitation',
         {'sender_username': sender.username, 'sender_id': sender.id, 'date': 'Now', 'state': 'uninvitation'},
         room=f'user_{receiver_id}')
