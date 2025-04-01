# Multi-stage build for the complete OCR application

# Stage 1: Build frontend
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build backend
FROM python:3.9-slim as backend-builder
WORKDIR /app
COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ ./api/
COPY ocr-engine/ ./ocr-engine/

# Stage 3: Final image
FROM python:3.9-slim
WORKDIR /app

# Install dependencies
COPY --from=backend-builder /app/api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install additional OCR dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libpng-dev \
    libjpeg-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY --from=backend-builder /app/api ./api
COPY --from=backend-builder /app/ocr-engine ./ocr-engine

# Copy frontend build files
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create required directories
RUN mkdir -p /app/uploads /app/processed

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "api/app.py"]