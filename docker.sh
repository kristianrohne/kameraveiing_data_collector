#!/bin/bash

# Kameraveiing Docker Management Script

set -e

show_help() {
    echo "🐳 Kameraveiing Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start all services"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  build          Build all images"
    echo "  logs           Show logs from all services"
    echo "  logs-backend   Show backend logs"
    echo "  logs-frontend  Show frontend logs"
    echo "  status         Show service status"
    echo "  clean          Stop and remove all containers and volumes"
    echo "  shell-backend  Open shell in backend container"
    echo "  shell-frontend Open shell in frontend container"
    echo "  health         Check health of all services"
    echo ""
}

case "${1:-help}" in
    start)
        echo "🚀 Starting Kameraveiing services..."
        docker compose up -d --build
        echo "✅ Services started!"
        echo "   Frontend: http://localhost:4200"
        echo "   Backend:  http://localhost:8000"
        ;;
    
    stop)
        echo "🛑 Stopping services..."
        docker compose down
        echo "✅ Services stopped!"
        ;;
    
    restart)
        echo "🔄 Restarting services..."
        docker compose down
        docker compose up -d --build
        echo "✅ Services restarted!"
        ;;
    
    build)
        echo "🔨 Building images..."
        docker compose build
        echo "✅ Images built!"
        ;;
    
    logs)
        docker compose logs -f
        ;;
    
    logs-backend)
        docker compose logs -f backend
        ;;
    
    logs-frontend)
        docker compose logs -f frontend
        ;;
    
    status)
        echo "📊 Service Status:"
        docker compose ps
        ;;
    
    clean)
        echo "🧹 Cleaning up..."
        read -p "This will remove all containers and volumes. Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker compose down -v --remove-orphans
            docker system prune -f
            echo "✅ Cleanup complete!"
        else
            echo "❌ Cleanup cancelled."
        fi
        ;;
    
    shell-backend)
        docker compose exec backend bash
        ;;
    
    shell-frontend)
        docker compose exec frontend sh
        ;;
    
    health)
        echo "🏥 Health Check:"
        echo -n "Backend:  "
        if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
            echo "✅ Healthy"
        else
            echo "❌ Unhealthy"
        fi
        
        echo -n "Frontend: "
        if curl -sf http://localhost:4200 > /dev/null 2>&1; then
            echo "✅ Healthy"
        else
            echo "❌ Unhealthy"
        fi
        ;;
    
    help|*)
        show_help
        ;;
esac