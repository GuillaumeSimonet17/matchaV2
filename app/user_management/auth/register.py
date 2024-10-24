from flask import flash, Blueprint, render_template, session, redirect, url_for, request, abort


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
    profile_image = request.files.get('profile_image')  # Pour un fichier uploadé
    bio = request.form.get('bio')
    gender = request.form.get('gender')
    gender_pref = request.form.get('gender_pref')
    tags = request.form.getlist('tags')
    
    # --------------- VERIFICATION DES INFOS ----------------------
    if password != confirm_password:
        valid = False
        flash('T\'as pas mis les même mots de passe.. T\'es con enfaite ?', 'danger')
    if len(username) < 3:
        valid = False
        flash('Tu sais pas lire enfaite ? C\'est  3 lettres minimum le username...', 'danger')

    # --------------- CREATE USER OR DISPLAY ERROR MESSAGE ----------------------
    if valid == True:
        data = {
            'username': username,
        }
        create_user(data)
        session['username'] = username
        return redirect(url_for('main.home'))
    return render_template('register.html')


def create_user(data):
    pass
