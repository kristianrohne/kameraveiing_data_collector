#!/bin/bash

# Kameraveiing Data Collector - Docker Management Script

echo "🐳 Kameraveiing Data Collector - Docker Management"
echo "=================================================="

case "$1" in
    start|up)
        echo "🚀 Starting Docker containers..."
        docker compose up -d
        echo "✅ Containers started!"
        echo "   Frontend: http://localhost:4200"
        echo "   Backend API: http://localhost:8000"
        ;;
    stop|down)
        echo "🛑 Stopping Docker containers..."
        docker compose down
        echo "✅ Containers stopped!"
        ;;
    restart)
        echo "� Restarting Docker containers..."
        docker compose down
        docker compose up -d
        echo "✅ Containers restarted!"
        echo "   Frontend: http://localhost:4200"
        echo "   Backend API: http://localhost:8000"
        ;;
    logs)
        echo "📋 Showing container logs..."
        docker compose logs -f
        ;;
    status)
        echo "📊 Container status:"
        docker compose ps
        echo ""
        echo "🔍 Testing services..."
        echo "Backend API test:"
        curl -s http://localhost:8000/api/auth/me || echo "❌ Backend not responding"
        echo ""
        echo "Frontend test:"
        curl -s -I http://localhost:4200 | head -1 || echo "❌ Frontend not responding"
        echo "Frontend API proxy test:"
        curl -s http://localhost:4200/api/auth/me || echo "❌ API proxy not working"
        ;;
    build)
        echo "🔨 Building Docker images..."
        docker compose build
        echo "✅ Build complete!"
        ;;
    clean)
        echo "🧹 Cleaning up Docker resources..."
        docker compose down
        docker compose down --volumes
        docker system prune -f
        echo "✅ Cleanup complete!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|build|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all containers"
        echo "  stop    - Stop all containers"
        echo "  restart - Restart all containers"
        echo "  logs    - Show container logs"
        echo "  status  - Show container status and test services"
        echo "  build   - Build Docker images"
        echo "  clean   - Stop containers and clean up resources"
        exit 1
        ;;
esac
