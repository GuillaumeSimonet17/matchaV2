#!/bin/bash
set -e

echo "Initialisation de la base de données..."

# La base de données $POSTGRES_DB est déjà créée par PostgreSQL
# car on l'a spécifiée dans les variables d'environnement

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Vérifier si les tables existent déjà
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public') THEN
            RAISE NOTICE 'Aucune table trouvée, initialisation de la base de données...';
        END IF;
    END
    \$\$;
EOSQL

echo "Initialisation terminée." 