# Usamos una imagen de Python profesional
FROM python:3.9-slim

# Instalamos herramientas básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Creamos la carpeta de la app
WORKDIR /app

# Copiamos los archivos necesarios
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de Streamlit
EXPOSE 8501

# Comando para arrancar la app
ENTRYPOINT ["streamlit", "run", "app_analista.py", "--server.port=8501", "--server.address=0.0.0.0"]
