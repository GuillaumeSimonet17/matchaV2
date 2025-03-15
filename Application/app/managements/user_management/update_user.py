import requests
import os
import magic

from flask import flash, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

from ORM.tables.user import User
from ORM.tables.tag import UserTag
from managements.utils import get_public_ip


API_IPFLARE_KEY = os.getenv('API_IPFLARE_KEY')

def update_user_infos(request, profile_image_data, user_tag_ids, tags):

    session_username = session.get('username')
    if not session_username:
        return False

    user = User._find_by_username(session.get('username'))
    if not session_username:
        return False

    # --------------- RECUPERATION DES INFOS ----------------------
    username = request.form.get('username')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    age = request.form.get('age')
    email = request.form.get('email')
    bio = request.form.get('bio')
    gender = request.form.get('gender')
    gender_pref = request.form.get('gender_pref')
    tag_ids_selected = request.form.getlist('tags[]')
    new_image = request.files.get('new_profile_image')
    
    new_image_filename = False
    if new_image:
        new_image_filename = new_image.filename
        mime = magic.Magic(mime=True)
        new_image = new_image.read()
        mime_type = mime.from_buffer(new_image)
    
        if not mime_type.startswith('image/'):
            flash('C\'est pas une image, tu vas pas nous la faire !', 'danger')
            return render_template('user.html', user=user, profile_image_data=profile_image_data,
                                   user_tag_ids=user_tag_ids, tags=tags)
    
        if new_image_filename:
            User.save_profile_image(user.id, new_image)
            profile_image_data = User.get_profile_image(user.id)

    location = request.form.get('location')

    allow_geoloc = request.form.get('allow_geoloc')
    if allow_geoloc == 'on':
        allow_geoloc = True

    new_tags = []
    for tag_id_selected in tag_ids_selected:
        if int(tag_id_selected) not in user_tag_ids:
            new_tags.append(int(tag_id_selected))
            user_tag = UserTag(None, user.id, tag_id_selected)
            user_tag.create()

    if len(tag_ids_selected) == 0:
        flash('Nan gros, t\'as pas compris... T\'as pas le droit à des valeurs null', 'danger')
        return render_template('user.html', user=user, profile_image_data=profile_image_data,
                               user_tag_ids=user_tag_ids, tags=tags)

    tag_ids_selected = [int(tag_id_selected) for tag_id_selected in tag_ids_selected]
    tags_to_delete = set(user_tag_ids) - set(tag_ids_selected)
    
    no_tags_selected = False
    if not tags_to_delete and not new_tags:
        no_tags_selected = True
        
    for tag_to_delete in tags_to_delete:
        user_tag = UserTag.find_user_tag_by_id(user.id, tag_to_delete)
        user_tag.delete()
    
    user_tag_ids = UserTag.find_tags_by_user_id(user.id)
    if user_tag_ids:
        user_tag_ids = [tag.tag_id for tag in user_tag_ids]
    else:
        user_tag_ids = []

    # --------------- VERIFICATION DES INFOS ----------------------
    if user_tag_ids == [] or username == '' or last_name == '' or first_name == '' or age == '' or email == '' or bio == '' \
            or gender == '' or gender_pref == '' or location == '':
        flash('Nan gros, t\'as pas compris... T\'as pas le droit à des valeurs null', 'danger')
        return render_template('user.html', user=user, profile_image_data=profile_image_data,
                               user_tag_ids=user_tag_ids, tags=tags)
    if int(age) < 18:
        flash('Opopop ! Qu\'est ce que tu fais là si t\'es mineur', 'danger')
        return render_template('user.html', user=user, profile_image_data=profile_image_data,
                               user_tag_ids=user_tag_ids, tags=tags)

    # --------------- INTERCEPTER MODIFICATIONS ----------------------

    if user:
        data = {}
        if username != user.username:
            data['username'] = username
        if last_name != user.last_name:
            data['last_name'] = last_name
        if first_name != user.first_name:
            data['first_name'] = first_name
        if int(age) != user.age:
            data['age'] = age
        if email != user.email:
            data['email'] = email
        if bio != user.bio:
            data['bio'] = bio
        if gender != user.gender:
            data['gender'] = gender
        if gender_pref != user.gender_pref:
            data['gender_pref'] = gender_pref
        if allow_geoloc != user.allow_geoloc:
            data['allow_geoloc'] = allow_geoloc

        if allow_geoloc and location:
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
            print('location = '
                  '', location)

            lng = geo['geometry']['lng']
            lat = geo['geometry']['lat']
            data['location'] = location
            data['lng'] = lng
            data['lat'] = lat

        if not location:
            ip = get_public_ip()
            header = {'X-API-Key': API_IPFLARE_KEY}
            geo = requests.get(
                f"https://api.ipflare.io/{ip}",
                headers=header,
            ).json()
            
            if geo.get('city'):
                city = geo['city'] + ', '
            elif geo.get('country_name'):
                city = geo['country_name'] + ', '
            else:
                city = ''
            country = geo['country_name']
            location = city + country
            print('location = '
                  '', location)

            lng = geo['longitude']
            lat = geo['latitude']
            data['location'] = location
            data['lng'] = lng
            data['lat'] = lat

        if data or not no_tags_selected:
            if data:
                print('\n', data)
                user.update(data)
                user = User._find_by_id(user.id)
                session['username'] = user.username
            flash('C\'est carré : update infos', 'success')
        if new_image_filename:
            flash('C\'est carré : update image', 'success')
        if not data and not new_image and no_tags_selected:
            flash('T\'as rien changé, tu vas pas nous la faire', 'danger')

    return render_template('user.html', user=user, profile_image_data=profile_image_data,
                           tags=tags, user_tag_ids=user_tag_ids)

def change_password(request):
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if len(new_password) < 8 or len(confirm_password) < 8:
        flash('Le nouveau mot de passe doit être avoir au moins 8 caractères.', 'danger')
        return False
    if current_password == '' or new_password == '' or confirm_password == '':
        flash('T\'as pas tout rentré, tu vas pas nous la faire', 'danger')
        return False
    if confirm_password == new_password:
        user = User._find_by_username(session['username'])
        if user:
            if check_password_hash(user.password, current_password):
                hashed_new_password = generate_password_hash(new_password)
                data = {
                    'password': hashed_new_password
                }
                user.update(data)
                flash('C\'est carré : update password', 'success')
                return True
            flash('C\'est pas le bon password', 'danger')

    else:
        flash('Tu sais pas écrire enfaite ? confirm_password ne correspond pas avec new_password', 'danger')
    return False
