from flask import flash, Blueprint, render_template, session, redirect, url_for, request, abort
from werkzeug.security import generate_password_hash, check_password_hash

from ORM.tables.user import User

def update_user_infos(request):
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
    image = request.files.get('profile_image')
    bio = request.form.get('bio')
    gender = request.form.get('gender')
    gender_pref = request.form.get('gender_pref')
    tags = request.form.getlist('tags')
    
    # --------------- VERIFICATION DES INFOS ----------------------
    if username == '' or last_name == '' or first_name == '' or age == '' or email == '' or image == '' or bio == '' \
        or gender == '' or gender_pref == '' or tags == []:
        flash('Nan gros, t\'as pas compris... T\'as pas le droit à des valeurs null', 'danger')
        return render_template('user.html')

    # --------------- INTERCEPTER MODIFICATIONS ----------------------
    user = User._find_by_username(username)
    if user:
        data = {}
        if username != user.username:
            data['username'] = user.username
        if last_name != user.last_name:
            data['last_name'] = user.last_name
        if first_name != user.first_name:
            data['first_name'] = user.first_name
        if age != user.age:
            data['age'] = user.age
        if email != user.email:
            data['email'] = user.email
        if image != user.image:
            data['profile_image'] = user.image
        if bio != user.bio:
            data['bio'] = user.bio
        if gender != user.gender:
            data['gender'] = user.gender
        if gender_pref != user.gender_pref:
            data['gender_pref'] = user.gender_pref
        if tags != user.tags:
            data['tags'] = tags

        user.update(data)
        flash('C\'est carré : update infos', 'success')

    return render_template('user.html')

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
                    'passsword':  hashed_new_password
                }
                user.update(data)
                flash('C\'est carré : update password', 'success')
    else:
        flash('Tu sais pas écrire enfaite ? confirm_password ne correspond pas avec new_password', 'danger')
    return redirect(url_for('main.user'))
