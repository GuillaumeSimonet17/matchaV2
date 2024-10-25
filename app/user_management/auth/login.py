from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from ORM.tables.user import User


def auth_login(request):
    username = request.form['username']
    password = request.form['password']

    user = User._find_by_username(username)
    print('user ici => ', user)
    if user:
        hashed_password = generate_password_hash(password)
        if check_password_hash(user.password, hashed_password):
            session['username'] = username
            session['user_id'] = user.id
            return True
        
    if username == 'admin' and password == 'psd':  # Remplacez par votre logique
        session['username'] = username
        return True

    return False
