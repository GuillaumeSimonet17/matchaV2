from werkzeug.security import check_password_hash
from flask import session
import requests
import os

from ORM.tables.user import User

def auth_login(request):
    username = request.form['username']
    password = request.form['password']
    location = request.form['location']
    
    user = User._find_by_username(username)
    if user:
        if check_password_hash(user.password, password):
            if not user.is_verified:
                return False, 'Veuillez confirmer votre compte.'
            session['username'] = username
            session['user_id'] = user.id
            
            if location != user.location:
                data = {}

                API_LOC_KEY = os.getenv('API_LOC_KEY')
                url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={API_LOC_KEY}"
                response = requests.get(url)
                geo = response.json()
                geo = geo['results'][0]

                if geo['components'].get('city'):
                    city = geo['components']['city'] + ', '
                elif geo['components'].get('county'):
                    city = geo['components']['county'] + ', '
                else:
                    city = ''

                country = geo['components']['country']
                location = city + country
                lng = geo['geometry']['lng']
                lat = geo['geometry']['lat']
                data['location'] = location
                data['lng'] = lng
                data['lat'] = lat

                user.update(data)
            return True, ''
    
    return False, 'Ecris mieux stp.'
