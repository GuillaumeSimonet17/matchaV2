from flask import Blueprint, flash, render_template, session, redirect, url_for, request

from ORM.tables.user import User
from ORM.views.profile import Profile
from ORM.tables.friendship import Friendship
from user_management.auth.login import auth_login
from user_management.auth.register import auth_register
from user_management.user_update_infos import update_user_infos, change_password


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
    return render_template('register.html')

@main.route('/')
def home():
    if 'username' in session:
        all_profiles = Profile._all()
        # filtrer ceux que j'ai block et qui m'ont block
        return render_template('search.html', all_profiles=all_profiles)
    return redirect(url_for('main.login'))

@main.route('/historic')
def historic():
    if 'username' in session:
        return render_template('historic.html')
    return redirect(url_for('main.login'))

@main.route('/notifs')
def notifs():
    if 'username' in session:
        return render_template('notifs.html')
    return redirect(url_for('main.login'))

@main.route('/chat')
def chat():
    if 'username' in session:
        return render_template('chat.html')
    return redirect(url_for('main.login'))

@main.route('/profile/<int:profile_id>')
def profile(profile_id):
    if 'username' in session:
        profile = Profile._find_by_id(profile_id)
        friendship = Friendship.get_friendship_by_user_ids([session['user_id'], profile_id])
        state, connected, recevied_invitation, sent_invitation = False
        if friendship:
            state = friendship.state
            if state != 'connected':
                recevied_invitation = friendship.receiver_id == session['user_id']
                sent_invitation = friendship.sender_id == session['user_id']
            else:
                connected = True
        return render_template('profile.html', profile=profile, state=state, connected=connected,
                               recevied_invitation=recevied_invitation, sent_invitation=sent_invitation)
    return redirect(url_for('main.login'))

@main.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        return update_user_infos(request)
        
    user = User._find_by_username(session['username'])
    return render_template('user.html', user)

@main.route('/change-password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return change_password(request)

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404