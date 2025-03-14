import requests
import re
import os
import magic

from flask import flash, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash

from ORM.tables.user import User
from ORM.tables.tag import UserTag

from flask_mail import Message
from app import mail, serializer


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'webp']

def create_user(data):
    user = User(None, data['username'], data['last_name'], data['first_name'], data['age'], data['password'],
                data['email'], None, data['bio'], data['gender'], data['gender_pref'], data['fame_rate'],
                data['connected'], data['location'], data['lng'], data['lat'])
    try:
        user.create()
        user_created = User._find_by_username(data['username'])
        if user_created:
            return user_created.id
    except Exception as e:
        print(e)
        return None

def create_tags(user_id, tag_ids):
    for tag_id in tag_ids:
        user_tag = UserTag(None, user_id, tag_id)
        user_tag.create()

def is_valid_username(username):
    forbidden_chars = r"['\"/\\]"
    if re.search(forbidden_chars, username):
        return False
    return True

def auth_register(request, all_tags):
    valid = True

    # --------------- RECUPERATION DES INFOS ----------------------
    username = request.form.get('username')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    age = request.form.get('age')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    email = request.form.get('email')
    bio = request.form.get('bio')
    gender = request.form.get('gender')
    gender_pref = request.form.get('gender_pref')
    tags = request.form.getlist('tags[]')
    image = request.files.get('profile_image')

    # --------------- VERIFICATION DES INFOS ----------------------
    if not image:
        valid = False
        flash('Met une image frère', 'danger')

    if image and allowed_file(image.filename):
        mime = magic.Magic(mime=True)
        image = image.read()
        mime_type = mime.from_buffer(image)

        if not mime_type.startswith('image/'):
            valid = False
            flash('C\'est pas une image, tu vas pas nous la faire !', 'danger')

    if not is_valid_username(username):
        valid = False
        flash('Choisi un username sans caractères spéciaux stp beau gosse', 'danger')
    if int(age) < 18:
        valid = False
        flash('Qu\'est-ce tu fais là si t\'es mineur frr', 'danger')
    if not tags:
        valid = False
        flash('Choisi au moins un tag khey stp', 'danger')
    if len(username) < 3:
        valid = False
        flash('Tu sais pas lire enfaite ? C\'est  3 lettres minimum le username...', 'danger')
    if len(password) < 8:
        valid = False
        flash('Minimum 8 caractères pour le mot de passe stp cousin.', 'danger')
    if password != confirm_password:
        valid = False
        flash('T\'as pas mis les même mots de passe.. T\'es con enfaite ?', 'danger')
    
    # --------------- CREATE USER OR DISPLAY ERROR MESSAGE ----------------------
    if valid == True:
        hashed_password = generate_password_hash(password)
        
        location = request.form.get('location')
        API_LOC_KEY = os.getenv('API_LOC_KEY')
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={API_LOC_KEY}"
        response = requests.get(url)
        geo = response.json()
        geo = geo['results'][0]
        lng = geo['geometry']['lng']
        lat = geo['geometry']['lat']

        data = {
            'username': username,
            'password': hashed_password,
            'last_name': last_name,
            'first_name': first_name,
            'age': age,
            'email': email,
            'profile_image': None,
            'bio': bio,
            'gender': gender,
            'gender_pref': gender_pref,
            'fame_rate': 0,
            'connected': False,
            'location': location,
            'lng': lng,
            'lat': lat,
            'allow_geoloc': True,
            'is_verified': False,
        }

        user_id = create_user(data)

        if user_id:
            User.save_profile_image(user_id, image)
            create_tags(user_id, tags)

            token = serializer.dumps(email, salt='email-confirm')
            
            confirm_url = url_for('main.confirm_email', token=token, _external=True)
            
            msg = Message("Confirm Your Account", recipients=[email], sender='gui_le_boat@gmail.com')
            msg.body = f"Hello, please confirm your account by clicking on the link: {confirm_url}"
            mail.send(msg)
            
            flash('A confirmation email has been sent to your address.', 'success')
        
        else:
            flash('Username ou email déjà utilisé', 'danger')
    
    return render_template('register.html', all_tags=all_tags)
