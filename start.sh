#!/bin/bash

# Attendre que la base de données soit prête
echo "Waiting for database to be ready..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "Database is ready!"

# Démarrer l'application Flask
flask run --host=0.0.0.0 --port=5000 