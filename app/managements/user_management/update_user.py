import requests

from flask import flash, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

from ORM.tables.user import User



def update_user_infos(request, user, profile_image_data, user_tag_ids, tags):
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
    location = request.form.get('location')

    
    # --------------- VERIFICATION DES INFOS ----------------------
    if username == '' or last_name == '' or first_name == '' or age == '' or email == '' or bio == '' \
            or gender == '' or gender_pref == '' or location == '' or tag_ids_selected == []:
        flash('Nan gros, t\'as pas compris... T\'as pas le droit à des valeurs null', 'danger')
        return render_template('user.html', user=user, profile_image_data=profile_image_data,
                               user_tag_ids=user_tag_ids, tags=tags)
    
    # --------------- INTERCEPTER MODIFICATIONS ----------------------
    user = User._find_by_username(username)
    
    # print('new_image', new_image.filename)
    if new_image.filename:
        img_read = new_image.read()
        User.save_profile_image(user.id, img_read)
        profile_image_data = User.get_profile_image(user.id)

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

        if location != user.location:
            API_KEY = 'ad10d1fa56804356afea60668546b54f'
            url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={API_KEY}"
            response = requests.get(url)
            geo = response.json()
            geo = geo['results'][0]
            print(geo)
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

        new_tags = []
        for tag_id_selected in tag_ids_selected:
            if tag_id_selected not in user_tag_ids:
                new_tags.append(tag_id_selected)
        
        # TODO :
        # if new_tags:
        # update les tags : add new ones and delete old ones that not in new_tags
        
        if data:
            user.update(data)
            user = User._find_by_id(user.id)
            session['username'] = user.username
            flash('C\'est carré : update infos', 'success')
        if new_image.filename:
            flash('C\'est carré : update image', 'success')
        if not data and not new_image:
            flash('T\'as rien changé, tu vas pas nous la faire', 'danger')
    
    return render_template('user.html', user=user, profile_image_data=profile_image_data,
                           tags=tags, user_tag_ids=user_tag_ids)


def change_password(request):
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
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