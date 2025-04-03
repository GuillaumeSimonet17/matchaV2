FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ../Application/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --upgrade -r /app/requirements.txt


COPY ../Application/app /app

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["/start.sh"]