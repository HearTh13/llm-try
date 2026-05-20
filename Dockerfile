FROM python:3.11-slim

WORKDIR /code

# Salin file requirements terlebih dahulu untuk mengoptimalkan caching layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode project ke dalam container
COPY . .

# Expose port FastAPI
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]