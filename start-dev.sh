#!/bin/bash

# Charger les variables d'environnement
source .env

# Lancer la base de données avec Docker Compose
echo "Démarrage de la base de données PostgreSQL..."
docker compose up -d matchadb

# Attendre que PostgreSQL soit prêt
echo "Attente de la disponibilité de PostgreSQL..."
until docker compose exec matchadb pg_isready -U $POSTGRES_USER; do
    echo "En attente de PostgreSQL..."
    sleep 2
done

# Vérifier si la base de données existe
echo "Vérification de l'existence de la base de données $POSTGRES_DB..."
if ! docker compose exec matchadb psql -U $POSTGRES_USER -lqt | cut -d \| -f 1 | grep -qw $POSTGRES_DB; then
    echo "Création de la base de données $POSTGRES_DB..."
    docker compose exec matchadb createdb -U $POSTGRES_USER $POSTGRES_DB
    
    # Exécuter le script d'initialisation si la base vient d'être créée
    echo "Initialisation de la base de données avec init.sql..."
    docker compose exec -T matchadb psql -U $POSTGRES_USER -d $POSTGRES_DB < init.sql
fi

# Activer l'environnement virtuel si il existe
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Lancer l'application Flask
echo "Démarrage de l'application Flask..."
export FLASK_APP=./app/app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000 --debug 