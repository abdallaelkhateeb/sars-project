FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt requirements-dev.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Use daphne for ASGI/WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "sars_core.asgi:application"]