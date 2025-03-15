FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système pour psycopg2, netcat et libmagic
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ../Application/requirements.txt /app/requirements.txt

#RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade -r /app/requirements.txt

ARG API_SERVER_URL
ENV API_SERVER_URL=$API_SERVER_URL

ARG NEXT_PUBLIC_API_SERVER_URL
ENV NEXT_PUBLIC_API_SERVER_URL=$NEXT_PUBLIC_API_SERVER_URL

ARG NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
ENV NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$NEXT_PUBLIC_GOOGLE_MAPS_API_KEY


COPY ../Application/app /app

# Script de démarrage
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Variables d'environnement par défaut
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["/start.sh"]