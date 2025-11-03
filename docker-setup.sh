#!/bin/bash

# Library Management System - Simple Docker Setup for Development
# Use this for quick development setup only

set -e

echo "🚀 Library Management System - Development Docker Setup"
echo "======================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up          Start development services"
    echo "  down        Stop all services"
    echo "  logs        Show logs"
    echo "  seed        Seed the database with sample data"
    echo "  clean       Stop services and remove volumes"
    echo "  shell       Open shell in API container"
    echo ""
}

# Parse command
case "${1:-up}" in
    "up")
        echo "🏗️  Starting development services..."
        docker-compose up -d
        echo ""
        echo "✅ Development services started!"
        echo ""
        echo "🌐 Access points:"
        echo "   • API Documentation: http://localhost:8000/docs"
        echo "   • API Health Check: http://localhost:8000/health"
        echo "   • Frontend: http://localhost:3000"
        echo ""
        echo "📚 To seed the database with sample data, run:"
        echo "   ./docker-setup.sh seed"
        ;;

    "down")
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Services stopped"
        ;;

    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;

    "seed")
        echo "🌱 Seeding database with sample data..."

        # Wait for API to be ready
        echo "⏳ Waiting for API to be ready..."
        timeout=30
        while [ $timeout -gt 0 ]; do
            if curl -f http://localhost:8000/health >/dev/null 2>&1; then
                break
            fi
            sleep 2
            timeout=$((timeout-2))
        done

        if [ $timeout -le 0 ]; then
            echo "❌ API did not start within 30 seconds"
            exit 1
        fi

        # Run seed script
        docker-compose exec api python seed_database.py
        echo "✅ Database seeded successfully!"
        echo ""
        echo "👤 Sample login credentials:"
        echo "   • Admin: admin@library.com / admin123"
        echo "   • Librarian: librarian@library.com / librarian123"
        echo "   • User: john@example.com / user123"
        ;;

    "clean")
        echo "🧹 Cleaning up..."
        docker-compose down -v
        echo "✅ Cleanup complete"
        ;;

    "shell")
        echo "🐚 Opening shell in API container..."
        docker-compose exec api /bin/bash
        ;;

    "help"|"-h"|"--help")
        show_usage
        ;;

    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac