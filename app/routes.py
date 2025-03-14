import os, requests, jwt, datetime
from flask import Blueprint, flash, request, render_template, session, redirect, url_for, jsonify, make_response
from flask_socketio import emit, join_room
from flask_mail import Message
from itsdangerous import SignatureExpired, BadTimeSignature
from werkzeug.security import generate_password_hash

from managements.user_management.user import go_user
from managements.user_management.auth.login import auth_login
from managements.user_management.auth.register import auth_register
from managements.user_management.update_user import change_password

from managements.profile import go_profile
from managements.notif import go_notif
from managements.search import go_search, apply_filters
from managements.historic import go_historic
from managements.chat import go_chat, handle_get_messages, handle_send_message
from managements.friendship import handle_invitation, handle_block, handle_connection_friendship, handle_uninvitation
from managements.utils import get_public_ip, get_random_pwd, token_required

from ORM.tables.tag import Tag
from ORM.tables.notif import Notif
from ORM.tables.user import User

from app import socketio, serializer, mail


main = Blueprint('main', __name__)

API_IPFLARE_KEY = os.getenv('API_IPFLARE_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

connected_users = {}

@socketio.on('connection')
def handle_connection():
    handle_connect()

@socketio.on('connect')
def handle_connect():
    user_id = session.get("user_id")
    sid = request.sid
    if user_id:
        connected_users[sid] = user_id
        user = User._find_by_id(user_id)
        if user and session.get("user_id"):
            user.update({'connected': True})
        join_room(f"user_{user_id}")

@socketio.on('disconnection')
def handle_disconnection():
    handle_disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    user_id = connected_users.pop(sid, None)
    if user_id:
        logout()

# PROFILE/FRIENDSHIP ---------------
@socketio.on('send_invitation')
@token_required
def send_invitation_route(data):
    user_id = session['user_id']
    if user_id:
        data['sender_id'] = user_id
        handle_invitation(data)

@socketio.on('send_block')
@token_required
def send_block_route(data):
    user_id = session['user_id']
    if user_id:
        data['sender_id'] = user_id
        handle_block(data)

@socketio.on('send_connection')
@token_required
def send_connection_route(data):
    user_id = session['user_id']
    if user_id:
        data['sender_id'] = user_id
        handle_connection_friendship(data)

@socketio.on('send_uninvitation')
@token_required
def send_uninvitation_route(data):
    user_id = session['user_id']
    if user_id:
        data['sender_id'] = user_id
        handle_uninvitation(data)


@socketio.on('view_profile')
@token_required
def view_profile(data):
    user_id = session.get('user_id')
    username = session.get('username')
    receiver_id = data['receiver_id']
    
    emit('receive_view_profile',
         {'receiver_id': receiver_id, 'sender_id': user_id, 'sender_username': username},
         room=f'user_{int(data['receiver_id'])}')


# CHAT ---------------
@socketio.on('get_messages')
@token_required
def get_messages(data):
    handle_get_messages(data)

@socketio.on('send_message')
@token_required
def send_message(data):
    handle_send_message(data)

@socketio.on('received_message')
@token_required
def received_message(data):
    if data['sender_id'] == session['current_channel']:
        data['profile_id'] = data['sender_id']
        handle_get_messages(data)
        
        notifs_exist = Notif.find_notifs('message', int(data['profile_id']), int(session['user_id']))
        if isinstance(notifs_exist, Notif):
            notifs_exist = list(notifs_exist)
        
        unviewed_notif_ids = [notif.id for notif in notifs_exist if not notif.read]
        Notif.mark_as_read(unviewed_notif_ids)

@socketio.on('mark_notifs_as_read')
@token_required
def mark_notifs_as_read(data):
    user_id = session['user_id']
    if user_id:
        Notif.mark_notifs_by_user_id_as_read(user_id)


# --------------------------- HTTP ---------------------------
@main.route('/get_location', methods=['GET'])
def get_location():
    ip = get_public_ip()
    header = {'X-API-Key': API_IPFLARE_KEY}
    response = requests.get(
        f"https://api.ipflare.io/{ip}",
        headers=header,
    )
    return response.json()

@main.route('/report-fake-account/<int:profile_id>', methods=['POST'])
@token_required
def report_fake_account(profile_id):
    try:
        msg = Message("Reporting fake account", recipients=['gui_le_boat@gmail.com'], sender='gui_le_boat@gmail.com')
        msg.body = f"User with ID {profile_id} has been report as fake account."
        mail.send(msg)
        return jsonify({"status": "success", "message": "Report successfully submitted!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@main.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        user = User._find_by_email(email)
        user.update({'is_verified': True, 'connected': True})
        session['username'] = user.username
        session['user_id'] = user.id
        session['current_page'] = 'home'
        return redirect(url_for('main.home'))
    except SignatureExpired:
        return "The confirmation link has expired.", 400
    except BadTimeSignature:
        return "Invalid confirmation link.", 400

@main.route('/get_current_page', methods=['GET'])
@token_required
def get_current_page():
    current_page = session.get('current_page', 'default')
    current_profile_id = session.get('profile_id', 'default')
    current_channel = session.get('current_channel', 'default')
    return jsonify(
        {'current_page': current_page, 'current_profile_id': current_profile_id, 'current_channel': current_channel})

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        res, msg = auth_login(request)
        if res:
            user = User._find_by_username(session['username'])
            user.update({'connected': True})
            token = jwt.encode(
                {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                SECRET_KEY,
                algorithm='HS256'
            )
            response = make_response(redirect(url_for('main.home')))
            response.set_cookie('access_token', token, httponly=True, secure=True)
            return response

        flash(msg, 'danger')

    if 'username' in session:
        session['current_page'] = 'home'
        session['current_channel'] = None
        return redirect(url_for('main.home'))

    return render_template('login.html')

@main.route('/logout')
@token_required
def logout():
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    session.pop('username', None)
    session.pop('current_page', None)
    session.pop('current_channel', None)

    user = User._find_by_id(session['user_id'])
    user.update({'connected': False})

    session.pop('user_id', None)

    response = make_response(redirect(url_for('main.login')))
    response.set_cookie('access_token', '', httponly=True, secure=True)
    return response

@main.route('/register', methods=['GET', 'POST'])
def register():
    all_tags = Tag._all()
    
    if request.method == 'POST':
        return auth_register(request, all_tags)
    return render_template('register.html', all_tags=all_tags)

@main.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('reset_password.html')
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            reset_password = get_random_pwd(20)
            reset_hashed_password = generate_password_hash(reset_password)

            user = User._find_by_email(email)
            if not user:
                flash('Email not found', 'danger')
            else:
                user.update({'password': reset_hashed_password})
    
                msg = Message("Reset Password", recipients=[email], sender='gui_le_boat@gmail.com')
                msg.body = (f"Hello, here is your new password: {reset_password}\n"
                            f"Don't forget to change it once you're logged in.")
                mail.send(msg)
                flash('Mail sent', 'success')
            return render_template('reset_password.html')

@main.route('/apply_filters', methods=['POST'])
@token_required
def apply_filters_route():
    return apply_filters(request)

@main.route('/', methods=['POST', 'GET'])
@token_required
def home():
    print('\ncoucou\n')
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    session['current_page'] = 'home'
    session['current_channel'] = None
    
    return go_search()

@main.route('/historic')
@token_required
def historic():
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    session['current_page'] = 'historic'
    session['current_channel'] = None
    return go_historic()

@main.route('/notifs', methods=['GET'])
@token_required
def notifs():
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    session['current_page'] = 'notifs'
    session['current_channel'] = None
    return go_notif()

@main.route('/chat')
@token_required
def chat():
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    return go_chat()

@main.route('/profile/<int:profile_id>')
@token_required
def profile(profile_id):
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    session['current_page'] = 'profile'
    return go_profile(profile_id)

@main.route('/user', methods=['GET', 'POST'])
@token_required
def user():
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    session['current_page'] = 'user'
    return go_user()

@main.route('/change-password', methods=['POST'])
@token_required
def update_password():
    if 'username' not in session or not User._find_by_username(session['username']):
        session.clear()
        return redirect(url_for('main.login'))
    
    if session.get('current_page') == 'notifs' and session['user_id']:
        Notif.mark_notifs_by_user_id_as_read(session['user_id'])
    
    change_password(request)
    return redirect(url_for('main.user'))

@main.app_errorhandler(404)
@token_required
def page_not_found(e):
    return render_template('404.html'), 404
