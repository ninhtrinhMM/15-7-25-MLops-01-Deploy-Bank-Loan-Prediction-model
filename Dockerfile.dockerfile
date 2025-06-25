# Base image Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy files vào container
COPY requirements.txt .
COPY model_ml.joblib .
COPY ML-app.py .

# Cài đặt thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Expose port ứng dụng
EXPOSE 5000

# Chạy ứng dụng (FastAPI)
CMD ["python", "ML-app.py"]