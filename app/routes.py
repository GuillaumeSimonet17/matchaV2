from flask import Blueprint, flash, request, render_template, session, redirect, url_for

from managements.user_management.auth.login import auth_login
from managements.user_management.auth.register import auth_register
from managements.user_management.update_user import update_user_infos, change_password
from managements.profile_management.profile_management import go_profile

from ORM.tables.user import User
from ORM.tables.tag import UserTag, Tag
from ORM.views.profile import Profile
from ORM.tables.notif import Notif
from ORM.tables.visit import Visit


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
        
        user_id = session['user_id']
        if isinstance(user_id, tuple):
            user_id = session['user_id'][0]
        visits = Visit.find_visits_by_user(user_id)
        visits_list = []
        if visits:
            for visit in visits:
                receiver = Profile._find_by_id(visit.receiver_id)
                visits_list.append({
                    'receiver': receiver,
                    'date': visit.created_at.strftime('%Y-%m-%d %H:%M'),
                })

        return render_template('historic.html', visits_list=visits_list)
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
        return go_profile(profile_id)
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
