from flask import Blueprint, flash, render_template, session, redirect, url_for, request, abort
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
        return render_template('search.html')
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


@main.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('main.login'))

@main.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        return update_user_infos(request)
        
    if 'username' in session:
        return render_template('user.html')
    return redirect(url_for('main.login'))

@main.route('/change-password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return change_password(request)


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404