#!/usr/bin/env python3
"""
Script de génération d'utilisateurs fictifs pour l'application Matcha
Il génère 500 utilisateurs avec des données réalistes
"""

import random
import string
import json
import hashlib
import datetime
import os
import sys
import requests
import io
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql

# Initialiser Faker avec différentes locales pour plus de diversité
fake = Faker(['fr_FR', 'en_US', 'es_ES', 'it_IT', 'de_DE'])

# Configuration
NUM_USERS = 500
PASSWORD_HASH = hashlib.sha256("Password123!".encode()).hexdigest()
MIN_AGE = 18
MAX_AGE = 65
GENDERS = ["male", "female", "unspecified"]
GENDER_PREFS = ["male", "female", "unspecified"]
FRANCE_LAT_BOUNDS = (42.0, 51.0)
FRANCE_LNG_BOUNDS = (-5.0, 8.0)

# URLs d'images de profil garanties valides
# Utilisation d'Unsplash avec des collections d'avatars
PROFILE_IMAGES = [
    # Images masculines
    [
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80",
        "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=300&q=80",
        "https://images.unsplash.com/photo-1568602471122-7832951cc4c5?w=300&q=80",
        "https://images.unsplash.com/photo-1564564321837-a57b7070ac4f?w=300&q=80",
        "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=300&q=80",
    ],
    # Images féminines
    [
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&q=80",
        "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&q=80",
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&q=80",
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&q=80",
        "https://images.unsplash.com/photo-1554151228-14d9def656e4?w=300&q=80",
    ],
    # Images neutres/non-binaires
    [
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=300&q=80",
        "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=300&q=80",
        "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=300&q=80",
    ]
]

# Créer une liste plate de toutes les images
ALL_PROFILE_IMAGES = [img for gender_imgs in PROFILE_IMAGES for img in gender_imgs]

# Intérêts prédéfinis (à partir des tags existants dans init.sql)
INTERESTS = [
  'Cooking and Gastronomy', 'Sport and Fitness', 'Travel', 'Music',
    'Cinema and Series', 'Nature and Hiking', 'Video Games', 'Art'
]

def get_db_connection():
    """Establishes a connection to the PostgreSQL"""
    # Récupérer les variables d'environnement
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')
    db_port = os.environ.get('POSTGRES_PORT', '5432')
    db_name = os.environ.get('POSTGRES_DB', 'matchadb')
    db_user = os.environ.get('POSTGRES_USER', 'guillaume')
    db_password = os.environ.get('POSTGRES_PASSWORD', 'admin')
    
    # Afficher les paramètres de connexion (sans le mot de passe)
    print(f"Connexion to PostgreSQL: {db_host}:{db_port}/{db_name} (user: {db_user})")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        sys.exit(1)

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Vérifier si la requête a réussi
        return response.content
    except Exception as e:
        print(f"Error while uploading the image {url}: {e}")
        return None

def generate_users(num_users):
    users = []
    
    # Nombre total d'images disponibles
    num_images = len(ALL_PROFILE_IMAGES)
    print(f"Number of available images: {num_images}")
    
    image_data = download_image("https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&q=80")

    
    # Ensuite, créer le reste des utilisateurs sans photo
    for i in range(num_users):
        gender_index = random.randint(0, len(GENDERS) - 1)
        gender = GENDERS[gender_index]
        
        if gender == "Male":
            first_name = fake.first_name_male()
        elif gender == "Female":
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name()
        
        last_name = fake.last_name()
        age = random.randint(MIN_AGE, MAX_AGE)
        
        user = {
            "username": f"{first_name.lower()}_{last_name.lower()}_{random.randint(1, 999)}",
            "last_name": last_name,
            "first_name": first_name,
            "age": age,
            "password": PASSWORD_HASH,
            "email": fake.email(),
            "profile_image": image_data,  # Pas de photo
            "bio": fake.paragraph(nb_sentences=3),
            "gender": gender,
            "gender_pref": random.choice(GENDER_PREFS),
            "fame_rate": random.randint(0, 500),
            "connected": random.choice([True, False]),
            "lng": random.uniform(*FRANCE_LNG_BOUNDS),
            "lat": random.uniform(*FRANCE_LAT_BOUNDS),
            "location": fake.city(),
            "allow_geoloc": random.choice([True, False]),
            "is_verified": True,
            "last_connection": datetime.datetime.now(),
            "tags": random.sample(INTERESTS, random.randint(1, min(5, len(INTERESTS))))
        }
        users.append(user)
    
    print(f"Generated {len(users)} users ({num_images} with photo)")
    return users

def seed_users(users):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Insérer les utilisateurs
        print("Inserting users into the database...")
        
        for i, user in enumerate(users):
            try:
                # Insérer l'utilisateur avec ou sans image
                if user["profile_image"]:
                    cur.execute("""
                        INSERT INTO app_user (
                            username, last_name, first_name, age, password, 
                            email, bio, gender, gender_pref, fame_rate, 
                            connected, lng, lat, location, allow_geoloc, is_verified,
                            profile_image, last_connection
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s
                        ) RETURNING id
                    """, (
                        user["username"], user["last_name"], user["first_name"], user["age"],
                        user["password"], user["email"], user["bio"], user["gender"],
                        user["gender_pref"], user["fame_rate"], user["connected"],
                        user["lng"], user["lat"], user["location"], user["allow_geoloc"],
                        user["is_verified"], psycopg2.Binary(user["profile_image"]), user['last_connection']
                    ))
                else:
                    cur.execute("""
                        INSERT INTO app_user (
                            username, last_name, first_name, age, password, 
                            email, bio, gender, gender_pref, fame_rate, 
                            connected, lng, lat, location, allow_geoloc, is_verified
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING id
                    """, (
                        user["username"], user["last_name"], user["first_name"], user["age"],
                        user["password"], user["email"], user["bio"], user["gender"],
                        user["gender_pref"], user["fame_rate"], user["connected"],
                        user["lng"], user["lat"], user["location"], user["allow_geoloc"],
                        user["is_verified"]
                    ))
                
                user_id = cur.fetchone()[0]
                
                # 2. Associer des tags (intérêts) à l'utilisateur
                for tag_name in user["tags"]:
                    # Récupérer l'ID du tag
                    cur.execute("SELECT id FROM tag WHERE name = %s", (tag_name,))
                    tag_result = cur.fetchone()
                    
                    if tag_result:
                        tag_id = tag_result[0]
                        # Créer l'association user-tag
                        cur.execute("""
                            INSERT INTO user_tag (user_id, tag_id) 
                            VALUES (%s, %s) ON CONFLICT DO NOTHING
                        """, (user_id, tag_id))
                
                # Afficher la progression
                if (i + 1) % 50 == 0:
                    print(f"Progrss: {i + 1}/{len(users)} insert users")
                    # Valider régulièrement pour éviter de perdre tout en cas d'erreur
                    conn.commit()
            
            except Exception as e:
                print(f"Error while inserting the user {user['username']}: {e}")
                conn.rollback()  # Annuler cette transaction
                continue
        
        # Valider les insertions d'utilisateurs
        conn.commit()
       
    except Exception as e:
        conn.rollback()
        print(f"Error when inserting datas: {e}")
    finally:
        cur.close()
        conn.close()

def count_existing_users():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM app_user")
        count = cur.fetchone()[0]
        return count
    except Exception as e:
        print(f"Error while counting users : {e}")
        return 0
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Compter les utilisateurs existants
    existing_users = count_existing_users()
    print(f"Number of existing users.: {existing_users}")
    
    # Calculer combien d'utilisateurs nous devons créer
    users_to_create = max(0, NUM_USERS - existing_users)
    
    if users_to_create > 0:
        print(f"Generating {users_to_create} new users...")
        users = generate_users(users_to_create)
        seed_users(users)
    else:
        print(f"The database already contains {existing_users} users, which is sufficient.")
        print(f"Minimum required: {NUM_USERS}")
