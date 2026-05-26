# imagen base — Python 3.11 en su versión más ligera
FROM python:3.11-slim

# evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# evita buffering en los logs — ves los prints en tiempo real
ENV PYTHONUNBUFFERED=1

# directorio de trabajo dentro del contenedor
WORKDIR /app

# instala dependencias del sistema necesarias para psycopg2 y Pillow
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# copia primero solo requirements.txt
# Docker cachea cada capa — si no cambia requirements.txt
# no reinstala dependencias en cada build
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copia el resto del proyecto
COPY . .

# puerto que expone el contenedor
EXPOSE 8000

# comando por defecto al iniciar el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]