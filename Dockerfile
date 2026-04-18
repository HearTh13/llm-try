# Gunakan image Python resmi
FROM python:3.9-slim

# Set folder kerja di dalam container
WORKDIR /code

# Copy file requirements dan instal library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua kode dari folder app lokal ke dalam container
COPY ./app ./app

# Jalankan perintah untuk menyalakan server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]