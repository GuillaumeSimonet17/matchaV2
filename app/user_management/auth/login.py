from werkzeug.security import check_password_hash
from flask import session

from ORM.tables.user import User

def auth_login(request):
    username = request.form['username']
    password = request.form['password']
    
    user = User._find_by_username(username)
    if user:
        if check_password_hash(user.password, password):
            session['username'] = username
            session['user_id'] = user.id
            return True
    
    return False
