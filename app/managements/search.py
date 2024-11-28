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

def go_search():

    user_id = session['user_id']
    user = User._find_by_id(user_id)

    user_tag_ids = UserTag.find_tags_by_user_id(user_id)
    user_tags = []
    tag_ids = []
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
    
    profile_filtered_blocked_ids = filtered_blocked_profiles(user_id, all_profiles_without_me)
    gendered_profiles = filtered_gender_profiles(user, profile_filtered_blocked_ids)

    sorted_profiles_by_tags_and_location = sort_profiles_by_tags_and_location(tag_ids, location, gendered_profiles)

    if all_profiles:
        final_profiles = []
        for profile in sorted_profiles_by_tags_and_location:

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

    nb_notifs = get_numbers_of_notifs()
    nb_notifs_msg = get_numbers_of_notifs_msg()
    return render_template('search.html', filtered_profiles=final_profiles, user_id=user_id,
                           nb_notifs=nb_notifs, nb_notifs_msg=nb_notifs_msg, user_tags=user_tags,
                           user_lat=user_lat, user_lng=user_lng)
