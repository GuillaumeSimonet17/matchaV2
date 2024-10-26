from flask import Blueprint, flash, request, render_template, session, redirect, url_for

from user_management.auth.login import auth_login
from user_management.auth.register import auth_register
from user_management.update_user import update_user_infos, change_password

from ORM.tables.user import User
from ORM.tables.tag import UserTag, Tag
from ORM.views.profile import Profile
from ORM.tables.friendship import Friendship
from ORM.tables.notif import Notif


main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if auth_login(request):
            return redirect(url_for('main.home'))
        flash('Ecris mieux stp', 'danger')
    
    if 'username' in session:
        return redirect(url_for('main.home'))
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return auth_register(request)
    tags = Tag._all()
    return render_template('register.html', tags=tags)


import base64

@main.route('/')
def home():
    if 'username' in session:
        filtered_profiles = False
        all_profiles = Profile._all()

        # filtrer ceux que j'ai block et qui m'ont block

        if all_profiles:
            filtered_profiles = []
            for profile in all_profiles:
                user_id = session['user_id']
                if isinstance(user_id, tuple):
                    user_id = session['user_id'][0]
                if profile.id != user_id:
                    image_data = Profile.get_profile_image(profile.id)
                    filtered_profiles.append({
                        'id': profile.id,
                        'username': profile.username,
                        'profile_image': image_data
                    })
        return render_template('search.html', filtered_profiles=filtered_profiles)
    return redirect(url_for('main.login'))

@main.route('/historic')
def historic():
    if 'username' in session:
        return render_template('historic.html')
    return redirect(url_for('main.login'))

@main.route('/notifs')
def notifs():
    if 'username' in session:
        
        user_id = session['user_id']
        if isinstance(user_id, tuple):
            user_id = session['user_id'][0]
        notifs = Notif.find_notifs_by_user(user_id)
        notifs_list = []
        if notifs:
            for notif in notifs:
                sender = Profile._find_by_id(notif.sender_id)
                notifs_list.append({
                    'sender': sender,
                    'state': notif.state,
                    'date': notif.created_at.strftime('%Y-%m-%d %H:%M'),
                })
        return render_template('notifs.html', notifs_list=notifs_list)
    return redirect(url_for('main.login'))

@main.route('/chat')
def chat():
    if 'username' in session:
        return render_template('chat.html')
    return redirect(url_for('main.login'))

@main.route('/profile/<int:profile_id>')
def profile(profile_id):
    if 'username' in session:
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

        # add historic tp user_id in db AND a notif to profile_id
        return render_template('profile.html', profile=profile, state=state, connected=connected,
                               profile_image_data=profile_image_data, recevied_invitation=recevied_invitation,
                               sent_invitation=sent_invitation, user_tags=user_tags)
    return redirect(url_for('main.login'))

@main.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    user = User._find_by_username(session['username'])
    profile_image_data = User.get_profile_image(user.id)
    user_tags = UserTag.find_tags_by_user_id(user.id)
    tags = Tag._all()
    user_tag_ids = [tag.tag_id for tag in user_tags]
    if request.method == 'POST':
        return update_user_infos(request, user=user, profile_image_data=profile_image_data, user_tag_ids=user_tag_ids, tags=tags)

    return render_template('user.html', user=user, profile_image_data=profile_image_data,
                           user_tag_ids=user_tag_ids, tags=tags)

@main.route('/change-password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    change_password(request)
    return redirect(url_for('main.user'))

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
