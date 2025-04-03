FROM nginx:latest

# Copier la configuration principale
COPY nginx.conf /etc/nginx/nginx.conf

# Créer les dossiers nécessaires
RUN mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

# Copier la configuration du site
COPY sites-available/matcha.conf /etc/nginx/sites-available/

# Créer le lien symbolique
RUN ln -s /etc/nginx/sites-available/matcha.conf /etc/nginx/sites-enabled/
