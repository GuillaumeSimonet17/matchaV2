import os
from flask import flash, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from ORM.tables.user import User
from ORM.tables.tag import UserTag


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
    tags = request.form.getlist('tags')
    
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
        file_path = os.path.join('../../uploads/', filename)
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
        # print('data = ', data)
        user_id = create_user(data)
        print('user_id = ', user_id)
        create_tags(user_id, tags)
        session['username'] = username
        session['user_id'] = user_id
        return redirect(url_for('main.home'))
    return render_template('register.html')
    
def create_user(data):
    user = User(None, data['username'], data['last_name'], data['first_name'], data['age'], data['password'], data['email'],
                data['profile_image'], data['bio'], data['gender'], data['gender_pref'])
    print('user => ', user)
    cre = user.create()
    print('cre = ', cre)
    return cre

def create_tags(user_id, tags):
    for tag in tags:
        print('tag = ', tag)
        user_tag = UserTag.create(user_id, tag)
        user_tag.create()
