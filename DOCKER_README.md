# Kameraveiing Data Collector - Docker Setup# Docker Setup for Kameraveiing Data Collector



This project contains a pig weight data collection system with OAuth authentication.This document explains how to run the pig weight data collection system using Docker.



## Prerequisites## 🐳 Docker Architecture



- DockerThe application consists of two main services:

- Docker Compose

- **Backend**: Flask API server with OAuth and file upload capabilities

## Quick Start with Docker- **Frontend**: Angular web application served through Nginx



### 1. Clone and Navigate## 🚀 Quick Start

```bash

git clone <repository-url>### Using the Management Script (Recommended)

cd kameraveiing_data_collector```bash

```# Make script executable (first time only)

chmod +x docker.sh

### 2. Build and Run with Docker Compose

```bash# Start all services

# Build and start all services./docker.sh start

docker-compose up --build

# View service status

# Or run in background./docker.sh status

docker-compose up --build -d

```# Check health

./docker.sh health

### 3. Access the Application

- **Frontend**: http://localhost:4200# View logs

- **Backend API**: http://localhost:8000./docker.sh logs



### 4. Stop the Services# Stop services

```bash./docker.sh stop

# Stop all services```

docker-compose down

### Manual Docker Commands

# Stop and remove volumes (WARNING: This will delete database data)```bash

docker-compose down -v# Build and start all services

```docker compose up --build



## Services# Run in background

docker compose up -d --build

### Backend (Flask)

- **Port**: 8000# Stop services

- **Database**: SQLite (persistent volume)docker compose down

- **Features**: OAuth authentication, file uploads, REST API```



### Frontend (Angular)## 📦 Services

- **Port**: 4200 (mapped to nginx port 80 in container)

- **Features**: User interface, OAuth flow, image upload### Backend (Flask)

- **Port**: 8000

## Environment Variables- **Health Check**: http://localhost:8000/api/health

- **Features**:

The docker-compose.yml includes default environment variables. For production, you should:  - Animalia SSO OAuth integration

  - File upload (50MB limit)

1. Update the OAuth credentials:  - Persistent data storage via Docker volumes

   - `ANIMALIA_CLIENT_ID`

   - `ANIMALIA_CLIENT_SECRET`### Frontend (Angular)

- **Port**: 4200 (production) / 4201 (development)

2. Change security keys:- **Features**:

   - `JWT_SECRET`  - Nginx reverse proxy for API calls

   - `SECRET_KEY`  - Gzip compression

  - Static asset caching

3. Update URLs if deploying to different hosts:  - Angular routing support

   - `FRONTEND_URL`

   - `ANIMALIA_REDIRECT_URI`## 🔧 Configuration



## Development Mode### Environment Variables

Create a `.env` file in the `backend/` directory:

For development, you can still run the services locally:

```bash

### Backend# OAuth Configuration

```bashANIMALIA_CLIENT_ID=your_client_id

cd backendANIMALIA_CLIENT_SECRET=your_client_secret

python3 app.pyANIMALIA_ENVIRONMENT=staging

```

# Flask Configuration

### FrontendSECRET_KEY=your_secret_key

```bashFLASK_ENV=development

cd frontend```

ng serve --host 172.17.250.146 --port 4200 --proxy-config proxy.conf.json

```### Volumes

- `backend_data`: Application data

## Docker Commands- `backend_uploads`: Uploaded images

- `backend_s3`: S3 simulation directory

### Build specific service- `backend_sessions`: Flask session files

```bash

docker-compose build backend## 📝 Available Commands

docker-compose build frontend

``````bash

# Start all services

### View logsdocker-compose up

```bash

docker-compose logs backend# Start in background

docker-compose logs frontenddocker-compose up -d

docker-compose logs -f  # Follow logs

```# Stop all services

docker-compose down

### Access container shell

```bash# Stop and remove volumes

docker-compose exec backend bashdocker-compose down -v

docker-compose exec frontend sh

```# View logs

docker-compose logs -f

## Persistent Data

# Rebuild specific service

- Backend database: Stored in `backend_data` volumedocker-compose build backend

- Session data: Stored in `backend_sessions` volumedocker-compose build frontend



## Troubleshooting# Scale services (if needed)

docker-compose up --scale backend=2

1. **Port conflicts**: If ports 4200 or 8000 are in use, update the docker-compose.yml port mappings

2. **OAuth issues**: Ensure the redirect URI in your OAuth provider matches the configured URL# Development mode with hot reload

3. **Build issues**: Clear Docker cache with `docker system prune` and rebuilddocker-compose --profile dev up

```

## Production Deployment

## 🔍 Troubleshooting

For production deployment:

### Check Service Health

1. Update environment variables in docker-compose.yml```bash

2. Use proper secrets management instead of hardcoded values# Backend health

3. Configure proper networking and reverse proxycurl http://localhost:8000/api/health

4. Set up SSL/TLS certificates

5. Configure backup for persistent volumes# Frontend health
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