# Docker Setup for Kameraveiing Data Collector

This document explains how to run the pig weight data collection system using Docker.

## 🐳 Docker Architecture

The application consists of two main services:

- **Backend**: Flask API server with OAuth and file upload capabilities
- **Frontend**: Angular web application served through Nginx

## 🚀 Quick Start

### Using the Management Script (Recommended)
```bash
# Make script executable (first time only)
chmod +x docker.sh

# Start all services
./docker.sh start

# View service status
./docker.sh status

# Check health
./docker.sh health

# View logs
./docker.sh logs

# Stop services
./docker.sh stop
```

### Manual Docker Commands
```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up -d --build

# Stop services
docker compose down
```

## 📦 Services

### Backend (Flask)
- **Port**: 8000
- **Health Check**: http://localhost:8000/api/health
- **Features**:
  - Animalia SSO OAuth integration
  - File upload (50MB limit)
  - Persistent data storage via Docker volumes

### Frontend (Angular)
- **Port**: 4200 (production) / 4201 (development)
- **Features**:
  - Nginx reverse proxy for API calls
  - Gzip compression
  - Static asset caching
  - Angular routing support

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `backend/` directory:

```bash
# OAuth Configuration
ANIMALIA_CLIENT_ID=your_client_id
ANIMALIA_CLIENT_SECRET=your_client_secret
ANIMALIA_ENVIRONMENT=staging

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

### Volumes
- `backend_data`: Application data
- `backend_uploads`: Uploaded images
- `backend_s3`: S3 simulation directory
- `backend_sessions`: Flask session files

## 📝 Available Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Scale services (if needed)
docker-compose up --scale backend=2

# Development mode with hot reload
docker-compose --profile dev up
```

## 🔍 Troubleshooting

### Check Service Health
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost:4200

# Docker service status
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f backend
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v --remove-orphans

# Rebuild from scratch
docker-compose up --build --force-recreate
```

## 🌐 Access Points

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **Development Frontend**: http://localhost:4201 (dev profile)

## 🔒 Security Notes

- OAuth credentials are loaded from environment variables
- Volumes ensure data persistence
- Nginx serves static files securely
- Health checks monitor service availability

## 📁 File Structure

```
├── docker-compose.yml          # Main orchestration
├── backend/
│   ├── Dockerfile             # Production backend image
│   ├── .dockerignore          # Backend build exclusions
│   └── .env                   # Environment variables
├── frontend/
│   ├── Dockerfile             # Production frontend image
│   ├── Dockerfile.dev         # Development frontend image
│   ├── nginx.conf             # Nginx configuration
│   ├── proxy.conf.docker.json # Docker proxy config
│   └── .dockerignore          # Frontend build exclusions
```

## 🚀 Deployment

For production deployment:

1. Set `FLASK_ENV=production` in backend/.env
2. Use production OAuth credentials
3. Consider using external volumes for data persistence
4. Set up proper SSL/TLS certificates
5. Configure firewall rules appropriately