#!/bin/bash

echo "=== Script de peuplement de la base de données Matcha avec 500 utilisateurs ==="

# Charger les variables d'environnement si le fichier .env existe
if [ -f ".env" ]; then
    echo "Chargement des variables d'environnement depuis .env..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Fichier .env non trouvé, utilisation des valeurs par défaut."
    export POSTGRES_DB=matchadb
    export POSTGRES_USER=guillaume
    export POSTGRES_PASSWORD=admin
    export POSTGRES_PORT=5432
fi

# Vérifier si Docker est en cours d'exécution
if ! docker info &>/dev/null; then
    echo "Docker n'est pas en cours d'exécution ou n'est pas accessible."
    exit 1
fi

# Vérifier si le conteneur matchadb est en cours d'exécution
CONTAINER_NAME=$(docker compose ps | grep matchadb | awk '{print $1}')
if [ -z "$CONTAINER_NAME" ]; then
    echo "Le conteneur matchadb n'est pas en cours d'exécution."
    echo "Veuillez démarrer les conteneurs avec 'docker compose up -d' avant d'exécuter ce script."
    exit 1
fi

echo "Conteneur trouvé: $CONTAINER_NAME"

# Attendre que PostgreSQL soit prêt
echo "Attente que PostgreSQL soit prêt..."
until docker compose exec matchadb pg_isready -U ${POSTGRES_USER}; do
    echo "PostgreSQL n'est pas encore prêt. Nouvelle tentative dans 2 secondes..."
    sleep 2
done

echo "PostgreSQL est prêt."

# Vérifier le nombre d'utilisateurs existants
echo "Vérification du nombre d'utilisateurs existants..."
EXISTING_USERS=$(docker compose exec -T matchadb psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c "SELECT COUNT(*) FROM app_user;")
EXISTING_USERS=$(echo $EXISTING_USERS | tr -d '[:space:]')

echo "Nombre d'utilisateurs existants: $EXISTING_USERS"

if [ "$EXISTING_USERS" -ge 1500 ]; then
    echo "La base de données contient déjà au moins 500 utilisateurs. Aucune action requise."
    exit 0
fi

# Calculer le nombre d'utilisateurs à créer
USERS_TO_CREATE=$((1500 - EXISTING_USERS))
echo "Création de $USERS_TO_CREATE nouveaux utilisateurs..."

# Vérifier si le script generate_users.py existe
if [ ! -f "generate_users.py" ]; then
    echo "Le fichier generate_users.py n'existe pas."
    exit 1
fi

# Vérifier si Python est installé sur la machine hôte
if ! command -v python3 &> /dev/null; then
    echo "Python3 n'est pas installé sur votre machine."
    echo "Veuillez installer Python3 avant d'exécuter ce script."
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "pip3 n'est pas installé sur votre machine."
    echo "Veuillez installer pip3 avant d'exécuter ce script."
    exit 1
fi

# Installer les dépendances Python
echo "Installation des dépendances Python..."
pip3 install psycopg2-binary faker

# Configurer les variables d'environnement pour le script Python
echo "Configuration des variables d'environnement..."
export POSTGRES_HOST=localhost
# Le port Docker est exposé sur la machine hôte
export POSTGRES_PORT=${POSTGRES_PORT}
export POSTGRES_DB=${POSTGRES_DB}
export POSTGRES_USER=${POSTGRES_USER}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Exécuter le script
echo "Exécution du script pour créer 500 utilisateurs..."
python3.12 generate_users.py

echo "=== Script de peuplement terminé ===" 