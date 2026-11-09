# 1. Gunakan versi Python yang ringan (versi 3.11 aman untuk pydantic & SQLAlchemy Anda)
FROM python:3.11-slim

# 2. Tentukan folder kerja di dalam container Docker
WORKDIR /app

# 3. Salin file requirements terlebih dahulu agar proses build lebih cepat
COPY requirements.txt .

# 4. Instal library (termasuk psycopg binary untuk PostgreSQL)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "psycopg[binary]"

# 5. Salin semua file proyek Anda ke dalam container
COPY . .

# 6. Buka port aplikasi
EXPOSE 8000

# 7. Terapkan migrasi sebelum menerima request
CMD ["sh", "-c", "python -m alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]