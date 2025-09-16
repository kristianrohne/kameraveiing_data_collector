# Docker Setup Guide

This project is fully containerized using Docker and Docker Compose. Both the frontend (Angular) and backend (Flask) applications run in separate containers with proper networking and volume management.

## 🏗️ Architecture

- **Frontend Container**: Angular app built with Node.js and served by nginx
- **Backend Container**: Flask application with Python 3.11
- **Networking**: Custom Docker network for inter-service communication
- **Volumes**: Persistent storage for database and session data

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on your system

### Option 1: Using the management script (Recommended)
```bash
# Make the script executable
chmod +x start-docker.sh

# Start all services
./start-docker.sh start

# Check status
./start-docker.sh status

# View logs
./start-docker.sh logs

# Stop services
./start-docker.sh stop
```

### Option 2: Using Docker Compose directly
```bash
# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## 🔧 Available Commands

The `start-docker.sh` script provides these commands:

- `start|up` - Start all containers
- `stop|down` - Stop all containers  
- `restart` - Restart all containers
- `logs` - Show real-time container logs
- `status` - Show container status and test services
- `build` - Build Docker images
- `clean` - Stop containers and clean up resources

## 🌐 Service Access

Once running, the services are available at:

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API through Frontend**: http://localhost:4200/api/

## 📁 Container Details

### Backend Container
- **Base Image**: python:3.11-slim
- **Working Directory**: /app
- **Port**: 8000
- **Environment**: Production Flask settings
- **Volumes**: 
  - `./backend/data:/app/data` (Database storage)
  - `./backend/flask_session:/app/flask_session` (Session storage)

### Frontend Container
- **Build Stage**: node:18-alpine (for building Angular app)
- **Production Stage**: nginx:alpine (for serving static files)
- **Port**: 4200 (mapped to nginx port 80)
- **Features**: 
  - API proxy to backend
  - Angular routing support
  - Security headers

## 🔄 Development Workflow

### Making Changes

#### Backend Changes
1. Make your changes to the backend code
2. Rebuild the backend container:
   ```bash
   ./start-docker.sh stop
   docker compose build backend
   ./start-docker.sh start
   ```

#### Frontend Changes
1. Make your changes to the frontend code
2. Rebuild the frontend container:
   ```bash
   ./start-docker.sh stop
   docker compose build frontend
   ./start-docker.sh start
   ```

#### Full Rebuild
```bash
./start-docker.sh build
./start-docker.sh restart
```

### Debugging

#### View Logs
```bash
# All services
./start-docker.sh logs

# Specific service
docker compose logs backend
docker compose logs frontend
```

#### Access Container Shell
```bash
# Backend container
docker compose exec backend bash

# Frontend container (nginx)
docker compose exec frontend sh
```

#### Test Services
```bash
# Using the script
./start-docker.sh status

# Manual testing
curl http://localhost:8000/api/auth/me
curl http://localhost:4200/api/auth/me
```

## 🗄️ Database and Storage

- **Database**: SQLite stored in `./backend/data/app.db`
- **Uploads**: File uploads stored in `./backend/data/uploads/`
- **Sessions**: Flask sessions stored in `./backend/flask_session/`

All data persists between container restarts due to volume mounting.

## 🔒 Environment Variables

The following environment variables are configured in `docker-compose.yml`:

- `FLASK_ENV=production`
- `DATABASE_URL=sqlite:///data/app.db`
- `OAUTH_CLIENT_ID` (set to your Animalia client ID)
- `OAUTH_CLIENT_SECRET` (set to your Animalia client secret)

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Stop any existing containers
   ./start-docker.sh stop
   
   # Check what's using the ports
   sudo netstat -tlnp | grep :4200
   sudo netstat -tlnp | grep :8000
   ```

2. **Build Failures**
   ```bash
   # Clean build
   ./start-docker.sh clean
   ./start-docker.sh build
   ./start-docker.sh start
   ```

3. **Permission Issues**
   ```bash
   # Fix script permissions
   chmod +x start-docker.sh
   
   # Fix data directory permissions
   sudo chown -R $USER:$USER backend/data
   ```

4. **API Not Accessible**
   - Check if containers are running: `./start-docker.sh status`
   - Check nginx configuration in `frontend/nginx.conf`
   - Verify Docker network: `docker network ls`

### Health Checks

The management script includes automatic health checks. Run:
```bash
./start-docker.sh status
```

This will test:
- Backend API connectivity
- Frontend service availability  
- API proxy functionality

## 📝 Notes

- The frontend is built in production mode for optimal performance
- nginx serves static files and proxies API requests to the backend
- All containers restart automatically unless stopped manually
- Database and uploaded files persist between container restarts
- The setup supports both development and production environments