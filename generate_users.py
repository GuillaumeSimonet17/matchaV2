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
GENDERS = ["Male", "Female", "Non-binary"]
GENDER_PREFS = ["Male", "Female", "Both"]
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
    'Cuisine et Gastronomie', 'Sport et Fitness', 'Voyages', 'Musique', 
    'Cinéma et Séries', 'Nature et Randonnée', 'Jeux Vidéo', 'Art'
]

def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL"""
    # Récupérer les variables d'environnement
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')
    db_port = os.environ.get('POSTGRES_PORT', '5432')
    db_name = os.environ.get('POSTGRES_DB', 'matchadb')
    db_user = os.environ.get('POSTGRES_USER', 'guillaume')
    db_password = os.environ.get('POSTGRES_PASSWORD', 'admin')
    
    # Afficher les paramètres de connexion (sans le mot de passe)
    print(f"Connexion à PostgreSQL: {db_host}:{db_port}/{db_name} (utilisateur: {db_user})")
    
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
        print(f"Erreur de connexion à la base de données: {e}")
        sys.exit(1)

def download_image(url):
    """Télécharge une image depuis une URL et la retourne sous forme de bytes"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Vérifier si la requête a réussi
        return response.content
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'image {url}: {e}")
        return None

def generate_users(num_users):
    """Génère une liste d'utilisateurs fictifs"""
    users = []
    
    # Nombre total d'images disponibles
    num_images = len(ALL_PROFILE_IMAGES)
    print(f"Nombre d'images disponibles: {num_images}")
    
    # D'abord, créer un utilisateur pour chaque image disponible
    for i, image_url in enumerate(ALL_PROFILE_IMAGES):
        # Télécharger l'image
        print(f"Téléchargement de l'image {i+1}/{num_images}: {image_url}")
        image_data = download_image(image_url)
        
        # Déterminer le genre en fonction de l'origine de l'image
        if i < len(PROFILE_IMAGES[0]):
            gender = "Male"
            first_name = fake.first_name_male()
        elif i < len(PROFILE_IMAGES[0]) + len(PROFILE_IMAGES[1]):
            gender = "Female"
            first_name = fake.first_name_female()
        else:
            gender = "Non-binary"
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
            "profile_image": image_data,  # Données binaires de l'image
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
            "tags": random.sample(INTERESTS, random.randint(1, min(5, len(INTERESTS))))
        }
        users.append(user)
    
    # Ensuite, créer le reste des utilisateurs sans photo
    remaining_users = num_users - num_images
    for i in range(remaining_users):
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
            "profile_image": None,  # Pas de photo
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
            "tags": random.sample(INTERESTS, random.randint(1, min(5, len(INTERESTS))))
        }
        users.append(user)
    
    print(f"Généré {len(users)} utilisateurs ({num_images} avec photo, {remaining_users} sans photo)")
    return users

def seed_users(users):
    """Insère les utilisateurs dans la base de données"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Insérer les utilisateurs
        print("Insertion des utilisateurs dans la base de données...")
        
        for i, user in enumerate(users):
            try:
                # Insérer l'utilisateur avec ou sans image
                if user["profile_image"]:
                    cur.execute("""
                        INSERT INTO app_user (
                            username, last_name, first_name, age, password, 
                            email, bio, gender, gender_pref, fame_rate, 
                            connected, lng, lat, location, allow_geoloc, is_verified,
                            profile_image
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s
                        ) RETURNING id
                    """, (
                        user["username"], user["last_name"], user["first_name"], user["age"],
                        user["password"], user["email"], user["bio"], user["gender"],
                        user["gender_pref"], user["fame_rate"], user["connected"],
                        user["lng"], user["lat"], user["location"], user["allow_geoloc"],
                        user["is_verified"], psycopg2.Binary(user["profile_image"])
                    ))
                else:
                    cur.execute("""
                        INSERT INTO app_user (
                            username, last_name, first_name, age, password, 
                            email, bio, gender, gender_pref, fame_rate, 
                            connected, lng, lat, location, allow_geoloc, is_verified
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
                    print(f"Progrès: {i + 1}/{len(users)} utilisateurs insérés")
                    # Valider régulièrement pour éviter de perdre tout en cas d'erreur
                    conn.commit()
            
            except Exception as e:
                print(f"Erreur lors de l'insertion de l'utilisateur {user['username']}: {e}")
                conn.rollback()  # Annuler cette transaction
                continue
        
        # Valider les insertions d'utilisateurs
        conn.commit()
        
        print("Tous les utilisateurs ont été insérés avec succès.")
        print("Création de relations entre utilisateurs...")
        
        try:
            # Récupérer tous les IDs d'utilisateurs
            cur.execute("SELECT id FROM app_user")
            user_ids = [row[0] for row in cur.fetchall()]
            
            # Éliminer les doublons potentiels dans les visites
            visit_pairs = set()
            for _ in range(min(1000, len(user_ids) * 2)):
                sender_id = random.choice(user_ids)
                receiver_id = random.choice(user_ids)
                
                # Éviter les auto-visites et les doublons
                if sender_id != receiver_id:
                    visit_pairs.add((sender_id, receiver_id))
            
            # Insérer les visites une par une pour éviter les conflits
            for sender_id, receiver_id in visit_pairs:
                created_at = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                try:
                    cur.execute("""
                        INSERT INTO visit (sender_id, receiver_id, created_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (sender_id, receiver_id) DO UPDATE 
                        SET updated_at = EXCLUDED.updated_at
                    """, (sender_id, receiver_id, created_at))
                except Exception as e:
                    print(f"Erreur lors de l'insertion d'une visite: {e}")
                    continue
            
            # Validation après les visites
            conn.commit()
            print(f"Visites créées: {len(visit_pairs)}")
        
            # Éliminer les doublons dans les amitiés
            friendship_data = []
            friendship_states = ["pending", "accepted", "declined"]
            friendship_pairs = set()
            
            for _ in range(min(800, len(user_ids) * 2)):
                sender_id = random.choice(user_ids)
                receiver_id = random.choice(user_ids)
                
                # Éviter les auto-amitiés et les doublons
                if sender_id != receiver_id and (sender_id, receiver_id) not in friendship_pairs:
                    friendship_pairs.add((sender_id, receiver_id))
                    state = random.choice(friendship_states)
                    friendship_data.append((state, sender_id, receiver_id))
            
            # Insérer les amitiés une par une
            for state, sender_id, receiver_id in friendship_data:
                try:
                    cur.execute("""
                        INSERT INTO friendship (state, sender_id, receiver_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (sender_id, receiver_id) DO NOTHING
                    """, (state, sender_id, receiver_id))
                except Exception as e:
                    print(f"Erreur lors de l'insertion d'une amitié: {e}")
                    continue
            
            # Validation après les amitiés
            conn.commit()
            print(f"Amitiés créées: {len(friendship_data)}")
            
            # Créer des canaux de discussion et messages pour les amitiés acceptées
            print("Création de canaux de discussion et messages...")
            
            # Récupérer les amitiés acceptées
            cur.execute("SELECT sender_id, receiver_id FROM friendship WHERE state = 'accepted'")
            accepted_friendships = cur.fetchall()
            
            for sender_id, receiver_id in accepted_friendships:
                try:
                    # Créer un canal
                    cur.execute("""
                        INSERT INTO channel (user_a, user_b)
                        VALUES (%s, %s)
                        ON CONFLICT (user_a, user_b) DO NOTHING
                        RETURNING id
                    """, (sender_id, receiver_id))
                    
                    result = cur.fetchone()
                    if result:
                        channel_id = result[0]
                        
                        # Ajouter quelques messages
                        num_messages = random.randint(1, 5)
                        for _ in range(num_messages):
                            # Choisir aléatoirement qui envoie le message
                            if random.choice([True, False]):
                                msg_sender, msg_receiver = sender_id, receiver_id
                            else:
                                msg_sender, msg_receiver = receiver_id, sender_id
                            
                            content = fake.sentence()
                            read = random.choice([True, False])
                            
                            # Insérer le message
                            cur.execute("""
                                INSERT INTO message (channel_id, sender_id, receiver_id, content, read)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (channel_id, msg_sender, msg_receiver, content, read))
                except Exception as e:
                    print(f"Erreur lors de la création d'un canal ou message: {e}")
                    continue
            
            # Validation finale
            conn.commit()
            print(f"Canaux de discussion créés: {len(accepted_friendships)}")
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de la création des relations: {e}")
        
        print(f"Insertion réussie de {len(users)} utilisateurs avec leurs relations!")
    
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'insertion des données: {e}")
    finally:
        cur.close()
        conn.close()

def count_existing_users():
    """Compte les utilisateurs existants dans la base de données"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM app_user")
        count = cur.fetchone()[0]
        return count
    except Exception as e:
        print(f"Erreur lors du comptage des utilisateurs: {e}")
        return 0
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("==== Script de génération d'utilisateurs fictifs ====")
    
    # Compter les utilisateurs existants
    existing_users = count_existing_users()
    print(f"Nombre d'utilisateurs existants: {existing_users}")
    
    # Calculer combien d'utilisateurs nous devons créer
    users_to_create = max(0, NUM_USERS - existing_users)
    
    if users_to_create > 0:
        print(f"Génération de {users_to_create} nouveaux utilisateurs...")
        users = generate_users(users_to_create)
        seed_users(users)
    else:
        print(f"La base de données contient déjà {existing_users} utilisateurs, ce qui est suffisant.")
        print(f"Minimum requis: {NUM_USERS}") 