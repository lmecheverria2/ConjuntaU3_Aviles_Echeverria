# Imagen base
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia dependencias y código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código
COPY . .

# Expone el puerto
EXPOSE 8000

# Comando para arrancar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
