#!/bin/bash

# Variables
COMPOSE_FILE="docker-compose.yml"
DB_NAME="matchadb"
DB_USER="guillaume"
DB_PASSWORD="admin"
DB_PORT="5432"
DB_HOST="127.0.0.1"
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"

# Construire les services Docker
echo "Building Docker Compose services..."
docker compose -f $COMPOSE_FILE build

# Lancer les services Docker en arrière-plan
echo "Starting Docker Compose services..."
docker compose -f $COMPOSE_FILE up -d

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL to be ready..."
until psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q'; do
  echo "PostgreSQL is not ready yet. Waiting..."
  sleep 2
done
echo "PostgreSQL is ready."

# Créer la base de données si elle n'existe pas
echo "Checking if database $DB_NAME exists..."
if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  echo "Database '$DB_NAME' does not exist. Creating it..."
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
else
  echo "Database '$DB_NAME' already exists."
fi

# Appliquer le dump SQL
echo "Running dump.sql to populate the database..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f ./init.sql

# Installer les dépendances Flask dans l'environnement virtuel
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
fi

echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Installer les requirements si ce n'est pas déjà fait
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "Installing requirements from $REQUIREMENTS_FILE..."
  pip install -r $REQUIREMENTS_FILE
else
  echo "No $REQUIREMENTS_FILE found, skipping installation of dependencies."
fi

# Démarrer l'application Flask
echo "Starting Flask application..."
export FLASK_APP=./app/app.py     # Remplace 'app.py' par le fichier de ton application Flask
export FLASK_ENV=development  # Utilise 'production' si tu veux déployer en mode production
flask run --host=0.0.0.0 --port=5000 --debug

# Fin du script
echo "Flask app is running on http://localhost:5000"
