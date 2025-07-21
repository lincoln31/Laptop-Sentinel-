FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    libopenexr-3-1-30 \
    libatlas-base-dev \
    python3-dev \
    python3-numpy \
    libtbb12 \
    libtbb-dev \
    libdc1394-dev \
    ffmpeg \
    libportaudio2 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*


# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app.py .

# Crear directorio para grabaciones
RUN mkdir -p /app/recordings
RUN mkdir -p /app/templates

# Exponer puerto
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]