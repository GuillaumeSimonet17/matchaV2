#!/bin/bash
set -e

echo "=== Initialisation de la base de données pour Matcha ==="

# Exécuter le script SQL d'initialisation
echo "Exécution du script SQL pour créer les tables..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init.sql

echo "Vérification de la structure de la base de données..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "\dt"

echo "=== Initialisation de la base de données terminée ==="
echo "Vous pouvez maintenant exécuter ./populate-db.sh pour ajouter 500 utilisateurs fictifs."
