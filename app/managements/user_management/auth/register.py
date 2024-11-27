import requests

from flask import flash, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash

from ORM.tables.user import User
from ORM.tables.tag import UserTag


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
    if not tags:
        valid = False
    if len(username) < 3:
        valid = False
        flash('Tu sais pas lire enfaite ? C\'est  3 lettres minimum le username...', 'danger')
    if password != confirm_password:
        valid = False
        flash('T\'as pas mis les même mots de passe.. T\'es con enfaite ?', 'danger')
    if not image:
        valid = False
        flash('Met une image frère', 'danger')
    if image and allowed_file(image.filename):
        image_data = image.read()
    
    # --------------- CREATE USER OR DISPLAY ERROR MESSAGE ----------------------
    if valid == True:
        hashed_password = generate_password_hash(password)
        
        location = request.form.get('location')
        API_KEY = 'ad10d1fa56804356afea60668546b54f'
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={API_KEY}"
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
            'connected': True,
            'location': location,
            'lng': lng,
            'lat': lat,
        }

        user_id = create_user(data)

        if user_id:
            User.save_profile_image(user_id, image_data)
            create_tags(user_id, tags)
            session['username'] = username
            session['user_id'] = user_id
            print('IN CREATE USER == USER_ID ==> ', user_id)
            session['current_page'] = 'home'
            return redirect(url_for('main.home'))
        flash('Username ou email déjà utilisé', 'danger')
    
    return render_template('register.html')
