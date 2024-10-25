from flask import Blueprint, render_template, session, redirect, url_for, request, abort
from werkzeug.security import generate_password_hash, check_password_hash


def auth_login(request):
    username = request.form['username']
    password = request.form['password']

    # recup user avec ce username
    hashed_password = generate_password_hash(password)
    is_password_correct = check_password_hash(hashed_password, password)
    
    if username == 'admin' and password == 'psd':  # Remplacez par votre logique
        session['username'] = username
        return True
    
    return False
