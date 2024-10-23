import os

from flask import Flask
from dotenv import load_dotenv

from ORM.database import init_db
from routes import main as main_routes

app = Flask(__name__)
app.secret_key = 'your_secret_key'

load_dotenv()

app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT')

init_db(app.config)

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

# notif = Notif(None, 'message', 2, 1, False)
# notf = notif.create()
# notif = Notif._find_by_id(3)
# notif.delete()
# notif_user = Notif.find_notifs_by_user(1)
# print(notif_user)
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


app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
