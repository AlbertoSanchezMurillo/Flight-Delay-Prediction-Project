# Usar una imagen base de Python 3.8 slim
FROM python:3.8-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar las dependencias necesarias (incluyendo Flask)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación desde 'resources/web'
COPY resources/web/ .

# Expone el puerto 5010 que Flask estará escuchando
EXPOSE 5010

# Ejecuta el script predict_flask.py
CMD ["python", "predict_flask.py"]

