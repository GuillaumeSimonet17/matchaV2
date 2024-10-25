import os
from flask import Blueprint, flash, request, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from ORM.tables.user import User
from ORM.tables.tag import UserTag, Tag
from ORM.views.profile import Profile
from ORM.tables.friendship import Friendship


main = Blueprint('main', __name__)


def update_user_infos(request, user, user_tag_ids, tags):
    # normalement dans le form j'ai toute les infos du user déjà entré
    # si un champ est vide : error
    # récup le user et check les modif
    # faire data {} avec modif
    # call update
    
    # --------------- RECUPERATION DES INFOS ----------------------
    username = request.form.get('username')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    age = request.form.get('age')
    email = request.form.get('email')
    # image = request.files.get('profile_image')
    bio = request.form.get('bio')
    gender = request.form.get('gender')
    gender_pref = request.form.get('gender_pref')
    tag_ids_selected = request.form.getlist('tags[]')

    # --------------- VERIFICATION DES INFOS ----------------------
    # TODO : or image == ''
    if username == '' or last_name == '' or first_name == '' or age == '' or email == ''  or bio == '' \
            or gender == '' or gender_pref == '' or tag_ids_selected == []:
        flash('Nan gros, t\'as pas compris... T\'as pas le droit à des valeurs null', 'danger')
        return render_template('user.html', user=user, user_tag_ids=user_tag_ids, tags=tags)

    # --------------- INTERCEPTER MODIFICATIONS ----------------------
    user = User._find_by_username(username)
    if user:
        data = {}
        if username != user.username:
            data['username'] = username
        if last_name != user.last_name:
            data['last_name'] = last_name
        if first_name != user.first_name:
            data['first_name'] = first_name
        if int(age)  != user.age:
            data['age'] = age
        if email != user.email:
            data['email'] = email
        # if image != user.profile_image:
        #     data['profile_image'] = image
        if bio != user.bio:
            data['bio'] = bio
        if gender != user.gender:
            data['gender'] = gender
        if gender_pref != user.gender_pref:
            data['gender_pref'] = gender_pref
        
        new_tags = []
        for tag_id_selected in tag_ids_selected:
            if tag_id_selected not in user_tag_ids:
                new_tags.append(tag_id_selected)

        # TODO :
        # if new_tags:
            #update les tags : add new ones and delete old ones that not in new_tags

        if data:
            user.update(data)
            user = User._find_by_id(user.id)
            flash('C\'est carré : update infos', 'success')
        else:
            flash('T\'as rien changé, tu vas pas nous la faire', 'danger')
    
    return render_template('user.html', user=user, tags=tags, user_tag_ids=user_tag_ids)


def change_password(request):
    # call update
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if confirm_password == new_password:
        user = User._find_by_username(session['username'])
        if user:
            hashed_current_password = generate_password_hash(current_password)
            if check_password_hash(user.password, hashed_current_password):
                hashed_new_password = generate_password_hash(new_password)
                data = {
                    'passsword': hashed_new_password
                }
                user.update(data)
                flash('C\'est carré : update password', 'success')
    else:
        flash('Tu sais pas écrire enfaite ? confirm_password ne correspond pas avec new_password', 'danger')
    return redirect(url_for('main.user'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'webp']

def auth_register(request):
    valid = True
    
    # --------------- RECUPERATION DES INFOS ----------------------
    username = request.form.get('username')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    age = request.form.get('age')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    email = request.form.get('email')
    image = request.files.get('profile_image')
    bio = request.form.get('bio')
    gender = request.form.get('gender')
    gender_pref = request.form.get('gender_pref')
    tags = request.form.getlist('tags[]')
    
    # --------------- VERIFICATION DES INFOS ----------------------
    if len(username) < 3:
        valid = False
        flash('Tu sais pas lire enfaite ? C\'est  3 lettres minimum le username...', 'danger')
    if password != confirm_password:
        valid = False
        flash('T\'as pas mis les même mots de passe.. T\'es con enfaite ?', 'danger')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        # image_data = image.read()
        file_path = os.path.join('uploads/', filename)
        image.save(file_path)
    
    # --------------- CREATE USER OR DISPLAY ERROR MESSAGE ----------------------
    if valid == True:
        hashed_password = generate_password_hash(password)
        
        data = {
            'username': username,
            'password': hashed_password,
            'last_name': last_name,
            'first_name': first_name,
            'age': age,
            'email': email,
            'profile_image': image.filename,
            'bio': bio,
            'gender': gender,
            'gender_pref': gender_pref,
        }

        user_id = create_user(data)
        if user_id:
            create_tags(user_id, tags)
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('main.home'))
        flash('Username ou email déjà utilisé', 'danger')

    return render_template('register.html')

def create_user(data):
    user = User(None, data['username'], data['last_name'], data['first_name'], data['age'], data['password'],
                data['email'], data['profile_image'], data['bio'], data['gender'], data['gender_pref'])
    try:
        user_created = user.create()
        return user_created
    except Exception as e:
        print(e)
        return None

def create_tags(user_id, tag_ids):
    for tag_id in tag_ids:
        user_tag = UserTag(None, user_id, tag_id)
        user_tag.create()

def auth_login(request):
    username = request.form['username']
    password = request.form['password']
    
    user = User._find_by_username(username)
    if user:
        if check_password_hash(user.password, password):
            session['username'] = username
            session['user_id'] = user.id
            return True
    
    if username == 'admin' and password == 'psd':  # Remplacez par votre logique
        session['username'] = username
        return True
    
    return False

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
        all_profiles = Profile._all()
        filtered_profiles = [profile for profile in all_profiles if profile.id != session['user_id'][0]]
        # filtrer ceux que j'ai block et qui m'ont block
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
        # add historic tp user_id in db AND a notif to profile_id
        return render_template('profile.html', profile=profile, state=state, connected=connected,
                               recevied_invitation=recevied_invitation, sent_invitation=sent_invitation)
    return redirect(url_for('main.login'))

@main.route('/user', methods=['GET', 'POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    user = User._find_by_username(session['username'])
    user_tags = UserTag.find_tags_by_user_id(user.id)
    tags = Tag._all()
    user_tag_ids = [tag.tag_id for tag in user_tags]
    if request.method == 'POST':
        return update_user_infos(request, user=user, user_tag_ids=user_tag_ids, tags=tags)

    return render_template('user.html', user=user, user_tag_ids=user_tag_ids, tags=tags)

@main.route('/change-password', methods=['POST'])
def update_password():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return change_password(request)

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404