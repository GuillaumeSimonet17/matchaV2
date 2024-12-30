from flask import render_template, session, jsonify
from ORM.views.profile import Profile
from ORM.tables.block import Block
from ORM.tables.tag import UserTag, Tag
from ORM.tables.user import User

from managements.notif import get_numbers_of_notifs, get_numbers_of_notifs_msg

from math import radians, sin, cos, sqrt, atan2


def count_common_tags(profile_tags, user_tags):
    return len(set(profile_tags) & set(user_tags))

def filtered_blocked_profiles(user_id, all_profiles):
    blocked_ids = []
    blocked = Block.find_blocks_by_user_id(user_id)
    if blocked:
        for block in blocked:
            if block.receiver_id == user_id:
                blocked_ids.append(block.sender_id)
            else:
                blocked_ids.append(block.receiver_id)
    return [profile for profile in all_profiles if profile.id not in blocked_ids]

def filtered_gender_profiles(user, all_profiles):
    gendered_profiles = []
    for profile in all_profiles:
        if user.gender_pref == 'unspecified' and profile.gender_pref == 'unspecified':
            gendered_profiles.append(profile)
        if user.gender_pref == 'unspecified' and profile.gender == user.gender or profile.gender == 'unspecified':
            gendered_profiles.append(profile)

        if (user.gender_pref != 'unspecified' and
                (profile.gender == user.gender_pref and user.gender == profile.gender_pref
                 or profile.gender_pref == 'unspecified')):
            gendered_profiles.append(profile)
    return gendered_profiles

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux points géographiques (Haversine formula).
    """
    R = 6371  # Rayon moyen de la Terre en kilomètres
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def sort_profiles_by_tags_and_location(user_tags, user_location, profiles):
    """
    Trie les profils selon deux critères :
    - Nombre de tags en commun (priorité 1)
    - Distance géographique (priorité 2)

    :param user_tags: Liste des tags de l'utilisateur actuel.
    :param user_location: Tuple (latitude, longitude) de l'utilisateur.
    :param profiles: Liste des profils à trier.
    :return: Liste triée des profils.
    """
    user_lat, user_lon = user_location

    def compute_profile_score(profile):
        # Nombre de tags en commun
        profile_tag_ids = UserTag.find_tags_by_user_id(profile.id)
        profile_tags = [tag_id.tag_id for tag_id in profile_tag_ids]
        common_tags_count = len(set(profile_tags) & set(user_tags))

        # Distance géographique
        profile_lat = profile.lat
        profile_lon = profile.lng
        distance = calculate_distance(user_lat, user_lon, profile_lat, profile_lon)

        # Retourne les deux critères pour le tri
        return (-common_tags_count, distance)  # Note : -common_tags_count pour un tri décroissant

    # Trier les profils en fonction des critères
    return sorted(profiles, key=compute_profile_score)

def get_profiles_list(is_suggestion_list=True):
    final_profiles = []

    user_id = session['user_id']
    user = User._find_by_id(user_id)
    
    user_tag_ids = UserTag.find_tags_by_user_id(user_id)
    user_tags = []
    tag_ids = []
    if user_tag_ids:
        for tag_id in user_tag_ids:
            tag = Tag._find_by_id(tag_id.tag_id)
            if tag:
                tag_ids.append(tag.id)
                user_tags.append(tag.name)

    user_lat = user.lat
    user_lng = user.lng
    location = (user_lat, user_lng)

    all_profiles = Profile._all()
    all_profiles_without_me = [profile for profile in all_profiles if profile.id != user.id]
    profile_filtered_blocked_ids = filtered_blocked_profiles(user.id, all_profiles_without_me)

    profile_list = profile_filtered_blocked_ids
    if is_suggestion_list:
        gendered_profiles = filtered_gender_profiles(user, profile_filtered_blocked_ids)
        sorted_profiles_by_tags_and_location = sort_profiles_by_tags_and_location(tag_ids, location, gendered_profiles)
        profile_list = sorted_profiles_by_tags_and_location

    if all_profiles:
        for profile in profile_list:

            profile_tag_ids = UserTag.find_tags_by_user_id(profile.id)
            profile_tags = []
            for tag_id in profile_tag_ids:
                tag = Tag._find_by_id(tag_id.tag_id)
                if tag:
                    profile_tags.append(tag.name)
            
            image_data = Profile.get_profile_image(profile.id)
            final_profiles.append({
                'id': profile.id,
                'username': profile.username,
                'profile_image': image_data,
                'age': profile.age,
                'gender': profile.gender,
                'gender_pref': profile.gender_pref,
                'fame_rate': profile.fame_rate,
                'lng': profile.lng,
                'lat': profile.lat,
                'tags': profile_tags,
            })
 
    return final_profiles, user, user_tags, tag_ids, location, user_lat, user_lng

def go_search():

    all_tags = Tag._all()

    final_profiles, user, user_tags, tag_ids, location, user_lat, user_lng = get_profiles_list()
    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    return render_template('search.html', filtered_profiles=final_profiles, user_id=user.id,
                           nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg, user_tags=user_tags, all_tags=all_tags,
                           user_lat=user_lat, user_lng=user_lng)

def apply_filters(request):
    all_profiles_filtered = []
    filters_data = request.get_json()
    if filters_data:
        
        is_suggestion_list = filters_data.get('help')
        print('is_suggestion_list = ', is_suggestion_list)
        final_profiles, user, user_tags, tag_ids, location, user_lat, user_lng = get_profiles_list(is_suggestion_list)
        
        all_profiles_filtered = final_profiles
        age_min = filters_data.get('age_min', 18)
        age_max = filters_data.get('age_max', 100)
        location_radius = filters_data.get('location_radius', 50)
        fame_rating_min = filters_data.get('fame_rating', 3.0)

        user_lat = filters_data.get('user_lat')
        user_lon = filters_data.get('user_lon')
        
        if user_lat is None or user_lon is None:
            return jsonify({
                "success": False,
                "message": "User location (latitude and longitude) is required for location filtering."
            }), 400

        if filters_data.get('location_filter_activated'):
            distance = 0
            for profile in final_profiles:
                profile_lat = profile.get('lat')
                profile_lon = profile.get('lng')
    
                if profile_lat is None or profile_lon is None:
                    continue
    
                distance = calculate_distance(float(user_lat), float(user_lon), float(profile_lat), float(profile_lon))
        
            all_profiles_filtered = [profile for profile in final_profiles if distance <= float(location_radius)]

        if filters_data.get('fame_rate_filter_activated'):
            all_profiles_filtered = [profile for profile in final_profiles if profile['fame_rate'] >= float(fame_rating_min)]

        if filters_data.get('age_filter_activated'):
            all_profiles_filtered = [profile for profile in final_profiles if int(age_min) <= profile['age'] <= int(age_max)]

        if filters_data.get('tags_filter_activated'):
            if len(filters_data.get('selected_tags')) > 0:
                for profile in all_profiles_filtered:
                    profile_tag_ids = UserTag.find_tags_by_user_id(profile['id'])
                    profile_tags = []
                    for tag_id in profile_tag_ids:
                        tag = Tag._find_by_id(tag_id.tag_id)
                        if tag:
                            profile_tags.append(tag.name)
                    if not any(tag in filters_data.get('selected_tags') for tag in profile_tags):
                        all_profiles_filtered.remove(profile)

    response = {
        "success": True,
        "message": "Filters applied successfully!",
        "filtered_profiles": all_profiles_filtered
    }
    return jsonify(response), 200