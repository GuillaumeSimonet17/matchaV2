import os

from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv

from ORM.database import init_db
from routes import main as main_routes

app = Flask(__name__)
socketio = SocketIO(app)

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT')

init_db(app.config)

from ORM.tables.user import User

# usr1 = User(None, 'username1', 'last1', 'first1', '20', 'password1', 'email1', 'img', 'bio', 'gender', 'genderpref')
# usr2 = User(None, 'username2', 'last2', 'first2', '20', 'password2', 'email2', 'img', 'bio', 'gender', 'genderpref')
# usr3 = User(None, 'username3', 'last3', 'first3', '30', 'password3', 'email3', 'img', 'bio', 'gender', 'genderpref')
# user1 = usr1.create()
# user2 = usr2.create()
# user3 = usr3.create()
# print('usr2 = ', usr2)
# print(usr2)

# found = User.get_all_values(['id', 'username', 'age', 'gender'])
# print(found)
# found = User.get_dict_by_id(243, ['id', 'username', 'age', 'gender'])
# found = User.get_dict_by_id(143)
# found1 = User._find_by_id(user1)
# found2 = User._find_by_id(user2)
# print(found)
# print('id  === ', found.id)
# users = User.get_all_dicts( ['id', 'username', 'age', 'gender'])
# print('=======================================')
# for user in users:
#     print(user)
# allusr = User._all()

# print(allusr)
# profile1_dict = Profile.get_all_dicts(['username', 'profile_image'])
# print(profile1_dict)
# profile1 = Profile._find_by_id(143)
# print(profile1.username)
# print('=======================================')
# print(profile1_dict)
# print(profile1.username, profile1.profile_image, profile1.id, profile1.age)
# dic = {
#     'age': 1
# }
# found.update(dic)
# found = User.get_dict_by_id(143, ['age'])
# print(found.username)
# found.delete()
# print(found.username)

# print('pro = ', profile1.username)
# profile1 = Profile._find_by_id(143)
# print('pro2 = ', profile1.username)

# chan2 = Channel(None, 5, 6)
# chan = chan2.create()
# chan = Channel._find_by_id(7)
# chan.delete()
# found = Channel.find_channel_by_user_ids(5, 7)
# for channel in found:
#     print(channel.user_b) if channel.user_b != 5 else print(channel.user_a)
# print(found)

from ORM.tables.notif import Notif

# notif = Notif(None, 'message', 2, 1, False)
# notif2 = Notif(None, 'invitation', 2, 1, False)
# notif3 = Notif(None, 'message', 3, 2, False)
# notf = notif.create()
# notf2 = notif2.create()
# notf3 = notif3.create()
# notif = Notif._find_by_id(3)
# notif.delete()
# notif_user = Notif.find_notifs_by_user(1)
# print(notif_user)

# Notif.mark_notifs_by_user_id_as_read(1)

# vals = {
#     'read': True,
#     'state': 'invitation'
# }
# Notif.update_mass(vals, [7, 8])

# visit = Visit(None, 1, 2)
# visit2 = Visit(None, 1, 3)
# view = visit.create()
# view2 = visit2.create()
# all_visits = Visit.find_visits_by_user(1)
# for visit in all_visits:
#     print(visit)
# visit = Visit._find_by_id(1)
# print(visit)
# get_all_values
# val = {
#     'updated_at': datetime.now(),
# }
# visit.update(val)

# block = Block(None, 1, 2)
# blk = block.create()
# je rentre dans search, je check un par un les user avant de les afficher si je les ai bloqués, ou s'ils m'ont bloqué
# bl = Block.find_block(1, 2)
# bl2 = Block.find_block(2, 1)
from ORM.tables.tag import Tag, UserTag
from ORM.tables.channel import Channel
from ORM.tables.message import Message

# tags = Tag._all()
# print(tags)
# first_tag = Tag._find_by_id(tags[0].id)
# print(first_tag.name)

# user_tags2 = UserTag(None, 1, 5)
# usr_tag2 = user_tags2.create()
# print(usr_tag2)

# tags_of_user = UserTag.find_tags_by_user_id(1)
# print(tags_of_user)

# chan = Channel(None, 2, 3)
# channel = chan.create()
# channel = Channel.find_channel_by_user_ids(1, 2)
# print(channel.id)
# msg = Message(None, channel.id, 1, 2, 'Coucou mon khey des montagnes eneigées', False)
# msg2 = Message(None, channel.id, 1, 2, 'Comment vas tu en cette belle journée', False)
# msg3 = Message(None, channel.id, 2, 1, 'waish sava ou koua le sen', False)
#
# mess = msg.create()
# mess2 = msg2.create()
# mess2 = msg3.create()
# print(mess)
# msg_list = Message.find_messages_by_channel_id(channel.id)
# for msg in msg_list:
#     print(msg.content)
# last = Message.find_last_message_by_channel_id(channel.id)
# print(last.content)

# Message.mark_messages_as_read(channel.id, 2)


app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
