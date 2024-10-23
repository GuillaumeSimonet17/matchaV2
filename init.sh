#!/bin/bash

# Arrêter le script si une commande échoue
set -e

export $(grep -v '^#' .env | xargs)

# Vérifier si le venv existe, sinon le créer
if [ ! -d ".venv" ]; then
  echo "Virtual environment (venv) not found. Creating venv..."
  python3 -m venv .venv
fi

# Activer l'environnement virtuel
echo "Activating virtual environment..."
source .venv/bin/activate

# Installer les dépendances si elles ne sont pas déjà installées
if ! pip freeze | grep -q Flask; then
  echo "Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
fi

# Lancer Docker Compose pour démarrer PostgreSQL
echo "Starting Docker Compose for PostgreSQL..."
docker compose up -d

# Attendre que la base de données PostgreSQL soit prête
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready!"

#echo "Creating database if it doesn't exist..."
#if ! psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U guillaume -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'matcha'" | grep -q 1; then
#  psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U guillaume -d postgres -c "CREATE DATABASE matcha;"
#  echo "Database 'matcha' created."
#else
#  echo "Database 'matcha' already exists."
#fi

echo "Init.sql run"
cat init.sql | psql -h localhost -p 5432 -U guillaume matcha
echo "Init.sql done"

# Lancer l'application Flask
echo "Starting Flask application..."
cd app
flask run --debug
