import requests, os, jwt, re
from random import choice, randint
from flask import request, session, redirect, url_for, jsonify, make_response
from datetime import datetime, timedelta
from ORM.tables.user import User

SECRET_KEY = os.getenv('SECRET_KEY')

def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    if response.status_code == 200:
        return response.json()["ip"]
    else:
        return "Erreur lors de la récupération de l'adresse IP publique."


def get_random_pwd(n):
    alpha_min = [chr(i) for i in range(97, 123)]
    alpha_maj = [chr(i) for i in range(65, 91)]
    number = [chr(i) for i in range(48, 58)]
    char_spe = ['%', '_', '-', '!', '$', '^', '&', '#', '(', ')', '[', ']', '=', '@']
    
    alphabets = dict()
    key = 0
    alphabets[key] = alpha_min
    key += 1
    alphabets[key] = alpha_maj
    key += 1
    alphabets[key] = number
    key += 1
    alphabets[key] = char_spe
    key += 1
    
    mdp = ''
    for i in range(n):
        s = randint(0, key - 1)
        mdp += choice(alphabets[s])
    
    return mdp

from functools import wraps

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        cookies = request.headers.get('Cookie')
        match = None
        if cookies:
            match = re.search(r"access_token=([^;]+)", cookies)
        token = None
        if match:
            token = match.group(1)
        if not match or not token:
            session.clear()
            return redirect(url_for('main.login'))
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if decoded['exp'] < datetime.utcnow().timestamp() + 300: # 5 minutes
                user = User._find_by_username(session['username'])
                new_token = jwt.encode(
                    {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                    SECRET_KEY,
                    algorithm='HS256'
                )
                response = make_response(f(*args, **kwargs))
                response.set_cookie('access_token', new_token, httponly=True)
                return response
            request.user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            session.clear()
            return redirect(url_for('main.login'))
        except jwt.InvalidTokenError:
            session.clear()
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapper
